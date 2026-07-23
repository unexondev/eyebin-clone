from dataclasses import dataclass
from .core.environment import Environment, EnvironmentOptions
import pyrealsense2 as rs


@dataclass
class PipelineOptions:

    optimized_startup : bool
    """
    If this option set to `True`, stereo module (depth sensors) is going to be heaten
    before running workers and so on.
    """

    max_len_captured_data_buffer : int
    """
    For scalibility we keep the captured RGB/depth data inside a buffer, then process them.
    Since this buffer may cause a memory overhead, we allow you to set its maximum size.
    If maximum length is exceeded, capturing process will be suspended until any of older data is dequeued.
    """

    environment_options : EnvironmentOptions = Environment.OPTS_DEFAULT

        
class Pipeline:
    """
    The main pipeline for EyeBin project that organizes tasks.
    """

    OPTS_DEFAULT = PipelineOptions(
        optimized_startup=True,
        max_len_captured_data_buffer=32
    )

    def __init__(self, options : PipelineOptions = OPTS_DEFAULT):
        self.opts = options
        self.ctx : rs.context = None # must be dynamic, may vary on different start calls ?
        self.env : Environment = None # same as this one

    def start_component_pipelines(self):
        """
        Starts RealSense's camera pipelines.
        """
        env = self.env

        if self.opts.optimized_startup:
            env.optimize_low_stereo_temperature() # heat sensors before proceeding

        env.start_component_pipelines()

        # TODO


    def capture(self):
        raise NotImplementedError()

    def all_components_healthy(self):
        """
        TODO: Camera must be 'started' if the temperatures to be checked
        """

        raise NotImplementedError()

    def start(self):
        """
        Starts the pipeline.
        """
        ctx = self.ctx = rs.context() # initialize the context

        env = self.env = Environment(
            ctx,
            self.opts.environment_options
            )
        
        env.init_components() # initialize the environment

        if not env.all_components_found():
            pass

        self.start_component_pipelines()

        while self.all_components_healthy():
            pass

        # TODO