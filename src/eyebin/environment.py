from pyrealsense2 import context, sensor, video_stream_profile, option
from dataclasses import dataclass

from .core.mixins.optimization import OptimizationMixin
from .core.stream_profile import StreamProfile


@dataclass
class EnvironmentOptions:

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

    def __init__(self,
                 profile_to_sensor : dict[StreamProfile, sensor],
                 options : EnvironmentOptions
                 ):
        self.opts = options
        self._prf_to_sensor = profile_to_sensor # profile to sensor map


    @classmethod
    def create(cls, context : context, stream_profiles : set[StreamProfile], options : EnvironmentOptions):

        prf_to_sensor = {}

        # map profiles with sensors
        sensors = context.query_all_sensors()
        prfs_not_found = stream_profiles.copy()
        for sensor in sensors:

            stream_prfs_sensor = sensor.get_stream_profiles()
            for profile_sensor in stream_prfs_sensor:

                if not prfs_not_found: break

                for profile in prfs_not_found:

                    if not profile_sensor.is_video_stream_profile():
                        continue

                    profile_sensor : video_stream_profile \
                        = profile_sensor.as_video_stream_profile()

                    if profile_sensor.stream_type() == profile.stream_type and \
                        profile_sensor.width() == profile.width and \
                        profile_sensor.height() == profile.height and \
                        profile_sensor.fps() == profile.fps:

                        prf_to_sensor[profile] = sensor

                        prfs_not_found.remove(profile)

                        break

            else:
                continue

            break

        else:
            raise RuntimeError("Some of the stream profiles are not supported")

        return cls(
            profile_to_sensor=prf_to_sensor,
            options=options
            )


    def check_health(self):

        for sensor in self.sensors():

            if not self.is_sensor_streaming(sensor):
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


    def stream_profiles(self):
        for prf in self._prf_to_sensor.keys():
            prf : StreamProfile
            yield prf


    def sensors(self):
        for _sensor in set(self._prf_to_sensor.values()):
            _sensor : sensor
            yield _sensor


    def get_sensor(self, stream_profile : StreamProfile) -> sensor:
        return self._prf_to_sensor[stream_profile]


    """
    Helper functions while interacting with sensors
    """
    @staticmethod
    def is_sensor_opened(sensor : sensor):
        return len(sensor.get_active_streams()) > 0


    @staticmethod
    def is_sensor_streaming(sensor : sensor):
        if not Environment.is_sensor_opened(sensor):
            return False
        try:
            sensor.start()
        except RuntimeError:
            # sensor is already started
            return True
        sensor.stop()
        return False
    
        
    @staticmethod
    def stop_sensor(sensor : sensor):
        """
        Stops the sensor. Returns `True` if sensor was running before it stopped, `False` otherwise.
        """
        try: 
            sensor.stop()
        except RuntimeError:
            return False
        return True