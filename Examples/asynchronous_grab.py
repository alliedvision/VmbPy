# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

def frame_handler(cam: Camera, frame: Frame):
    log = Log.get_instance()
    log.info('{} acquired {}'.format(cam, frame))

    cam.requeue_frame(frame)


def main():
    with Vimba.get_instance() as vimba:
        # Lookup first detected camera.
        cams = vimba.get_all_cameras()
        if cams:
            # Enter Camera context
            with cams[0] as cam:

                # Enable Logging for capturing messages from the frame handler
                vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

                # Start Streaming, wait for five seconds, stop streaming
                cam.start_streaming(frame_handler, 5)
                time.sleep(5)
                cam.stop_streaming()

                # Disable Logging
                vimba.disable_log()


if __name__ == '__main__':
    main()
