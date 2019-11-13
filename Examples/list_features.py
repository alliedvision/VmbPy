"""BSD 2-Clause License

Copyright (c) 2019, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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
    with Vimba.get_instance() as vimba:
        print('Print system wide properties:')
        print('camera access mode: {}'.format(str(vimba.get_camera_access_mode())))

        print('Print system features:')
        for feat in vimba.get_all_features():
            print_feature(feat)

        print_camera(vimba.get_all_cameras())
        print_interface(vimba.get_all_interfaces())


if __name__ == '__main__':
    main()
