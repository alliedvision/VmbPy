# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import time
from vimba import *


def frame_handler(cam: Camera, frame: Frame):
    log = Log.get_instance()
    log.info('{} acquired {}'.format(cam, frame))

    cam.queue_frame(frame)


def main():
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()

        # Use first detected camera
        if cams:
            with cams[0] as cam:
                # Enable Logging for capturing messages from the frame handler
                vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

                # Start Streaming, wait for five seconds, stop streaming
                cam.start_streaming(frame_handler)
                time.sleep(5)
                cam.stop_streaming()

                # Disable Logging
                vimba.disable_log()

        else:
            print('No Cameras detected')


if __name__ == '__main__':
    main()
