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
        with vmbpy.VmbSystem.get_instance() as vmb:
            if not VmbPyTestCase.get_test_camera_id():
                try:
                    VmbPyTestCase.set_test_camera_id(vmb.get_all_cameras()[0].get_id())
                except IndexError:
                    # no cameras found by VmbC. Leave test_cam_id empty. This will cause tests
                    # using a real camera to fail
                    VmbPyTestCase.set_test_camera_id('<NO CAMERA FOUND>')

            try:
                # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
                cam = vmb.get_camera_by_id(VmbPyTestCase.get_test_camera_id())
                with cam:
                    try:
                        stream = cam.get_streams()[0]
                        stream.GVSPAdjustPacketSize.run()

                        while not stream.GVSPAdjustPacketSize.is_done():
                            pass

                    except (AttributeError, vmbpy.VmbFeatureError):
                        pass

            except vmbpy.VmbCameraError:
                pass

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
    if fps > 0:
        return num_frames / fps
    warnings.warn("Failed to get feature 'AcquisitionFrameRate'")
    return num_frames * 2.0  # set timeout to 2s. per frame


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


def _clamp(n, smallest, largest):
    return max(smallest, min(largest, n))


def set_throughput_to_fraction(cam: vmbpy.Camera, fraction: float = 0.75):
    """
    Set the DeviceLinkThroughputLimit feature of `cam` to `fraction * max_limit`.

    Note:
        The value that is actually set on the feature is clamped to the (nim, max) interval. This
        means that if the fraction is set to 0.0, the value will be set to min. If the fraction is
        set to 1.1, the value will be set to max.
    """

    try:
        (min_limit, max_limit) = cam.DeviceLinkThroughputLimit.get_range()
        new_value = _clamp(fraction*max_limit, min_limit, max_limit)
        cam.DeviceLinkThroughputLimit.set(new_value)
    except AttributeError as e:
        warnings.warn(f'Camera does not have feature DeviceLinkThroughputLimit: {e}')
    except Exception as e:
        warnings.warn(f'Could not set DeviceLinkThroughputLimit to {new_value}: {e}')


def reset_roi(cam: vmbpy.Camera, roi: int = 0):
    """
    Set the ROI (width, height) to specified value.
    If no 'roi' value specified - the maximum will be set.

    Limiting ROI should reduce the time to acquire and transfer frames,
    making the tests independent from the sensor size.
    """
    (min_height, max_height) = cam.Height.get_range()
    (min_width, max_width) = cam.Width.get_range()
    # roi==0 sets to maximum
    height = max_height
    width = max_width
    if roi > 0:
        width = _clamp(roi, min_width, max_width)
        height = _clamp(roi, min_height, max_height)
        if width != roi or height != roi:
            warnings.warn(f'ROI set to minimum: ({width}x{height})')
    cam.Width.set(width)
    cam.Height.set(height)
