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
import warnings

import vmbpy


class VmbPyTestCase(unittest.TestCase):
    """
    Class that represents a test case for vmbpy.

    Adds the static functions `get_test_camera_id` and `set_test_camera_id` to simplify opening the
    appropriate device for testing.
    """
    # Initial guess for test cam id is reading appropriate environment variable. If the user
    # supplies a value after importing this helper class it will overwrite that initial guess. If
    # the environment variable is empty and the user does not supply a device ID before `setUpClass`
    # is called, this class will try to detect available cameras and choose the first one.
    test_cam_id = os.getenv('VMBPY_DEVICE_ID', '')

    @classmethod
    def setUpClass(cls):
        if not VmbPyTestCase.get_test_camera_id():
            with vmbpy.VmbSystem.get_instance() as vmb:
                try:
                    VmbPyTestCase.set_test_camera_id(vmb.get_all_cameras()[0].get_id())
                except IndexError:
                    # no cameras found by VmbC. Leave test_cam_id empty. This will cause tests
                    # using a real camera to fail
                    VmbPyTestCase.set_test_camera_id('<NO CAMERA FOUND>')

        print(f'Executing tests in class "{cls.__name__}" '
              f'with camera ID "{VmbPyTestCase.get_test_camera_id()}"', flush=True)

    def assertNoRaise(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)

        except BaseException as e:
            self.fail('Function raised: {}'.format(e))

    @staticmethod
    def get_test_camera_id() -> str:
        return VmbPyTestCase.test_cam_id

    @staticmethod
    def set_test_camera_id(test_cam_id):
        VmbPyTestCase.test_cam_id = test_cam_id


def calculate_acquisition_time(cam: vmbpy.Camera, num_frames: int) -> float:
    """
    Calculate how many seconds it takes to record `num_frames` from `cam` in current configuration.

    WARNING: The cams context must already be entered as this function tries to access camera
    features!
    """
    fps = cam.get_feature_by_name('AcquisitionFrameRate').get()
    return num_frames / fps


def reset_default_user_set(cam_id: str) -> None:
    try:
        with vmbpy.VmbSystem.get_instance() as vmb:
            cam = vmb.get_camera_by_id(cam_id)
            with cam:
                try:
                    cam.get_feature_by_name('UserSetDefault').set('Default')
                except vmbpy.VmbFeatureError:
                    try:
                        cam.get_feature_by_name('UserSetDefaultSelector').set('Default')
                    except vmbpy.VmbFeatureError:
                        warnings.warn('Failed to reset default user set')
    except vmbpy.VmbCameraError:
        warnings.warn('Camera could not be found to reset the default user set')


def load_default_user_set(cam_id: str) -> None:
    try:
        with vmbpy.VmbSystem.get_instance() as vmb:
            cam = vmb.get_camera_by_id(cam_id)
            with cam:
                try:
                    cam.get_feature_by_name('UserSetSelector').set('Default')
                    cam.get_feature_by_name('UserSetLoad').run()
                except vmbpy.VmbFeatureError:
                    warnings.warn('Failed to load default user set')
    except vmbpy.VmbCameraError:
        warnings.warn('Camera could not be found to load default user set')
