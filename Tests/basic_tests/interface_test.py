"""BSD 2-Clause License

Copyright (c) 2019, Allied Vision Technologies GmbH
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


class InterfaceTest(VmbPyTestCase):
    def setUp(self):
        self.vimba = VmbSystem.get_instance()
        self.vimba._startup()

        inters = self.vimba.get_all_interfaces()

        if not inters:
            self.vimba._shutdown()
            self.skipTest('No Interface available to test against. Abort.')

    def tearDown(self):
        self.vimba._shutdown()

    def test_interface_decode_id(self):
        # Expectation all interface ids can be decoded in something not ''
        for i in self.vimba.get_all_interfaces():
            self.assertNotEqual(i.get_id(), '')

    def test_interface_decode_type(self):
        # Expectation all interface types be in interface types
        excpected = (
            TransportLayerType.Firewire,
            TransportLayerType.Ethernet,
            TransportLayerType.Usb,
            TransportLayerType.CL,
            TransportLayerType.CSI2,
        )

        for i in self.vimba.get_all_interfaces():
            self.assertIn(i.get_type(), excpected)

    def test_interface_decode_name(self):
        # Expectation all interface names  can be decoded in something not ''
        for i in self.vimba.get_all_interfaces():
            self.assertNotEqual(i.get_name(), '')

    def test_interface_get_all_features(self):
        # Expectation: Call get_all_features raises RuntimeError outside of with
        # Inside of with return a non empty set
        inter = self.vimba.get_all_interfaces()[0]
        self.assertNotEqual(inter.get_all_features(), ())

    def test_interface_get_features_affected_by(self):
        # Expectation: Call get_features_affected_by raises RuntimeError outside of with.
        # Inside with it must either return and empty set if the given feature has no affected
        # Feature or a set off affected features
        inter = self.vimba.get_all_interfaces()[0]
        try:
            affects_feats = inter.get_feature_by_name('DeviceUpdateList')

        except VmbFeatureError:
            self.skipTest('Test requires Feature \'DeviceUpdateList\'.')

        try:
            not_affects_feats = inter.get_feature_by_name('DeviceCount')

        except VmbFeatureError:
            self.skipTest('Test requires Feature \'DeviceCount\'.')

        self.assertTrue(affects_feats.has_affected_features())
        self.assertNotEquals(inter.get_features_affected_by(affects_feats), ())

        self.assertFalse(not_affects_feats.has_affected_features())
        self.assertEquals(inter.get_features_affected_by(not_affects_feats), ())

    def test_interface_get_features_selected_by(self):
        # Expectation: Call get_features_selected_by raises RuntimeError outside of with.
        # Inside with it must either return and empty set if the given feature has no selected
        # Feature or a set off affected features
        inter = self.vimba.get_all_interfaces()[0]
        try:
            selects_feats = inter.get_feature_by_name('DeviceSelector')

        except VmbFeatureError:
            self.skipTest('Test requires Feature \'DeviceSelector\'.')

        try:
            not_selects_feats = inter.get_feature_by_name('DeviceCount')

        except VmbFeatureError:
            self.skipTest('Test requires Feature \'DeviceCount\'.')

        self.assertTrue(selects_feats.has_selected_features())
        self.assertNotEquals(inter.get_features_selected_by(selects_feats), ())

        self.assertFalse(not_selects_feats.has_selected_features())
        self.assertEquals(inter.get_features_selected_by(not_selects_feats), ())

    def test_interface_get_features_by_type(self):
        # Expectation: Call get_features_by_type raises RuntimeError outside of with
        # Inside of with return a non empty set for IntFeature (DeviceCount is IntFeature)
        inter = self.vimba.get_all_interfaces()[0]
        self.assertNotEqual(inter.get_features_by_type(IntFeature), ())

    def test_interface_get_features_by_category(self):
        # Expectation: Call get_features_by_category raises RuntimeError outside of with
        # Inside of with return a non empty set for /DeviceEnumeration)
        inter = self.vimba.get_all_interfaces()[0]
        self.assertNotEqual(inter.get_features_by_category('/DeviceEnumeration'), ())

    def test_interface_get_feature_by_name(self):
        # Expectation: Call get_feature_by_name raises RuntimeError outside of with
        # Inside of with return dont raise VimbaFeatureError for 'DeviceCount'
        # A invalid name must raise VimbaFeatureError
        inter = self.vimba.get_all_interfaces()[0]
        self.assertNoRaise(inter.get_feature_by_name, 'DeviceCount')
        self.assertRaises(VmbFeatureError, inter.get_feature_by_name, 'Invalid Name')
