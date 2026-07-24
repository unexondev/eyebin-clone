from pyrealsense2 import context, sensor, format, video_stream_profile
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
    For managing stereo module (depth sensors) and RGB camera components.
    """

    def __init__(self, context : context, options : EnvironmentOptions):
        self.ctx = context # RealSense context
        self.opts = options
        self.cp_stereo = None # Stereo module
        self.cp_rgb = None # RGB module


    @property
    def stereo(self):
        cp_stereo = self.cp_stereo
        if cp_stereo is None:
            raise RuntimeError("Stereo module (depth sensors) is not initialized.")
        return cp_stereo


    @property
    def rgb(self):
        cp_rgb = self.cp_rgb
        if cp_rgb is None:
            raise RuntimeError("RGB camera is not initialized.")
        return cp_rgb


    def init_components(self):

        ctx = self.ctx

        sensors = ctx.query_all_sensors()
        for sensor in sensors:

            if sensor.is_depth_sensor():
                # then we can take it as stereo module
                if self.cp_stereo is not None:
                    raise NotImplementedError("Selection from multiple depth sensors is not implemented for now.")

                self.cp_stereo = sensor

            elif sensor.is_color_sensor():
                if self.cp_rgb is not None:
                    raise NotImplementedError("Selection from multiple color sensors is not implemented for now.")

                self.cp_rgb = sensor

        if self.stereo is None or self.cp_rgb is None:
            raise RuntimeError("Missing component, both stereo module & RGB camera are required.")


    """
    Helper functions while interacting with components
    """
    @staticmethod
    def is_component_opened(component : sensor):
        return len(component.get_active_streams()) > 0

    @staticmethod
    def stream_profiles_supported(component : sensor, stream_profiles : set[StreamProfile]):

        for prf_check in stream_profiles:

            for prf in component.get_stream_profiles():

                if not prf.is_video_stream_profile():
                    continue

                vs_prf : video_stream_profile = prf.as_video_stream_profile()

                if (prf_check.width == vs_prf.width() 
                    and prf_check.height == vs_prf.height() 
                    and vs_prf.fps() == prf_check.frame_rate):
                    # same profile in supported profiles
                    break
            else:
                return False # one of the profiles is not supported

        return True

    @staticmethod
    def stop_component(component : sensor):
        """
        Stops the component. Returns `True` if component was running before it stopped, `False` otherwise.
        """
        try: 
            component.stop()
        except RuntimeError:
            return False
        return True