from vmbpy import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class TransportLayerTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        # Actually enter context manager manually because it needs to be entered during test runs
        # and `_startup` will otherwise experience VmbErrorAlready
        self.vmb.__enter__()

        transport_layers = self.vmb.get_all_transport_layers()

        if not transport_layers:
            self.vmb.__exit__(None, None, None)
            self.skipTest('No Transport Layers available to test against. Abort.')

    def tearDown(self):
        self.vmb.__exit__(None, None, None)

    def test_transport_layer_interfaces_have_correct_type(self):
        # Expectation: All interfaces reported by the transport layer are of type Interface
        for tl in self.vmb.get_all_transport_layers():
            with self.subTest(f'transport_layer={str(tl)}'):
                interfaces = tl.get_interfaces()
                if not interfaces:
                    self.skipTest(f'Could not test because {tl} did not provide any interfaces')
                for i in interfaces:
                    self.assertIsInstance(i, Interface)

    def test_transport_layer_cameras_have_correct_type(self):
        # Expectation: All cameras reported by the transport layer are of type Camera
        for tl in self.vmb.get_all_transport_layers():
            with self.subTest(f'transport_layer={str(tl)}'):
                cameras = tl.get_cameras()
                if not cameras:
                    self.skipTest(f'Could not test because {tl} did not provide any cameras')
                for cam in cameras:
                    self.assertIsInstance(cam, Camera)

    def test_transport_layer_decode_id(self):
        # Expectation all transport layer ids can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_id(), '')

    def test_transport_layer_decode_name(self):
        # Expectation all transport layer names can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_name(), '')

    def test_transport_layer_decode_model_name(self):
        # Expectation all transport layer model names can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_model_name(), '')

    def test_transport_layer_decode_vendor(self):
        # Expectation all transport layer vendor fields can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_vendor(), '')

    def test_transport_layer_decode_version(self):
        # Expectation all transport layer version fields can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_version(), '')

    def test_transport_layer_decode_path(self):
        # Expectation all transport layer path fields can be decoded to something other than ''
        for tl in self.vmb.get_all_transport_layers():
            self.assertNotEqual(tl.get_path(), '')

    def test_transport_layer_decode_type(self):
        # Expectation all transport layer types be in transport layer types
        for tl in self.vmb.get_all_transport_layers():
            self.assertIn(tl.get_type(), TransportLayerType)
