from dataclasses import dataclass

from pyrealsense2 import syncer, sensor

from .environment import Environment
from .core.stream_profile import StreamProfile


@dataclass
class StreamOptions:
    stream_profiles_stereo : set[StreamProfile]
    stream_profile_rgb : set[StreamProfile]


class Stream:
    """
    Defining how to capture data,
    
    Stream operations FIXME
    """

    def __init__(self, environment : Environment, options : StreamOptions):
        opts = self.opts = options
        env = self.env = environment

        # check if profiles passed in options are supported
        if not env.stream_profiles_supported(env.stereo, opts.stream_profiles_stereo):
            raise RuntimeError("A stream profile is not supported for stereo module.")

        if not env.stream_profiles_supported(env.rgb, [ opts.stream_profile_rgb ]):
            raise RuntimeError("Stream profile is not supported for RGB camera.")

        self.syncer : syncer = None


    def is_stereo_consumable(self):
        return self.opts.stream_profiles_stereo.issubset(self.env.stereo.get_active_streams())

    def is_rgb_consumable(self):
        return self.opts.stream_profile_rgb in self.env.rgb.get_active_streams()


    def start(self):
        # TODO CONTINUE FROM HERE
        # THINK ABOUT CONSUMING IDEA BETTER
        # DEPTH, COLOR, INFRARED (rs.stream.<here>)
        env = self.env
        stereo = env.stereo
        rgb = env.rgb

        prfs_stereo = self.opts.stream_profiles_stereo
        prf_rgb = self.opts.stream_profile_rgb

        if not self.is_stereo_consumable():
            if not env.is_component_opened(stereo): # a small overhead ?
                stereo.open(prfs_stereo)

        if not self.is_rgb_consumable():
            if not env.is_component_opened(rgb): # a small overhead ?
                rgb.open(prf_rgb)

        # initialize a syncer
        sync = syncer(
            queue_size=1 # 1 frame max to be buffered before processing is enough
            )

        # start streaming
        try:
            rgb.start(sync)
            stereo.start(sync)
        except RuntimeError:
            # that means components are already started
            pass

        self.syncer = sync


    def stop(self):

        env = self.env
        stereo = env.stereo
        rgb = env.rgb

        prfs_stereo = self.opts.stream_profiles_stereo
        prf_rgb = self.opts.stream_profile_rgb

        # check running stream profiles belong to this stream
        ss_stereo = stereo.get_active_streams()
        if ss_stereo

        ss_rgb = rgb.get_active_streams()