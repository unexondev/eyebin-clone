from pyrealsense2 import context, option


class OptimizationMixin:

    def optimize_low_stereo_temperature(self):

        self.ctx : context

        asic_temp_min = self.opts.asic_temp_range_ds[0]
        projector_temp_min = self.opts.projector_temp_range_ds[0]

        ss_queue = [ sensor for sensor in self.ctx.query_all_sensors() if sensor.is_depth_sensor() ]

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

                opt_asic_temp = option.asic_temperature
                opt_project_temp = option.projector_temperature

                opts_valid = sensor.get_supported_options()

                asic_temp = None
                project_temp = None

                if opt_asic_temp in opts_valid:
                    asic_temp = sensor.get_option(opt_asic_temp)
                if opt_project_temp in opts_valid:
                    project_temp = sensor.get_option(opt_project_temp)

                asic_temp_ok = asic_temp is None or asic_temp >= asic_temp_min
                project_temp_ok = project_temp is None or project_temp >= projector_temp_min
            
                if asic_temp_ok and project_temp_ok:
                    sensor.stop() # stop stressing
                    sensor.close() # turn off the sensor
                    ss_queue.remove(sensor) # remove the sensor from queue