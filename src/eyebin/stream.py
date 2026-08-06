from pyrealsense2 import syncer, frame

from .environment import Environment
from .core.stream_profile import StreamProfile

from dataclasses import dataclass
from collections import deque

import threading

import logging

logger = logging.getLogger(__name__)


@dataclass
class StreamOptions:

    queue_size_syncer : int = 1
    """
    For scalibility we keep the captured RGB/depth data inside a buffer, then process them.
    Since this buffer may cause a memory overhead, we allow you to set its maximum size.
    If maximum length is exceeded, capturing process will be suspended until any of older data is dequeued.
    """

    cascade_stop : int = True
    """
    If set to `True`, when one of the stream profiles is stopped, the rest of the stream profiles will also be stopped.
    """

    max_buffer_length : int = 1
    """
    For scalibility we keep the captured RGB/depth data inside a buffer, then process them.
    Since this buffer may cause a memory overhead, we allow you to set its maximum size.
    If maximum length is exceeded, capturing process will be suspended until any of older data is dequeued.
    """

    wait_data_timeout : int = 5000


class Stream:
    """
    Defining how to capture data,
    
    Stream operations FIXME
    """

    def __init__(self, syncer : syncer, environment : Environment, options : StreamOptions):
        self.syncer = syncer
        self.env = environment
        self.opts = options
        self._t_prod_data = threading.Thread(target=self.stream_data_producer)
        self._q_buffer = deque(maxlen=options.max_buffer_length)
        logger.debug("Initialized Stream instance %X with syncer %X." % (id(self), id(self.syncer)))


    @classmethod
    def create(cls, environment : Environment, options : StreamOptions):
        sync = syncer(
            options.queue_size_syncer
            )
        return cls(sync, environment, options)


    def stream_data_producer(self): # FIXME better name
        queue = self._q_buffer

        while self.active():

            prf_frame_map = {}

            succ, fset = self.syncer.try_wait_for_frames(self.opts.wait_data_timeout)

            if not succ:
                continue

            if len(fset) != len(list(self.env.stream_profiles())):
                # not enough frame, skip this one
                continue

            for frame in fset:
                for prf in self.env.stream_profiles():
                    if prf.stream_type != frame.profile.stream_type():
                        continue
                    prf_frame_map[prf] = frame

            queue.append(prf_frame_map)


    def get_data(self) -> dict[StreamProfile, frame]:
        try:
            return self._q_buffer.pop()
        except IndexError:
            return None
        

    def start(self):
        env = self.env
        logger.debug("Stream instance %X is beginning streaming with syncer %X..." % (id(self), id(self.syncer)))

        succ = env.start_all(self.syncer)

        if not succ:
            return False

        self._t_prod_data.start() # start stream data producer thread

        return True
    

    def stop(self):
        env = self.env
        env.stop_all(self.syncer)


    def active(self):
        """
        Ensures stream is active.

        Returns:
            `True` if *all* the streams are active, `False` otherwise.
        """
        env = self.env

        for prf in env.stream_profiles():

            if not env.is_streaming(prf):

                if self.opts.cascade_stop:
                    env.stop_all()

                return False
            
        return True
