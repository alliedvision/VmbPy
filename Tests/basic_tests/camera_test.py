"""BSD 2-Clause License

Copyright (c) 2026, Allied Vision Technologies GmbH
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
import os
import sys

from vmbpy import VmbCameraError
from vmbpy.c_binding import VmbCameraInfo
from vmbpy.camera import Camera
from vmbpy.frame import Frame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


def _dummy_frame_handler(cam, stream, frame):
    pass


class CameraNoStreamsTest(VmbPyTestCase):
    """Regression test for a Camera whose GenTL Transport Layer reports zero streams.

    `Camera._open()` fills `Camera.__streams` from `self.__info.streamCount`. If a given camera
    (e.g. a new/unsupported model, or one whose Transport Layer misreports its stream count)
    reports 0 streams, `Camera.__streams` stays empty for the lifetime of the `with` context.

    `Camera.is_streaming()` already anticipates this and guards the resulting `__streams[0]`
    access with `except IndexError: return False`. `start_streaming()`, `stop_streaming()` and
    `queue_frame()` did not have the same guard, so they instead raised a bare
    `IndexError: list index out of range` that gave no indication a Camera/stream problem
    caused it. This test constructs that zero-stream state without needing real hardware, by
    bypassing `Camera.__init__` (which requires a real `VmbCameraInfo`/`Interface` from
    discovery) and only setting the attributes these methods actually touch.

    `start_streaming()` cannot silently succeed without any stream to stream from, so it raises
    `VmbCameraError`. `stop_streaming()` and `queue_frame()` document that they return silently
    if streaming mode is not active, so - like `is_streaming()` - a missing stream is treated as
    "not streaming" rather than an error.
    """

    def setUp(self):
        self.cam = Camera.__new__(Camera)
        self.cam._Camera__streams = []
        # start_streaming()'s VmbCameraError message includes get_id(), which reads
        # __info.cameraIdString - give it a minimal real VmbCameraInfo rather than nothing.
        info = VmbCameraInfo()
        info.cameraIdString = b'DEV_TEST0000'
        self.cam._Camera__info = info
        # Satisfy the `RaiseIfOutsideContext` decorator without opening a real device.
        self.cam._context_entered = True

    def test_start_streaming_without_streams_raises_camera_error(self):
        with self.assertRaises(VmbCameraError):
            self.cam.start_streaming(handler=_dummy_frame_handler)

    def test_stop_streaming_without_streams_returns_silently(self):
        self.assertNoRaise(self.cam.stop_streaming)

    def test_queue_frame_without_streams_returns_silently(self):
        # RuntimeTypeCheckEnable on queue_frame() requires an actual Frame instance, but the
        # zero-stream guard is checked before the frame's contents are ever touched.
        dummy_frame = Frame.__new__(Frame)
        self.assertNoRaise(self.cam.queue_frame, dummy_frame)

    def test_is_streaming_without_streams_returns_false(self):
        # Already guarded before this fix, and the reference behavior stop_streaming/queue_frame
        # were brought in line with: a missing stream means "not streaming", not an error.
        self.assertFalse(self.cam.is_streaming())
