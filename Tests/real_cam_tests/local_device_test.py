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
import sys

from vmbpy import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class LocalDeviceTest(VmbPyTestCase):
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
            raise Exception('Failed to open Camera {}.'.format(self.cam)) from e

    def tearDown(self):
        # In some test cases the camera might already have been closed. In that case an additional
        # call to `cam._close` will result in an error. This can be ignored in our test tearDown.
        try:
            self.cam._close()
        except Exception:
            pass
        self.vmb._shutdown()

    def test_local_device_feature_discovery(self):
        # Expectation: Features are detected for the LocalDevice
        self.assertNotEqual(self.local_device.get_all_features(), ())

    def test_local_device_features_category(self):
        # Expectation: Getting features by category for an existing category returns a set of
        # features, for a non-existent category an empty set is returned
        category = self.local_device.get_all_features()[0].get_category()
        self.assertNotEqual(self.local_device.get_features_by_category(category), ())
        self.assertEqual(self.local_device.get_features_by_category("Invalid Category"), ())

    def test_local_device_feature_by_name(self):
        # Expectation: A feature can be gotten by name. Invalid feature names raise a
        # VmbFeatureError
        feat = self.local_device.get_all_features()[0]
        self.assertEqual(self.local_device.get_feature_by_name(feat.get_name()), feat)
        self.assertRaises(VmbFeatureError, self.local_device.get_feature_by_name, "Invalid Name")

    def test_local_device_features_by_type(self):
        # Expectation: Getting features by type returns a set of features for an existing type
        type = self.local_device.get_all_features()[0].get_type()
        self.assertNotEqual(self.local_device.get_features_by_type(type), ())

    def test_local_device_features_selected_by(self):
        # Expectation: Selected features can be gotten for a feature instance
        try:
            feat = [f for f in self.local_device.get_all_features()
                    if f.has_selected_features()].pop()
        except IndexError:
            self.skipTest('Could not find feature with \'selected features\'')
        self.assertNotEqual(self.local_device.get_features_selected_by(feat), ())

    def test_local_device_context_sensitivity(self):
        # Expectation: Call get_all_features outside of Camera context raises a RuntimeError and
        # the error message references the Camera context
        local_device = self.cam.get_local_device()
        feat = local_device.get_all_features()[0]
        feat_name = feat.get_name()

        # Ensure that normal calls work while context is still open
        self.assertNoRaise(local_device.get_all_features)
        self.assertNoRaise(local_device.get_features_selected_by, feat)
        self.assertNoRaise(local_device.get_features_by_type, IntFeature)
        self.assertNoRaise(local_device.get_features_by_category, 'foo')
        self.assertNoRaise(local_device.get_feature_by_name, feat_name)

        # This closes the local device of self.cam implicitly. Alternatively it is possible to call
        # local_device._close here if that implicit behavior should not be relied upon
        self.cam._close()
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.get_all_features)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.get_features_selected_by,
                               feat)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.get_features_by_type,
                               IntFeature)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.get_features_by_category,
                               'foo')

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.get_feature_by_name,
                               feat_name)
        # open camera context again so tearDown works as expected
        self.cam._open()
