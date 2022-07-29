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
import threading

from vmbpy import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class ChunkAccessTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        try:
            self.cam._open()
            self.local_device = self.cam.get_local_device()
        except VmbCameraError as e:
            self.cam._close()
            raise Exception ('Failed to open Camera {}.'.format(self.cam)) from e

        try:
            self.chunk_mode = self.cam.get_feature_by_name('ChunkModeActive')

        except VmbFeatureError:
            self.cam._close()
            self.vimba._shutdown()
            self.skipTest('Required Feature \'ChunkModeActive\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_chunk_callback_is_executed(self):
        # Expectation: The chunk callback is executed for every call to `Frame.access_chunk_data`
        class FrameHandler:
            def __init__(self) -> None:
                self.frame_callbacks_executed = 0
                self.chunk_callbacks_executed = 0
                self.is_done = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                self.frame_callbacks_executed += 1
                frame.access_chunk_data(self.chunk_callback)
                stream.queue_frame(frame)

                if self.frame_callbacks_executed >= 5:
                    self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                self.chunk_callbacks_executed += 1

        self.chunk_mode.set(True)
        handler = FrameHandler()
        try:
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=5),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertEquals(handler.frame_callbacks_executed,
                          handler.chunk_callbacks_executed,
                          f'Number of executed frame callbacks '
                          f'({handler.frame_callbacks_executed}) does not equal number of '
                          f'executed chunk callbacks ({handler.chunk_callbacks_executed})')

    def test_error_raised_if_chunk_is_not_active(self):
        # Expectation: If the frame does not contain chunk data `VmbFrameError` is raised upon
        # calling `Frame.access_chunk_data`
        class FrameHandler:
            def __init__(self, test_instance: VmbPyTestCase) -> None:
                self.expected_exception_raised = False
                self.is_done = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                try:
                    frame.access_chunk_data(self.chunk_callback)
                except VmbFrameError:
                    self.expected_exception_raised = True
                finally:
                    self.is_done.set()
                self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                # Will never be called because the C-API raises an error before we get this far
                pass

        self.chunk_mode.set(False)
        handler = FrameHandler(self)
        try:
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=5),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertTrue(handler.expected_exception_raised,
                        'The expected Exception type was not raised by `access_chunk_data`')
