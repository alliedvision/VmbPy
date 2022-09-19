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


class VmbSystemTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()

    def tearDown(self):
        pass

    def test_singleton(self):
        # Expected behavior: Multiple calls to VmbSystemTest.get_instance() return the same object.
        self.assertEqual(self.vmb, VmbSystem.get_instance())

    def test_get_version(self):
        # Expectation: Returned Version is not empty and does not raise any exceptions.
        self.assertNotEqual(self.vmb.get_version(), "")

    def test_set_path_configuration(self):
        # Expectation: Internal path configuration starts out as None and is updated using correct
        # path separator depending on operating system. Testing that VmbC actually uses this value
        # as expected is not really possible in a generic way
        try:
            # VmbC expects separator on Windows to be ";". For other platforms it should be ":"
            sep = ';' if sys.platform == 'win32' else ':'

            self.assertIsNone(self.vmb._Impl__path_configuration)
            self.vmb.set_path_configuration('foo')
            self.assertEqual(self.vmb._Impl__path_configuration, 'foo')
            self.vmb.set_path_configuration('foo', 'bar')
            self.assertEqual(self.vmb._Impl__path_configuration, 'foo' + sep + 'bar')
            # Crude check to see that configuration is applied: Try to start API with this invalid
            # configuration. If no TLs are found, that is probably a sign that the configuration is
            # honored
            with self.assertRaises(VmbTransportLayerError):
                with self.vmb:
                    pass
        finally:
            # Explicitly reset path configuration to None so we do not impact subsequent test cases
            self.vmb._Impl__path_configuration = None

    def test_set_path_configuration_while_entering_context(self):
        # Expectation: `set_configuration_path` returns the `VmbSystem` instance to allow setting
        # the configuration while entering the context manager. This tests sets an invalid
        # configuration and catches the raised `VmbTransportLayerError` to ensure that the
        # configuration is applied as expected
        try:
            with self.assertRaises(VmbTransportLayerError):
                with self.vmb.set_path_configuration('foo', 'bar'):
                    pass
        finally:
            # Explicitly reset path configuration to None so we do not impact subsequent test cases
            self.vmb._Impl__path_configuration = None

    def test_get_all_cameras_type(self):
        # Expectation: All camera instances returned by `get_all_cameras` have correct type
        with self.vmb:
            for cam in self.vmb.get_all_cameras():
                self.assertIsInstance(cam, Camera)

    def test_get_camera_by_id(self):
        # Expectation: Getting a camera by id should return the expected camera
        with self.vmb:
            for cam in self.vmb.get_all_cameras():
                self.assertEqual(cam,
                                 self.vmb.get_camera_by_id(cam.get_id()))

    def test_get_camera_by_id_failure(self):
        # Expected behavior: Lookup of a currently unavailable camera must throw an
        # VmbCameraError
        with self.vmb:
            self.assertRaises(VmbCameraError, self.vmb.get_camera_by_id, 'Invalid ID')

    def test_get_all_interfaces_type(self):
        # Expectation: All interface instances returned by `get_all_interfaces` have correct type
        with self.vmb:
            for inter in self.vmb.get_all_interfaces():
                self.assertIsInstance(inter, Interface)

    def test_get_interface_by_id(self):
        # Expectation: Getting an interface by id should return the expected interface
        with self.vmb:
            for inter in self.vmb.get_all_interfaces():
                self.assertEqual(inter,
                                 self.vmb.get_interface_by_id(inter.get_id()))

    def test_get_interface_by_id_failure(self):
        # Expected behavior: Lookup of a currently unavailable interface must throw an
        # VmbInterfaceError
        with self.vmb:
            self.assertRaises(VmbInterfaceError, self.vmb.get_interface_by_id, 'Invalid ID')

    def test_get_all_transport_layers_type(self):
        # Expectation: All transport layer instances returned by `get_all_transport_layers` have
        # correct type
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertIsInstance(tl, TransportLayer)

    def test_get_transport_layer_by_id(self):
        # Expectation: Getting a transport layer by id should return the expected tl
        with self.vmb:
            for tl in self.vmb.get_all_transport_layers():
                self.assertEqual(tl,
                                 self.vmb.get_transport_layer_by_id(tl.get_id()))

    def test_get_transport_layer_by_id_failure(self):
        # Expected behavior: Lookup of a currently unavailable Transport Layer must throw an
        # VmbTransportLayerError
        with self.vmb:
            self.assertRaises(VmbTransportLayerError,
                              self.vmb.get_transport_layer_by_id,
                              'Invalid ID')

    def test_get_feature_by_name_failure(self):
        # Expected behavior: Lookup of a currently unavailable feature must throw an
        # VmbFeatureError
        with self.vmb:
            self.assertRaises(VmbFeatureError, self.vmb.get_feature_by_name, 'Invalid ID')

    def test_runtime_check_failure(self):
        with self.vmb:
            # All functions with RuntimeTypeCheckEnable must return a TypeError on Failure
            self.assertRaises(TypeError, self.vmb.get_transport_layer_by_id, 0)
            self.assertRaises(TypeError, self.vmb.get_camera_by_id, 0)
            self.assertRaises(TypeError, self.vmb.get_cameras_by_tl, 0)
            self.assertRaises(TypeError, self.vmb.get_cameras_by_interface, 0)
            self.assertRaises(TypeError, self.vmb.get_interface_by_id, 1)
            self.assertRaises(TypeError, self.vmb.get_interfaces_by_tl, 1)
            self.assertRaises(TypeError, self.vmb.get_feature_by_name, 0)
            self.assertRaises(TypeError, self.vmb.enable_log, '-1')

            self.assertRaises(TypeError, self.vmb.get_features_selected_by, '-1')
            self.assertRaises(TypeError, self.vmb.get_features_by_type, [])
            self.assertRaises(TypeError, self.vmb.register_camera_change_handler, 0)
            self.assertRaises(TypeError, self.vmb.unregister_camera_change_handler, 0)
            self.assertRaises(TypeError, self.vmb.register_interface_change_handler, 0)
            self.assertRaises(TypeError, self.vmb.unregister_interface_change_handler, 0)

    def test_vmbsystem_context_manager_reentrancy(self):
        # Expectation: Implemented Context Manager must be reentrant, not causing
        # multiple starts of the API (would cause C-Errors)

        with self.vmb:
            with self.vmb:
                with self.vmb:
                    pass

    def test_vmbsystem_api_context_sensitivity_inside_context(self):
        # Expectation: VmbSystem has functions that shall only be callable inside the Context and
        # calling outside must cause a runtime error. This test check only if the RuntimeErrors
        # are triggered then called Outside of the with block.
        self.assertRaises(RuntimeError, self.vmb.read_memory, 0, 0)
        self.assertRaises(RuntimeError, self.vmb.write_memory, 0, b'foo')
        self.assertRaises(RuntimeError, self.vmb.get_all_transport_layers)
        self.assertRaises(RuntimeError, self.vmb.get_transport_layer_by_id)
        self.assertRaises(RuntimeError, self.vmb.get_all_interfaces)
        self.assertRaises(RuntimeError, self.vmb.get_interface_by_id, 'id')
        self.assertRaises(RuntimeError, self.vmb.get_all_cameras)
        self.assertRaises(RuntimeError, self.vmb.get_camera_by_id, 'id')
        self.assertRaises(RuntimeError, self.vmb.get_all_features)

        # Enter scope to get handle on TransportLayer/Interface/Features as valid parameters for the
        # test: Don't to this in production code because the feature will be invalid if use.
        with self.vmb:
            tl = self.vmb.get_all_transport_layers()[0]
            inter = self.vmb.get_all_interfaces()[0]
            feat = self.vmb.get_all_features()[0]

        self.assertRaises(RuntimeError, self.vmb.get_interfaces_by_tl, tl)
        self.assertRaises(RuntimeError, self.vmb.get_cameras_by_tl, tl)
        self.assertRaises(RuntimeError, self.vmb.get_cameras_by_interface, inter)
        self.assertRaises(RuntimeError, self.vmb.get_features_selected_by, feat)
        self.assertRaises(RuntimeError, self.vmb.get_features_by_type, IntFeature)
        self.assertRaises(RuntimeError, self.vmb.get_features_by_category, 'foo')
        self.assertRaises(RuntimeError, self.vmb.get_feature_by_name, 'foo')

    def test_vmbsystem_api_context_sensitivity_outside_context(self):
        # Expectation: VmbSystem has functions that shall only be callable outside the Context and
        # calling inside must cause a runtime error. This test check only if the RuntimeErrors are
        # triggered then called inside of the with block.
        with self.vmb:
            self.assertRaises(RuntimeError, self.vmb.set_path_configuration, 'foo')

    def test_api_context_is_not_entered_on_startup_errors(self):
        # Expectation: If an error occurs during startup, the context of VmbSystem should not be
        # entered.
        with self.assertRaises(VmbTransportLayerError):
            # This raises an error during startup (as part of the __enter__ call). Exceptions that
            # are raised in __enter__ do NOT trigger a call to __exit__ automatically, because
            # Python does not consider them to actually have entered the context as expected.
            with self.vmb.set_path_configuration('INVALID PATH CONFIGURATION'):
                self.fail('The context was entered even though an error was encountered')

        # Explicitly reset path configuration to None so we do not impact subsequent test cases
        self.vmb._Impl__path_configuration = None
        # Perform another call to make sure that the context is not lingering after the context
        # manager has been left correctly
        self.assertRaises(RuntimeError, self.vmb.read_memory, 0, 0)
