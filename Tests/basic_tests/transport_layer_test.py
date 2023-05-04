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


class TransportLayerTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()

        with self.vmb:
            transport_layers = self.vmb.get_all_transport_layers()
            if not transport_layers:
                self.skipTest('No Transport Layers available to test against. Abort.')

    def tearDown(self):
        pass

    def test_transport_layer_interfaces_have_correct_type(self):
        # Expectation: All interfaces reported by the transport layer are of type Interface
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                with self.subTest(f'transport_layer={str(tl)}'):
                    interfaces = tl.get_interfaces()
                    if not interfaces:
                        self.skipTest(f'Could not test because {tl} did not provide any interfaces')
                    for i in interfaces:
                        self.assertIsInstance(i, Interface)

    def test_transport_layer_cameras_have_correct_type(self):
        # Expectation: All cameras reported by the transport layer are of type Camera
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                with self.subTest(f'transport_layer={str(tl)}'):
                    cameras = tl.get_cameras()
                    if not cameras:
                        self.skipTest(f'Could not test because {tl} did not provide any cameras')
                    for cam in cameras:
                        self.assertIsInstance(cam, Camera)

    def test_transport_layer_decode_id(self):
        # Expectation all transport layer ids can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_id(), '')

    def test_transport_layer_decode_name(self):
        # Expectation all transport layer names can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_name(), '')

    def test_transport_layer_decode_model_name(self):
        # Expectation all transport layer model names can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_model_name(), '')

    def test_transport_layer_decode_vendor(self):
        # Expectation all transport layer vendor fields can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_vendor(), '')

    def test_transport_layer_decode_version(self):
        # Expectation all transport layer version fields can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_version(), '')

    def test_transport_layer_decode_path(self):
        # Expectation all transport layer path fields can be decoded to something other than ''
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_path(), '')

    def test_transport_layer_decode_type(self):
        # Expectation all transport layer types be in transport layer types
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertIn(tl.get_type(), TransportLayerType)

    def test_transport_layer_get_all_features(self):
        # Expectation: Call get_all_features returns a non empty set
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_all_features(), ())

    def test_transport_layer_get_features_selected_by(self):
        # Expectation: Call get_features_selected_by must either return and empty set if the given
        # feature has no selected Feature or a set of affected features
        with self.vmb:
            tl = self.vmb.get_all_transport_layers()[0]
            try:
                selects_feats = tl.get_feature_by_name('InterfaceSelector')

            except VmbFeatureError:
                self.skipTest('Test requires Feature \'InterfaceSelector\'.')

            try:
                not_selects_feats = tl.get_feature_by_name('TLID')

            except VmbFeatureError:
                self.skipTest('Test requires Feature \'TLID\'.')

            self.assertTrue(selects_feats.has_selected_features())
            self.assertNotEqual(tl.get_features_selected_by(selects_feats), ())

            self.assertFalse(not_selects_feats.has_selected_features())
            self.assertEqual(tl.get_features_selected_by(not_selects_feats), ())

    def test_transport_layer_get_features_by_type(self):
        # Expectation: Call get_features_by_type returns a non empty set for StringFeature
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_features_by_type(StringFeature), ())

    def test_transport_layer_get_features_by_category(self):
        # Expectation: Call get_features_by_category returns a non empty set for /SystemInformation)
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNotEqual(tl.get_features_by_category('/SystemInformation'), ())

    def test_transport_layer_get_feature_by_name(self):
        # Expectation: Call get_feature_by_name does not raise an exception for valid feature names,
        # raises a `VmbFeatureError` for invalid feature names
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertNoRaise(tl.get_feature_by_name, 'TLID')
                self.assertRaises(VmbFeatureError, tl.get_feature_by_name, 'Invalid Name')

    def test_transport_layer_context_sensitivity(self):
        # Expectation: Call get_all_features outside of VmbSystem context raises a RuntimeError and
        # the error message references the VmbSystem context
        tls_and_feats = []
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                feat = tl.get_all_features()[0]
                tls_and_feats.append((tl, feat))

        for tl, feat in tls_and_feats:
            self.assertRaisesRegex(RuntimeError,
                                   'outside of VmbSystem.* context',
                                   tl.get_all_features)

            self.assertRaisesRegex(RuntimeError,
                                   'outside of VmbSystem.* context',
                                   tl.get_features_selected_by,
                                   feat)

            self.assertRaisesRegex(RuntimeError,
                                   'outside of VmbSystem.* context',
                                   tl.get_features_by_type,
                                   IntFeature)

            self.assertRaisesRegex(RuntimeError,
                                   'outside of VmbSystem.* context',
                                   tl.get_features_by_category,
                                   'foo')

            self.assertRaisesRegex(RuntimeError,
                                   'outside of VmbSystem.* context',
                                   tl.get_feature_by_name,
                                   'foo')
