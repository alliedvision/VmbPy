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
import tempfile

from vmbpy import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class PersistableFeatureContainerTest(VmbPyTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.vmb = VmbSystem.get_instance()
        cls.vmb._startup()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.vmb._shutdown()
        super().tearDownClass()

    def test_transport_layer_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        for tl in self.vmb.get_all_transport_layers():
            with self.subTest(f'transport_layer={str(tl)}'):
                fname = 'transport_layer.xml'
                tl.save_settings(fname)
                # Room for improvement: Unfortunately there is no generic writeable feature that
                # every interface supports that we can modify here to check that loading the
                # settings resets the feature to the original value. So we just load again and if no
                # errors occur assume the test to be passed.
                tl.load_settings(fname)

                os.remove(fname)

    def test_interface_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        for inter in self.vmb.get_all_interfaces():
            with self.subTest(f'interface={str(inter)}'):
                fname = 'interface.xml'
                inter.save_settings(fname)
                # Room for improvement: Unfortunately there is no generic writeable feature that
                # every interface supports that we can modify here to check that loading the
                # settings resets the feature to the original value. So we just load again and if no
                # errors occur assume the test to be passed.
                inter.load_settings(fname)

                os.remove(fname)

    def test_save_settings_type_error(self):
        # Expectation: Using parameters with incorrect type raises a TypeError
        # Use a transport layer to access save settings. Precise class does not matter. It only
        # needs to provide access to the method
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(TypeError, tl.save_settings, 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', PersistType.All, 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', PersistType.All,
                          ModulePersistFlags.None_, 'foo')

    def test_load_settings_type_error(self):
        # Expectation: Using parameters with incorrect type raises a TypeError
        # Use a transport layer to access save settings. Precise class does not matter. It only
        # needs to provide access to the method
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(TypeError, tl.load_settings, 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', PersistType.All, 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', PersistType.All,
                          ModulePersistFlags.None_, 'foo')

    def test_save_settings_verify_path(self):
        # Expectation: Valid files end with .xml and can be either a absolute path or relative
        # path to the given File. Everything else is a ValueError.

        # create a temporary directory to test relative paths with subdirs
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_paths = (
                'valid1_save.xml',
                os.path.join('.', 'valid2_save.xml'),
                os.path.join(tmpdir, 'valid3_save.xml'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valid4_save.xml'),
            )
            tl = self.vmb.get_all_transport_layers()[0]
            self.assertRaises(ValueError, tl.save_settings, 'inval.xm')

            for path in valid_paths:
                self.assertNoRaise(tl.save_settings, path)
                os.remove(path)

    def test_load_settings_verify_path(self):
        # Expectation: Valid files end with .xml and must exist before before any execution.

        # create a temporary directory to test relative paths with subdirs
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_paths = (
                'valid1_load.xml',
                os.path.join('.', 'valid2_load.xml'),
                os.path.join(tmpdir, 'valid3_load.xml'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valid4_load.xml'),
            )
            tl = self.vmb.get_all_transport_layers()[0]
            self.assertRaises(ValueError, tl.load_settings, 'inval.xm', PersistType.All)

            for path in valid_paths:
                self.assertRaises(ValueError, tl.load_settings, path, PersistType.All)

            for path in valid_paths:
                tl.save_settings(path, PersistType.All)

                self.assertNoRaise(tl.load_settings, path, PersistType.All)
                os.remove(path)

    def test_load_settings_api_context_sensitivity_inside_context(self):
        # Expectation: Calling load_settings outside of VmbSystem context raises a RuntimeError and
        # the error message references the VmbSystem context

        tl = self.vmb.get_all_transport_layers()[0]
        inter = self.vmb.get_all_interfaces()[0]

        # Manually manage VmbSystem context for this test
        self.vmb._shutdown()

        # Make sure that the error message for these classes references their parent scope
        self.assertRaisesRegex(RuntimeError,
                               'outside of VmbSystem.* context',
                               tl.load_settings)
        self.assertRaisesRegex(RuntimeError,
                               'outside of VmbSystem.* context',
                               inter.load_settings)

        # Start VmbSystem again so tearDown method works as expected
        self.vmb._startup()

    def test_save_settings_api_context_sensitivity_inside_context(self):
        # Expectation: Calling save_settings outside of VmbSystem context raises a RuntimeError and
        # the error message references the VmbSystem context

        tl = self.vmb.get_all_transport_layers()[0]
        inter = self.vmb.get_all_interfaces()[0]

        # Manually manage VmbSystem context for this test
        self.vmb._shutdown()

        # Make sure that the error message for these classes references their parent scope
        self.assertRaisesRegex(RuntimeError,
                               'outside of VmbSystem.* context',
                               tl.save_settings)
        self.assertRaisesRegex(RuntimeError,
                               'outside of VmbSystem.* context',
                               inter.save_settings)

        # Start VmbSystem again so tearDown method works as expected
        self.vmb._startup()
