# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

def main():
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()

        # Use first detected camera.
        if cams:
            with cams[0] as cam:

                # Enable Logging for capturing prints
                vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)
                log = Log.get_instance()

                # Acquire 10 Frames synchronously.
                for frame in cam.get_frame_iter(10):
                    log.info('Got {}'.format(frame))

                vimba.disable_log()

if __name__ == '__main__':
    main()
