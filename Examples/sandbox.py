# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

@scoped_log_enable(LogLevel.Trace)
def main():
    # Perform logged full system discovery
    with System.get_instance() as sys:

        for cam in sys.get_all_cameras():
            with cam:
                pass

        for inter in sys.get_all_interfaces():
            with inter:
                pass


if __name__ == '__main__':
    main()

