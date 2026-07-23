import pyrealsense2 as rs
import curses


ASIC_TEMP_RECOMMENDED = 30.0 # FIXME SWAG
PROJECT_TEMP_RECOMMENDED = 30.0 # FIXME SWAG


def any_device_connected(ctx : rs.context):
    return len(ctx.query_devices()) > 0

def prepare_depth_sensors(ctx : rs.context):

    ss_queue = [ sensor for sensor in ctx.query_all_sensors() if sensor.is_depth_sensor() ]

    if not ss_queue:
        # no sensors detected
        raise RuntimeError("No sensors detected, please ensure that the device is connected.")

    for sensor in ss_queue:

        prf_max_fps = None
        for prf in sensor.get_stream_profiles():
            if prf_max_fps is None or prf.fps() > prf_max_fps.fps():
                prf_max_fps = prf

        sensor.open(prf_max_fps) # turn on the sensor
        sensor.start(lambda _ : None) # start stressing

    while len(ss_queue) > 0:

        for sensor in ss_queue.copy():

            opt_asic_temp = rs.option.asic_temperature
            opt_project_temp = rs.option.projector_temperature

            opts_valid = sensor.get_supported_options()

            asic_temp = None
            project_temp = None

            if opt_asic_temp in opts_valid:
                asic_temp = sensor.get_option(opt_asic_temp)
            if opt_project_temp in opts_valid:
                project_temp = sensor.get_option(opt_project_temp)

            asic_temp_ok = asic_temp is None or asic_temp >= ASIC_TEMP_RECOMMENDED
            project_temp_ok = project_temp is None or project_temp >= PROJECT_TEMP_RECOMMENDED
        
            if asic_temp_ok and project_temp_ok:
                sensor.stop() # stop stressing
                sensor.close() # turn off the sensor
                ss_queue.remove(sensor) # remove the sensor from queue

    print("done")

    return
            

ctx = rs.context()

prepare_depth_sensors(ctx) # prepare the sensors

pipeline = rs.pipeline()

config = rs.config() # https://github.com/realsenseai/librealsense/blob/7c3ee3fb7c640e9f315e663907208cb56c4febfd/src/pipeline/config.h#L18
config.enable_stream(
    stream_type=rs.stream.depth,
    width=640, height=480,
    format=rs.format.z16,
    framerate=30)

pipeline.start(config)

def main(stdscr : curses.window):
    while True:

        frames = pipeline.wait_for_frames(
            timeout_ms=5000
            ) # 5 seconds for timeout

        depth = frames.get_depth_frame()

        h_csl, w_csl = stdscr.getmaxyx()
        w_depth, h_depth = depth.width, depth.height

        stdscr.clear() # clear screen

        CELL_WIDTH = 6
        for y_csl in range(h_csl):
            for x_csl in range(w_csl // CELL_WIDTH):

                x_depth = int(x_csl * w_depth / w_csl)
                y_depth = int(y_csl * h_depth / h_csl)

                distance = depth.get_distance(x_depth, y_depth)

                stdscr.addstr(
                    y_csl,
                    x_csl * CELL_WIDTH,
                    f"{distance:5.2f}"
                )

        stdscr.refresh() # refresh console so changes will be applied

        import time
        time.sleep(0.1)

curses.wrapper(main)