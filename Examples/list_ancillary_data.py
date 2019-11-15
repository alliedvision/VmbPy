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
from vimba import *

def print_usage():
    print('Usage: python list_ancillary_data.py <camera_id>\n');
    print('Parameters:   camera_id         ID of the camera to be used');


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args():
    args = sys.argv[1:]

    if len(args) != 1:
        abort(reason="Invalid number of parameters given!", error_code=2, usage=True)

    return args[0]


def main():
    camera_id = parse_args()

    with Vimba.get_instance() as vimba:
        try:
            cam = vimba.get_camera_by_id(camera_id)

        except VimbaCameraError:
            abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        with cam:
            # Enable ChunkMode (ChunkMode appends Ancillary Data to Frames)
            try:
                cam.get_feature_by_name('ChunkModeActive').set(True)

            except VimbaFeatureError:
                abort('Failed to enable ChunkMode on Camera \'{}\'. Abort.'.format(camera_id))

            # Capture single Frame and print all contained ancillary data
            frame = cam.get_frame()
            anc_data = frame.get_ancillary_data()
            if anc_data:
                with anc_data:
                    for feat in anc_data.get_all_features():
                        print('Feature Name   : '.format(feat.get_name()))
                        print('Display Name   : '.format(feat.get_display_name()))
                        print('Tooltip        : '.format(feat.get_tooltip()))
                        print('Description    : '.format(feat.get_description()))
                        print('SNFC Namespace : '.format(feat.get_snfc_namespace()))
                        print()

            else:
                abort('Frame {} does not contain AncillaryData. Abort'.format(frame.get_id()))


if __name__ == '__main__':
    main()
