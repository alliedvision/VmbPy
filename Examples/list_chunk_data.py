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
    print('/// VmbPy List Chunk Data Example ///')
    print('/////////////////////////////////////\n')


def print_usage():
    print('Usage:')
    print('    python list_chunk_data.py [camera_id]')
    print('    python list_chunk_data.py [/h] [-h]')
    print()
    print('Parameters:')
    print('    camera_id   ID of the camera to use (using first camera if not specified)')
    print()


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)

    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)

    return None if argc == 0 else args[0]


def get_camera(camera_id: Optional[str]) -> Camera:
    with VmbSystem.get_instance() as vmb:
        if camera_id:
            try:
                return vmb.get_camera_by_id(camera_id)

            except VmbCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vmb.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')

            return cams[0]


class ChunkExample:
    def __init__(self, cam: Camera) -> None:
        self.cam = cam
        self.enabled_chunk_selectors = []

    def run(self):
        with self.cam:
            self.setup_camera()
            print('Press <enter> to stop Frame acquisition.')
            try:
                self.cam.start_streaming(handler=self.frame_callback, buffer_count=10)
                input()
            finally:
                self.cam.stop_streaming()

    def setup_camera(self):
        with self.cam:
            # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
            try:
                stream = self.cam.get_streams()[0]
                stream.GVSPAdjustPacketSize.run()
                while not stream.GVSPAdjustPacketSize.is_done():
                    pass

            except (AttributeError, VmbFeatureError):
                pass

            try:
                # Turn on a selection of Chunk features
                self.cam.ChunkModeActive.set(False)
                for selector in ('Timestamp', 'Width', 'Height', 'ExposureTime'):
                    try:
                        self.cam.ChunkSelector.set(selector)
                        self.cam.ChunkEnable.set(True)
                        self.enabled_chunk_selectors.append(selector)
                    except VmbFeatureError:
                        print('The device does not support chunk feature "{}". It was not enabled.'
                              ''.format(selector))
                self.cam.ChunkModeActive.set(True)
            except (AttributeError, VmbFeatureError):
                abort('Failed to enable Chunk Mode for camera \'{}\'. Abort.'
                      ''.format(self.cam.get_id()))

    def frame_callback(self, cam: Camera, stream: Stream, frame: Frame):
        print('{} acquired {}'.format(cam, frame), flush=True)
        if frame.contains_chunk_data():
            frame.access_chunk_data(self.chunk_callback)
        else:
            print('No Chunk Data present', flush=True)
        cam.queue_frame(frame)

    def chunk_callback(self, features: FeatureContainer):
        # Print information provided by chunk features that were enabled for this example. More
        # features are available (e.g. via features.get_all_features())
        if self.enabled_chunk_selectors:
            msg = 'Chunk Data:'
            for selector in self.enabled_chunk_selectors:
                chunk_feature_name = 'Chunk' + selector
                # Access to chunk data is only possible via the passed FeatureContainer instance
                chunk_feature = features.get_feature_by_name(chunk_feature_name)
                msg += ' {}={}'.format(chunk_feature_name, chunk_feature.get())
        else:
            msg = 'No chunk selectors were enabled. No chunk data to show.'
        print(msg, flush=True)


def main():
    print_preamble()
    cam_id = parse_args()

    with VmbSystem.get_instance():
        cam = get_camera(cam_id)
        chunk_example = ChunkExample(cam)
        chunk_example.run()


if __name__ == '__main__':
    main()
