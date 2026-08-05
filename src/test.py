from eyebin import create_context
from eyebin import Environment, EnvironmentOptions
from eyebin import Stream, StreamOptions
from eyebin import VideoStreamProfile, StreamType, StreamFormat

# get the context first
context = create_context()

# create stream profiles
sp_depth = VideoStreamProfile(StreamType.depth, StreamFormat.z16, 1280, 720, 6)
sp_color = VideoStreamProfile(StreamType.color, StreamFormat.rgb8, 1280, 720, 6)

# set enviornment options
opts_env = EnvironmentOptions(
    optimized_startup=True,
    asic_temp_range_stereo=(30.0, 40.0),
    projector_temp_range_stereo=(27.0, 40.0)
)

# create environment for the stream profiles requested
env = Environment.create(context, { sp_depth, sp_color }, opts_env)

# set stream options
opts_stream = StreamOptions()

# create stream
stream = Stream(env, opts_stream)

# start the stream
started = stream.start()

if not started:
    raise RuntimeError("Couldn't start stream!")

while stream.active(apply_all_streams=True):

    stream.wait_for_data(sp_depth)