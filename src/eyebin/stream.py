from dataclasses import dataclass

from pyrealsense2 import syncer

from .environment import Environment
from.core.stream_profile import StreamProfile


@dataclass
class StreamOptions:

    queue_size_syncer : int = 1

    wait_data_timeout : int = 5000


class Stream:
    """
    Defining how to capture data,
    
    Stream operations FIXME
    """

    def __init__(self, environment : Environment, options : StreamOptions):
        self.opts = options
        self.env = environment
        self.syncer : syncer = syncer(
            options.queue_size_syncer
            )


    def start(self):
        env = self.env
        return env.start_all(self.syncer)
            

    def stop(self):
        env = self.env
        env.stop_all(self.syncer)


    def active(self, apply_all_streams=False):
        """
        Ensures stream is active.

        Args:
            apply_all_streams: If set to `True`, when one of the stream profiles are inactive, rest of the profiles will be stopped.
            
        Returns:
            `True` if *all* the streams are active, `False` otherwise.
        """
        env = self.env

        for prf in env.stream_profiles():

            if not env.is_streaming(prf):

                if apply_all_streams:
                    env.stop_all()

                return False

        return True


    def wait_for_data(self, stream_profile):

        print("gasfjhkasjkfh")

        sync = self.syncer

        breakpoint()

        success, fset = sync.try_wait_for_frames(
            self.opts.wait_data_timeout
            )

        if not success:
            print("returning", len(fset))
            return False # return false if not succeeded


        print("abc")
        # handle & return the data on success
        for frame in fset:
            print(frame)