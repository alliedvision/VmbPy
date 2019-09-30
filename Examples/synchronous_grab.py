# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

#TODO: Store images

def main():
    with Vimba.get_instance() as vimba:

        # Get a few frames from all detected cameras
        for cam in vimba.get_all_cameras():
            with cam:
                # 1) Get single Frame
                frame = cam.get_frame()

                #2) Get a sequence of 5 Frames
                frame = [f for f in cam.get_frame_iter(5)]

                #3) Get 5 frames frame by frame
                for frame in cam.get_frame_iter(5):
                    pass

                #4) Get frames until a event occurred
                class Stop(Exception):
                    pass

                try:
                    for no, frame in enumerate(cam.get_frame_iter(None)):
                        if no == 9:
                            raise Stop()

                        else:
                            print('{}'.format(no))

                except Stop:
                    print('Stopped')


if __name__ == '__main__':
    main()

