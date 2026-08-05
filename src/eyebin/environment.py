from pyrealsense2 import context, option, syncer
from pyrealsense2 import sensor as rs_sensor
from pyrealsense2 import stream_profile as rs_stream_profile
from pyrealsense2 import video_stream_profile as rs_video_stream_profile
from dataclasses import dataclass

from .core.mixins.optimization import OptimizationMixin
from .core.stream_profile import StreamProfile


@dataclass
class EnvironmentOptions:

    optimized_startup : bool
    """
    If this option set to `True`, stereo module (depth sensors) is going to be heaten
    before running workers and so on.
    """

    asic_temp_range_stereo : tuple[float, float]
    """
    Optimal ASIC temperature range for depth sensors to establish accuracy and safety.
    On initialization step, depth sensors are going to be heaten before running workers
    until the given 'minimum' optimal temperature value is reached. On the other hand, if the
    temperature exceeds the given 'maximum' optimal temperature value, the pipeline will be suspended.
    """

    projector_temp_range_stereo : tuple[float, float]
    """
    Optimal project temperature range for depth sensors to establish accuracy and safety.
    On initialization step, depth sensors are going to be heaten before running workers
    until the given 'minimum' optimal temperature value is reached. On the other hand, if the
    temperature exceeds the given 'maximum' optimal temperature value, the pipeline will be suspended.
    """


class Environment(OptimizationMixin):
    """
    Manage all the devices required to receive data for given video stream profiles
    """

    @dataclass
    class SensorContext:
        sensor : rs_sensor
        profile : rs_stream_profile
        def __hash__(self):
            return hash((
                self.sensor, self.profile
            ))

    def __init__(self,
                 profile_to_sensor : dict[StreamProfile, SensorContext],
                 options : EnvironmentOptions
                 ):
        self.opts = options
        self._prf_to_sensor_ctx = profile_to_sensor # profile to sensor map


    @classmethod
    def create(cls, context : context, stream_profiles : set[StreamProfile], options : EnvironmentOptions):

        prf_to_sensor_ctx = {}

        # map profiles with sensors
        sensors = context.query_all_sensors()
        prfs_not_found = stream_profiles.copy()
        for sensor in sensors:

            rs_prfs_stream = sensor.get_stream_profiles()
            for rs_prf_stream in rs_prfs_stream:

                if not prfs_not_found: break

                for profile in prfs_not_found:

                    if not rs_prf_stream.is_video_stream_profile():
                        continue

                    rs_prf_stream : rs_video_stream_profile \
                        = rs_prf_stream.as_video_stream_profile()

                    if rs_prf_stream.stream_type() == profile.stream_type and \
                        rs_prf_stream.width() == profile.width and \
                        rs_prf_stream.height() == profile.height and \
                        rs_prf_stream.fps() == profile.fps:

                        prf_to_sensor_ctx[profile] = cls.SensorContext(sensor, rs_prf_stream)

                        prfs_not_found.remove(profile)

                        break

            else:
                continue

            break

        else:
            raise RuntimeError("Some of the stream profiles are not supported")

        return cls(
            profile_to_sensor=prf_to_sensor_ctx,
            options=options
            )


    @staticmethod
    def _is_sensor_opened(sensor : rs_sensor):
        return len(sensor.get_active_streams()) > 0


    @staticmethod
    def _is_sensor_started(sensor : rs_sensor):
        if not Environment._is_sensor_opened(sensor):
            return False
        try:
            sensor.start(lambda _ : None)
        except RuntimeError:
            # sensor is already started
            return True
        sensor.stop()
        return False


    def _get_rs_stream_profile(self, stream_profile : StreamProfile):
        return self._prf_to_sensor_ctx[stream_profile].profile


    """
    Helper functions while interacting with sensors
    """

    def get_sensor(self, stream_profile : StreamProfile):
        return self._prf_to_sensor_ctx[stream_profile].sensor


    def stream_profiles(self):
        for prf in self._prf_to_sensor_ctx.keys():
            prf : StreamProfile
            yield prf


    def sensors(self):
        for ctx_sensor in set(self._prf_to_sensor_ctx.values()):
            yield ctx_sensor.sensor


    def is_streaming(self, stream_profile : StreamProfile):
        sensor = self.get_sensor(stream_profile)
        return self._is_sensor_started(sensor)


    def check_health(self):

        for sensor in self.sensors():

            if not self._is_sensor_started(sensor):
                continue # sensor must be streaming to check its health

            if sensor.is_depth_sensor():
                """
                - Asic temperature
                - Projector temperature
                """
                opts_sensor = sensor.get_supported_options()
                if option.asic_temperature in opts_sensor:
                    asic_temp = sensor.get_option(option.asic_temperature)
                    asic_temp_max = self.opts.asic_temp_range_stereo[1]

                    if asic_temp > asic_temp_max:
                        return False

                if option.projector_temperature in opts_sensor:
                    projector_temp = sensor.get_option(option.projector_temperature)
                    projector_temp_max = self.opts.projector_temp_range_stereo[1]

                    if projector_temp > projector_temp_max:
                        return False

        # TODO add health checks for other type of sensors?

        return True
    

    def start_stream(self, stream_profile : StreamProfile, syncer : syncer = None):
        """
        Begins streaming by starting the sensor.
        Returns `True` if sensor is started successfully, `False` otherwise.
        """
        sensor = self.get_sensor(stream_profile)

        if self.opts.optimized_startup:
            self.apply_optimizations(sensor) # apply optimizations to the sensor

        # check if already opened
        if not self._is_sensor_opened(sensor):
            # try to open with given profile
            try:
                sensor.open(
                    self._get_rs_stream_profile(stream_profile)
                    )
            except RuntimeError:
                # couldn't open
                return False

        # check if already started
        if self._is_sensor_started(sensor):
            return True

        # try to start
        try:
            sensor.start(syncer)
        except RuntimeError:
            # couldn't start
            return False

        # started successfully
        return True
    
        
    def stop_stream(self, stream_profile : StreamProfile):
        """
        Ends the stream by stopping the sensor.

        Args:
            stream_profile: A `StreamProfile` instance indicating which sensor to be stopped.
        """
        sensor = self.get_sensor(stream_profile)
        try: 
            sensor.stop()
        except RuntimeError:
            pass


    def start_all(self, syncer : syncer = None):
        """
        Starts all the streams by starting related sensors.

        Args:
            syncer: A `pyrealsense2.syncer` instance to synchronize frames.

        Returns:
            `True` if all the streams have been started successfully, `False` otherwise.
        """
        for prf in self.stream_profiles():

            if not self.start_stream(prf, syncer):

                self.stop_all() # stop all if some of them couldn't be started

                return False

        # all streams have been started
        return True


    def stop_all(self):
        """
        Ends all the streams by stopping related sensors.
        """
        for sensor in self.sensors():
            try:
                sensor.stop()
            except RuntimeError:
                continue