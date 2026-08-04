from eyebin import create_context
from eyebin import Environment, EnvironmentOptions
from eyebin import Stream, StreamOptions
from eyebin import VideoStreamProfile, StreamType, StreamFormat

# get the context first
context = create_context()

# create stream profiles
sp_depth = VideoStreamProfile(StreamType.depth, StreamFormat.z16, 1920, 1080, 30)
sp_color = VideoStreamProfile(StreamType.color, StreamFormat.rgb8, 1920, 1080, 30)

# set enviornment options
opts_env = EnvironmentOptions(
    asic_temp_range_stereo=(30.0, 40.0),
    projector_temp_range_stereo=(30.0, 40.0)
)

# create environment for the stream profiles requested
env = Environment.create(context, { sp_depth, sp_color }, opts_env)

# set stream options
opts_stream = StreamOptions()

# create stream
stream = Stream(env, opts_stream)

# start the stream
stream.start()

while stream.on:
    pass