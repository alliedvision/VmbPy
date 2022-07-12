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
from vmbpy import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class StreamTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb.__enter__()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb.__exit__(None, None, None)
            raise Exception('Failed to lookup Camera.') from e

        try:
            self.cam.__enter__()
            self.streams = self.cam.get_streams()
        except VmbCameraError as e:
            self.cam.__exit__(None, None, None)
            raise Exception ('Failed to open Camera {}.'.format(self.cam)) from e

    def tearDown(self):
        self.cam.__exit__(None, None, None)
        self.vmb.__exit__(None, None, None)

    def test_stream_feature_discovery(self):
        # Expectation: Outside of context, all features must be cleared,
        # inside of context all features must be detected.
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                self.assertNotEqual(stream.get_all_features(), ())

    def test_stream_features_category(self):
        # Expectation: Getting features by category for an existing category returns a set of
        # features, for a non-existent category an empty set is returned
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                category = stream.get_all_features()[0].get_category()
                self.assertNotEqual(stream.get_features_by_category(category), ())
                self.assertEqual(stream.get_features_by_category("Invalid Category"), ())

    def test_stream_feature_by_name(self):
        # Expectation: A feature can be gotten by name. Invalid feature names raise a
        # VmbFeatureError
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                feat = stream.get_all_features()[0]
                self.assertEqual(stream.get_feature_by_name(feat.get_name()), feat)
                self.assertRaises(VmbFeatureError, stream.get_feature_by_name, "Invalid Name")

    def test_stream_features_by_type(self):
        # Expectation: Getting features by type returns a set of features for an existing type
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                type = stream.get_all_features()[0].get_type()
                self.assertNotEqual(stream.get_features_by_type(type), ())

    def test_stream_features_selected_by(self):
        # Expectation: Selected features can be gotten for a feature instance
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                try:
                    feat = [f for f in stream.get_all_features()
                            if f.has_selected_features()].pop()
                except IndexError:
                    self.skipTest('Could not find feature with \'selected features\'')
                self.assertNotEqual(stream.get_features_selected_by(feat), ())
