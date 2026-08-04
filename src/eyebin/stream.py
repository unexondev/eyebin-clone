from dataclasses import dataclass

from pyrealsense2 import syncer, sensor

from .environment import Environment


@dataclass
class StreamOptions:
    pass


class Stream:
    """
    Defining how to capture data,
    
    Stream operations FIXME
    """

    def __init__(self, environment : Environment, options : StreamOptions):
        self.opts = options
        self.env = environment
        self.syncer : syncer = None


    def is_stereo_consumable(self):
        return self.opts.stream_profiles_stereo.issubset(self.env.stereo.get_active_streams())


    def is_rgb_consumable(self):
        return self.opts.stream_profile_rgb in self.env.rgb.get_active_streams()


    def start(self):
        env = self.env
        for prf in env.stream_profiles():
            env.start_stream(prf)
            

    def stop(self):
        pass


    @property
    def on(self):
        env = self.env
        for sensor in env.sensors():
            if not env.is_sensor_streaming(sensor):
                return False
        return True