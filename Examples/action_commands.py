"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
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
from vmbpy import *


def print_preamble():
    print('/////////////////////////////////////')
    print('/// VmbPy Action Commands Example ///')
    print('/////////////////////////////////////\n')


def print_usage():
    print('Usage:')
    print('    python action_commands.py <camera_id>')
    print('    python action_commands.py [/h] [-h]')
    print()
    print('Parameters:')
    print('    camera_id      ID of the camera to be used')
    print()


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    cam_id = ""
    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)
        elif not cam_id:
            cam_id = arg

    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)

    return cam_id if cam_id else None


def get_input() -> str:
    prompt = 'Press \'a\' to send action command. Press \'q\' to stop example. Enter:'
    print(prompt, flush=True)
    return input()


def get_camera(camera_id: Optional[str]) -> Camera:
    with VmbSystem.get_instance() as vmb:
        if camera_id:
            try:
                return vmb.get_camera_by_id(camera_id)

            except VmbCameraError:
                abort('Failed to access camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vmb.get_all_cameras()
            if not cams:
                abort('No cameras accessible. Abort.')

            return cams[0]


def frame_handler(cam: Camera, stream: Stream, frame: Frame):
    if frame.get_status() == FrameStatus.Complete:
        print('Frame(ID: {}) has been received.'.format(frame.get_id()), flush=True)

    cam.queue_frame(frame)


def main():
    print_preamble()
    camera_id = parse_args()

    with VmbSystem.get_instance():
        cam = get_camera(camera_id)
        inter = cam.get_interface()

        with cam:
            # Prepare camera for ActionCommand - trigger
            device_key = 1
            group_key = 1
            group_mask = 1

            # Try to adjust GeV packet size. This feature is only available for GigE - cameras.
            try:
                stream = cam.get_streams()[0]
                stream.GVSPAdjustPacketSize.run()
                while not stream.GVSPAdjustPacketSize.is_done():
                    pass
            except (AttributeError, VmbFeatureError):
                pass

            try:
                cam.TriggerSelector.set('FrameStart')
                cam.TriggerSource.set('Action0')
                cam.TriggerMode.set('On')
                cam.ActionDeviceKey.set(device_key)
                cam.ActionGroupKey.set(group_key)
                cam.ActionGroupMask.set(group_mask)
            except (AttributeError, VmbFeatureError):
                abort('The selected camera does not seem to support action commands')

            # Enter streaming mode and wait for user input.
            try:
                cam.start_streaming(frame_handler)

                while True:
                    ch = get_input()

                    if ch == 'q':
                        break

                    elif ch == 'a':
                        inter.ActionDeviceKey.set(device_key)
                        inter.ActionGroupKey.set(group_key)
                        inter.ActionGroupMask.set(group_mask)
                        inter.ActionCommand.run()

            finally:
                cam.stop_streaming()


if __name__ == '__main__':
    main()
