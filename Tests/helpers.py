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
import os
import unittest
import vimba


class VimbaTestCase(unittest.TestCase):
    """
    Class that represents a test case for VimbaPython.

    Adds the static functions `get_test_camera_id` and `set_test_camera_id` to simplify opening the
    appropriate device for testing.
    """
    test_cam_id = ''

    @classmethod
    def setUpClass(cls):
        if not VimbaTestCase.get_test_camera_id():
            # Try to read device id from environment variable. If it is not set test_cam_id will
            # still be an empty string
            VimbaTestCase.set_test_camera_id(os.getenv('VIMBAPYTHON_DEVICE_ID', ''))
        if not VimbaTestCase.get_test_camera_id():
            with vimba.Vimba.get_instance() as vmb:
                try:
                    VimbaTestCase.set_test_camera_id(vmb.get_all_cameras()[0].get_id())
                except IndexError:
                    # no cameras found by vimba. Leave test_cam_id empty. This will cause tests
                    # using a real camera to fail
                    VimbaTestCase.set_test_camera_id('<NO CAMERA FOUND>')

        print(f'Executing tests in class "{cls.__name__}" '
              f'with camera ID "{VimbaTestCase.get_test_camera_id()}"', flush=True)

    def assertNoRaise(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)

        except BaseException as e:
            self.fail('Function raised: {}'.format(e))

    @staticmethod
    def get_test_camera_id() -> str:
        return VimbaTestCase.test_cam_id

    @staticmethod
    def set_test_camera_id(test_cam_id):
        VimbaTestCase.test_cam_id = test_cam_id
