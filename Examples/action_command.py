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

def abort(reason: str, return_code: int = 1):
    print(reason + '\n')
    print('Usage: python action_command.py <camera_id> <interface_id>\n');
    print('Parameters:   camera_id         ID of the camera to be used');
    print('              interface_id      ID of network interface to send out Action Command');
    print('                               \'ALL\' enables broadcast on all interfaces\n');
    sys.exit(return_code)


def parse_args():
    args = sys.argv[1:]

    if len(args) != 2:
        abort("Invalid number of parameters given!", 2)

    return (args[0], args[1])


def set_feature(entity, feature_name: str, feature_value):
    try:
        entity.get_feature_by_name(feature_name).set(feature_value)

    except VimbaFeatureError:
        abort('Could not set Feature \'{}\'. Abort.'.format(feature_name))


def run_command(entity, feature_name: str):
    try:
        entity.get_feature_by_name(feature_name).run()

    except VimbaFeatureError:
        abort('Failed to run Feature \'{}\'. Abort.'.format(feature_name))


def frame_handler(cam: Camera, frame: Frame):
    if frame.get_status() == FrameStatus.Complete:
        print('Frame(ID: {}) has been received.'.format(frame.get_id()), flush=True)

    cam.queue_frame(frame)


def main():
    camera_id, interface_id = parse_args()

    with Vimba.get_instance() as vimba:
        try:
            cam = vimba.get_camera_by_id(camera_id)

        except VimbaCameraError:
            abort('Failed to lookup Camera {}. Abort.'.format(camera_id))

        with cam:
            # Prepare Camera for Software Trigger
            device_key = 1
            group_key = 1
            group_mask = 1

            set_feature(cam, 'TriggerSelector', 'FrameStart')
            set_feature(cam, 'TriggerSource', 'Action0')
            set_feature(cam, 'TriggerMode', 'On')
            set_feature(cam, 'ActionDeviceKey', device_key)
            set_feature(cam, 'ActionGroupKey', group_key)
            set_feature(cam, 'ActionGroupMask', group_mask)

            # Enter Streaming mode and wait for user input.
            try:
                cam.start_streaming(frame_handler)

                promt = 'Press \'a\' to send action command. Press \'q\' to stop example.\nEnter:'
                while True:
                    ch = input(promt)

                    if ch == 'q':
                        break

                    elif ch == 'a':
                        set_feature(vimba, 'ActionDeviceKey', device_key)
                        set_feature(vimba, 'ActionGroupKey', group_key)
                        set_feature(vimba, 'ActionGroupMask', group_mask)
                        run_command(vimba, 'ActionCommand')

            finally:
                cam.stop_streaming()


if __name__ == '__main__':
    main()
