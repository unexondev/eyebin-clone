from pyrealsense2 import context
from dataclasses import dataclass

from .mixins.optimization import OptimizationMixin

@dataclass
class StreamProfile:
    width : int
    height : int
    frame_rate : int

@dataclass
class EnvironmentOptions:

    stream_profile_stereo : StreamProfile = StreamProfile(
        width=1280, height=720,
        frame_rate=6 # lower frame rates are recommended
    )

    stream_profile_rgb : StreamProfile = StreamProfile(
        width=1920, height=1080,
        frame_rate=6 # lower frame rates are recommended
    )

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

    OPTS_DEFAULT = EnvironmentOptions(
        asic_temp_range_stereo=(30.0, 45.0), # FIXME
        projector_temp_range_stereo=(30.0, 45.0) # FIXME
    )

    def __init__(self, context : context, options : EnvironmentOptions = OPTS_DEFAULT):
        self.ctx = context # RealSense context
        self.opts = options
        self.m_stereo = None # Stereo module
        self.m_rgb = None # RGB module


    def init_components(self):

        ctx = self.ctx

        sensors = ctx.query_all_sensors()
        for sensor in sensors:

            if sensor.is_depth_sensor():
                # then we can take it as stereo module
                if self.m_stereo is not None:
                    raise NotImplementedError("Selection from multiple depth sensors is not implemented for now.")

                self.m_stereo = sensor

            elif sensor.is_color_sensor():
                if self.m_rgb is not None:
                    raise NotImplementedError("Selection from multiple color sensors is not implemented for now.")

                self.m_rgb = sensor


    def all_components_found(self):
        return (self.m_stereo is not None
                and self.m_rgb is not None)


    def start_component_pipelines(self):
        # TODO
        pass


    @property
    def stereo(self):
        m_stereo = self.m_stereo
        if m_stereo is None:
            raise RuntimeError("Stereo module (depth sensors) is not found.")
        return self.m_stereo


    @property
    def rgb(self):
        m_rgb = self.m_rgb
        if m_rgb is None:
            raise RuntimeError("RGB camera is not found.")