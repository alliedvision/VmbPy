# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import ctypes
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

def main():

    sys = System.get_instance()
    sys.enable_log(LOG_CONFIG_TRACE_CONSOLE_ONLY)

    with sys:
        for cam in sys.get_all_cameras():
            cam.set_access_mode(AccessMode.Lite)

            print(cam.get_permitted_access_modes())

            with cam:
                pass


if __name__ == '__main__':
    main()

