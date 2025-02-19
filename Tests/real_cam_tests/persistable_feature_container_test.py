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


class PersistableFeatureContainerTest(VmbPyTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.vmb = VmbSystem.get_instance()
        cls.vmb._startup()

        try:
            cls.cam = cls.vmb.get_camera_by_id(cls.get_test_camera_id())

        except VmbCameraError as e:
            cls.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

    @classmethod
    def tearDownClass(cls) -> None:
        cls.vmb._shutdown()
        super().tearDownClass()

    def test_camera_save_load(self):
        # Expectation: A modified setting is set back to the saved value when the xml file is loaded
        with self.cam:
            fname = 'camera.xml'

            feat_height = self.cam.get_feature_by_name('Height')
            is_streamable = feat_height.is_streamable()

            # Save initial state of all features
            old_val = feat_height.get()
            self.assertNoRaise(self.cam.save_settings, fname)
            self.assertTrue(os.path.isfile(fname))

            # Modify one of the features
            min_, max_ = feat_height.get_range()
            inc = feat_height.get_increment()
            feat_height.set(max_ - min_ - inc)

            # Load saved state from xml file. This should write the old value back to the modified
            # feature
            self.assertNoRaise(self.cam.load_settings, fname)
            os.remove(fname)

            # Only streamable features will be persisted with VmbPy
            if is_streamable:
                self.assertEqual(old_val, feat_height.get())

    def test_stream_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        with self.cam:
            for stream in self.cam.get_streams():
                with self.subTest(f'stream={str(stream)}'):
                    fname = 'stream.xml'
                    self.assertNoRaise(stream.save_settings, fname)
                    self.assertTrue(os.path.isfile(fname))
                    # Room for improvement: Unfortunately there is no generic writeable feature that
                    # every stream supports that we can modify here to check that loading the
                    # settings resets the feature to the original value. So we just load again and
                    # if no errors occur assume the test to be passed.
                    self.assertNoRaise(stream.load_settings, fname)

                    os.remove(fname)

    def test_local_device_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        with self.cam:
            local_device = self.cam.get_local_device()
            fname = 'local_device.xml'
            self.assertNoRaise(local_device.save_settings, fname)
            self.assertTrue(os.path.isfile(fname))
            # Room for improvement: Unfortunately there is no generic writeable feature that every
            # local device supports that we can modify here to check that loading the settings
            # resets the feature to the original value. So we just load again and if no errors occur
            # assume the test to be passed.
            self.assertNoRaise(local_device.load_settings, fname)

            os.remove(fname)

    def test_persist_types(self):
        # Expectation: All possible persist_types are accepted
        # Note: The content of the XML is not checked!
        # Room for improvement: Check that the content of the xml file actually corresponds with
        # what is expected for each persist type
        with self.cam:
            fname = 'camera.xml'
            for t in PersistType:
                with self.subTest(f'persist_type={str(t)}'):
                    self.assertNoRaise(self.cam.save_settings, fname, persist_type=t)
                    self.assertTrue(os.path.isfile(fname))
                    os.remove(fname)

    def test_persist_flags(self):
        # Expectation: All possible persist_flags are accepted
        # Note: The content of the XML is not checked!
        # Room for improvement: Check that the content of the xml file actually corresponds with
        # what is expected for each persist flag
        with self.cam:
            fname = 'camera.xml'
            for f in ModulePersistFlags:
                with self.subTest(f'persist_flags={str(f)}'):
                    self.assertNoRaise(self.cam.save_settings, fname, persist_flags=f)
                    self.assertTrue(os.path.isfile(fname))
                    os.remove(fname)

    def test_persist_flags_combinations(self):
        # Expectation: persist_flags can be combined via logical or
        # Note: The content of the XML is not checked!
        # Room for improvement: Check that the content of the xml file actually corresponds with
        # what is expected for each persist flag
        with self.cam:
            fname = 'camera.xml'
            # test some combinations below. Testing all combinations of two flag variables takes
            # very long but can be implemented via this generator:
            # `itertools.product(vmbpy.ModulePersistFlags, repeat=2)`
            for a, b in ((ModulePersistFlags.None_, ModulePersistFlags.RemoteDevice),
                         (ModulePersistFlags.RemoteDevice, ModulePersistFlags.Interface),
                         (ModulePersistFlags.RemoteDevice, ModulePersistFlags.TransportLayer),
                         (ModulePersistFlags.Interface, ModulePersistFlags.TransportLayer)):
                with self.subTest(f'persist_flags={str(a)} | {str(b)}'):
                    self.assertNoRaise(self.cam.save_settings, fname, persist_flags=a | b)
                    self.assertTrue(os.path.isfile(fname))
                    os.remove(fname)

    def test_load_settings_api_context_sensitivity_inside_context(self):
        # Expectation: Calling load_settings outside of VmbSystem context raises a RuntimeError and
        # the error message references the appropriate context

        with self.cam:
            stream = self.cam.get_streams()[0]
            local_device = self.cam.get_local_device()

        self.assertRaises(RuntimeError, self.cam.load_settings)

        # Make sure that the error message for these classes references their parent scope
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.load_settings)
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.load_settings)

    def test_save_settings_api_context_sensitivity_inside_context(self):
        # Expectation: Calling save_settings outside of VmbSystem context raises a RuntimeError and
        # the error message references the appropriate context

        with self.cam:
            stream = self.cam.get_streams()[0]
            local_device = self.cam.get_local_device()

        self.assertRaises(RuntimeError, self.cam.save_settings)

        # Make sure that the error message for these classes references their parent scope
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.save_settings)
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               local_device.save_settings)
