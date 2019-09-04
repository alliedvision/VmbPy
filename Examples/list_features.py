# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

def print_interface_features(interfaces):
    for inter in interfaces:
        print('Print features of Interface: {}'.format(inter))

        with inter:
            for feat in inter.get_all_features():
                print('    ', feat)

        print('\n')


def print_camera_features(cameras):
    for cam in cameras:
        print('Print features of Camera: {}'.format(cam))

        with cam:
            for feat in cam.get_all_features():
                print('    ', feat)

        print('\n')


def main():
    with System.get_instance() as sys:

        print('Print System features:')
        for feat in sys.get_all_features():
            print('    ', feat)

        print('\n')

        print_camera_features(sys.get_all_cameras())
        print_interface_features(sys.get_all_interfaces())


if __name__ == '__main__':
    main()
