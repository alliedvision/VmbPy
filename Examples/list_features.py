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
import sys
from typing import Optional
from vimba import *


def print_preamble():
    print('///////////////////////////////////////')
    print('/// Vimba API List Features Example ///')
    print('///////////////////////////////////////\n')


def print_usage():
    print('Usage: python print_usage.py [CameraID]\n')
    print('Parameters:   CameraID    ID of the camera to use (using first camera if not specified)')


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    if argc > 1:
        abort(reason="Invalid number of parameters given!", error_code=2, usage=True)

    return None if argc == 0 else args[0]


def print_feature(feature):
    print('/// Feature name   : {}'.format(feature.get_name()))
    print('/// Display name   : {}'.format(feature.get_display_name()))
    print('/// Tooltip        : {}'.format(feature.get_tooltip()))
    print('/// Description    : {}'.format(feature.get_description()))
    print('/// SFNC Namespace : {}'.format(feature.get_sfnc_namespace()))
    print('/// Unit           : {}'.format(feature.get_unit()))

    try:
        value = feature.get()

    except AttributeError:
        value = None

    except VimbaFeatureError:
        value = None

    print('/// Value          : {}\n'.format(str(value)))


def main():
    print_preamble()
    cam_id = parse_args()

    with Vimba.get_instance() as vimba:

        # Determine Camera to use
        if cam_id:
            try:
                cam = vimba.get_camera_by_id(cam_id)

            except VimbaCameraError:
                abort('Unable to access Camera \'{}\'. Abort.'.format(cam_id))

        else:
            cams = vimba.get_all_cameras()
            if not cams:
                abort('No cameras connected. Abort.')

            cam = cams[0]

        # Print all Camera features
        with cam:
            print('Print all features of camera \'{}\''.format(cam.get_id()))
            for feature in cam.get_all_features():
                print_feature(feature)


if __name__ == '__main__':
    main()
