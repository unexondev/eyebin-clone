from dataclasses import dataclass


@dataclass(frozen=True)
class StreamProfile:
    width : int
    height : int
    frame_rate : int