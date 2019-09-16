# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

def print_feature(feature):
    print('    name: {}'.format(feature.get_name()))
    print('    type: {}'.format(feature.get_type()))
    print('    flags: {}'.format(feature.get_flags()))
    print('    category: {}'.format(feature.get_category()))
    print('    display_name: {}'.format(feature.get_display_name()))
    print('    polling_time: {}'.format(feature.get_polling_time()))
    print('    unit: {}'.format(feature.get_unit()))
    print('    representation: {}'.format(feature.get_representation()))
    print('    visibility: {}'.format(str(feature.get_visibility())))
    print('    tooltip: {}'.format(feature.get_tooltip()))
    print('    description: {}'.format(feature.get_description()))
    print('    sfnc namespace: {}'.format(feature.get_sfnc_namespace()))
    print('    streamable: {}'.format(feature.is_streamable()))
    print('    has affected: {}'.format(feature.has_affected_features()))
    print('    has selected: {}'.format(feature.has_selected_features()))
    print('\n')


def print_interface(interfaces):
    for inter in interfaces:
        print('Print interface properties:')
        print('id: {}'.format(inter.get_id()))
        print('type: {}'.format(str(inter.get_type())))
        print('name: {}'.format(inter.get_name()))
        print('serial: {}'.format(inter.get_serial()))
        print('permitted access mode: {}'.format(inter.get_permitted_access_mode()))

        print('Interface features:')
        with inter:
            for feat in inter.get_all_features():
                print_feature(feat)


def print_camera(cameras):
    for cam in cameras:
        print('Print camera properties:')
        print('id: {}'.format(cam.get_id()))
        print('name: {}'.format(cam.get_name()))
        print('model: {}'.format(cam.get_model()))
        print('serial: {}'.format(cam.get_serial()))
        print('permitted access modes: {}'.format(cam.get_permitted_access_modes()))
        print('interface id: {}'.format(cam.get_interface_id()))
        print('access mode: {}'.format(str(cam.get_access_mode())))

        print('Camera features:')
        with cam:
            for feat in cam.get_all_features():
                print_feature(feat)


def main():
    System.get_instance().enable_log(LOG_CONFIG_TRACE_CONSOLE_ONLY)
    with System.get_instance() as sys:
        print('Print system wide properties:')
        print('camera access mode: {}'.format(str(sys.get_camera_access_mode())))
        print('network discovery: {}'.format(sys.get_network_discovery()))

        print('Print system features:')
        for feat in sys.get_all_features():
            print_feature(feat)

        print_camera(sys.get_all_cameras())
        print_interface(sys.get_all_interfaces())


if __name__ == '__main__':
    main()
