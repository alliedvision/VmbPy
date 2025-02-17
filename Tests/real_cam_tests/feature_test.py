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
import threading
import unittest

from vmbpy import *
from vmbpy.feature import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class CamBaseFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.height = self.cam.get_feature_by_name('Height')

        except VmbCameraError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'Height\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_name(self):
        # Expectation: Return decoded FeatureName
        self.assertEqual(self.height.get_name(), 'Height')

    def test_get_flags(self):
        # Expectation: Return decoded FeatureFlags
        self.assertEqual(self.height.get_flags(), (FeatureFlags.Read, FeatureFlags.Write))

    def test_get_category(self):
        # Expectation: Return decoded category
        self.assertNotEqual(self.height.get_category(), '')

    def test_get_display_name(self):
        # Expectation: Return decoded category
        self.assertEqual(self.height.get_display_name(), 'Height')

    def test_get_polling_time(self):
        # Expectation: Return polling time. Only volatile features return
        # anything other than zero.
        self.assertEqual(self.height.get_polling_time(), 0)

    def test_get_unit(self):
        # Expectation: If Unit exists, return unit else return ''
        self.assertIsInstance(self.height.get_unit(), str)

    def test_get_representation(self):
        # Expectation: Get numeric representation if existing else ''
        self.assertIsInstance(self.height.get_representation(), str)

    def test_get_visibility(self):
        # Expectation: Get UI Visibility
        self.assertIn(self.height.get_visibility(), FeatureVisibility)

    def test_get_tooltip(self):
        # Expectation: Get tooltip if existing else ''
        self.assertIsInstance(self.height.get_tooltip(), str)

    def test_get_description(self):
        # Expectation: Get decoded description
        self.assertNotEqual(self.height.get_description(), '')

    def test_get_sfnc_namespace(self):
        # Expectation: Get decoded sfnc namespace
        self.assertNotEqual(self.height.get_sfnc_namespace(), '')

    def test_is_streamable(self):
        # Expectation: Streamable features shall return a bool
        self.assertIsInstance(self.height.is_streamable(), bool)

    def test_has_selected_features(self):
        # Expectation:Features that select features shall return a bool
        self.assertIsInstance(self.height.has_selected_features(), bool)

    def test_get_access_mode(self):
        # Expectation: Read/Write Features return (True, True), ReadOnly return (True, False)
        self.assertEqual(self.height.get_access_mode(), (True, True))

    def test_is_readable(self):
        # Expectation: True if feature grant read access else False
        self.assertTrue(self.height.is_readable())

    def test_is_writeable(self):
        # Expectation: True if feature grant write access else False
        self.assertTrue(self.height.is_writeable())

    def test_write_access_changes_when_streaming(self):
        # Expectation: Feature write access changes when streaming is started (warning: some
        # features may be writeable even during streaming!)
        self.assertTrue(self.height.is_writeable())
        try:
            self.cam.start_streaming(lambda cam, stream, frame: cam.queue_frame(frame))
            self.assertFalse(self.height.is_writeable())
        finally:
            self.cam.stop_streaming()

    def test_change_handler(self):
        # Expectation: A given change handler is executed on value change.
        # Adding the same handler multiple times shall not lead to multiple executions.
        # The same goes for double unregister.

        class Handler:
            def __init__(self):
                self.event = threading.Event()
                self.call_cnt = 0

            def __call__(self, feat):
                self.call_cnt += 1
                self.event.set()

        handler = Handler()

        self.height.register_change_handler(handler)
        self.height.register_change_handler(handler)

        tmp = self.height.get()

        min_, _ = self.height.get_range()
        inc = self.height.get_increment()

        if min_ <= tmp - inc:
            self.height.set(tmp - inc)

        else:
            self.height.set(tmp + inc)

        handler.event.wait()

        self.height.unregister_change_handler(handler)
        self.height.unregister_change_handler(handler)

        self.height.set(tmp)

        self.assertEqual(handler.call_cnt, 1)

    def test_stringify_features(self):
        # Expectation: Each Feature must have a __str__ method. Depending on the Feature
        # current Values are queried, this can fail. In those cases, all exceptions are
        # fetched -> all features must be strinify able without raising any exception
        for feat in self.vmb.get_all_features():
            self.assertNoRaise(str, feat)

        for feat in self.cam.get_all_features():
            self.assertNoRaise(str, feat)


class CamBoolFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.feat: BoolFeature = self.cam.get_features_by_type(BoolFeature)[0]

        except (VmbCameraError, IndexError):
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Could not find a Bool feature to use for the test')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: BoolFeature must return BoolFeature on get_type
        self.assertEqual(self.feat.get_type(), BoolFeature)

    def test_get(self):
        # Expectation: returns current boolean value.
        if self.feat.is_readable():
            self.assertNoRaise(self.feat.get)
        else:
            self.skipTest(f'Feature {self.feat.get_name()} is not readable')

    def test_set(self):
        # Expectation: Raises invalid Access on non-writeable features, does not raise an error on
        # writeable features.
        if not self.feat.is_readable():
            self.skipTest(f'Feature {self.feat.get_name()} is not readable')
        else:
            value = self.feat.get()
            if self.feat.is_writeable():
                self.assertNoRaise(self.feat.set, value)
            else:
                self.assertRaises(VmbFeatureError, self.feat.set, value)


class CamCommandFeatureTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        self.feat = None
        for inter in self.vmb.get_all_interfaces():
            try:
                self.feat = inter.get_features_by_type(CommandFeature)[0]
            except IndexError:
                # The interface does not have any CommandFeatures
                pass

        if self.feat is None:
            self.vmb._shutdown()
            self.skipTest('Could not find a CommandFeature to execute the test cases with')

    def tearDown(self):
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: CommandFeature must return CommandFeature on get_type
        self.assertEqual(self.feat.get_type(), CommandFeature)


@unittest.skipIf(VmbPyTestCase.get_test_camera_id().startswith("Sim"),
                 "Test suite skipped in simulation mode.")
class CamEnumFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.feat_r = self.cam.get_feature_by_name('DeviceScanType')

        except VmbFeatureError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'DeviceScanType\' not available.')

        try:
            self.feat_rw = self.cam.get_feature_by_name('AcquisitionMode')

        except VmbFeatureError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'AcquisitionMode\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: EnumFeature must return EnumFeature on get_type
        self.assertEqual(self.feat_r.get_type(), EnumFeature)
        self.assertEqual(self.feat_rw.get_type(), EnumFeature)

    def test_entry_as_bytes(self):
        # Expectation: Get EnumEntry as encoded byte sequence
        expected = b'MultiFrame'
        entry = self.feat_rw.get_entry('MultiFrame')

        self.assertEqual(bytes(entry), expected)

    def test_entry_as_tuple(self):
        # Expectation: Get EnumEntry as (str, int)
        entry = self.feat_rw.get_entry('MultiFrame')
        self.assertEqual(entry.as_tuple(), self.feat_rw.get_entry(int(entry)).as_tuple())

    def test_get_all_entries(self):
        # Expectation: Get all possible enum entries regardless of the availability
        expected = (self.feat_r.get_entry('Areascan'),)

        for e in expected:
            self.assertIn(e, self.feat_r.get_all_entries())

        expected = (
            self.feat_rw.get_entry('SingleFrame'),
            self.feat_rw.get_entry('MultiFrame'),
            self.feat_rw.get_entry('Continuous')
        )

        for e in expected:
            self.assertIn(e, self.feat_rw.get_all_entries())

    def test_get_avail_entries(self):
        # Expectation: All returned enum entries must be available
        for e in self.feat_r.get_available_entries():
            self.assertTrue(e.is_available())

        for e in self.feat_rw.get_available_entries():
            self.assertTrue(e.is_available())

    def test_get_entry_int(self):
        # Expectation: Lookup a given entry by using an int as key.
        # Invalid keys must return VmbFeatureError.

        expected = self.feat_r.get_all_entries()[0]
        self.assertEqual(self.feat_r.get_entry(int(expected)), expected)

        expected = self.feat_rw.get_all_entries()[1]
        self.assertEqual(self.feat_rw.get_entry(int(expected)), expected)

        self.assertRaises(VmbFeatureError, self.feat_r.get_entry, -1)
        self.assertRaises(VmbFeatureError, self.feat_rw.get_entry, -1)

    def test_get_entry_str(self):
        # Expectation: Lookup a given entry by using a str as key.
        # Invalid keys must return VmbFeatureError.

        expected = self.feat_r.get_all_entries()[0]
        self.assertEqual(self.feat_r.get_entry(str(expected)), expected)

        expected = self.feat_rw.get_all_entries()[1]
        self.assertEqual(self.feat_rw.get_entry(str(expected)), expected)

        self.assertRaises(VmbFeatureError, self.feat_r.get_entry, 'Should be invalid')
        self.assertRaises(VmbFeatureError, self.feat_rw.get_entry, 'Should be invalid')

    def test_get(self):
        # Expectation: Get must return the current value.
        self.assertNoRaise(self.feat_r.get)
        self.assertNoRaise(self.feat_rw.get)

    def test_set_entry(self):
        # Expectation: Set given enum entry if feature is writable.
        # Raises:
        # - VmbFeatureError if enum entry is from other enum feature.
        # - VmbFeatureError if feature is read only

        # Read Only Feature
        entry = self.feat_r.get_all_entries()[0]
        self.assertRaises(VmbFeatureError, self.feat_r.set, entry)

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, self.feat_rw.get_entry(2))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by setting the feature from the ReadOnly entry.
            self.assertRaises(VmbFeatureError, self.feat_rw.set, entry)

        finally:
            self.feat_rw.set(old_entry)

    def test_set_str(self):
        # Expectation: Set given enum entry string value if feature is writable.
        # Raises:
        # - VmbFeatureError if given string is not associated with this feature.
        # - VmbFeatureError if feature is read only

        # Read Only Feature
        if not self.feat_r.is_writeable():
            self.assertRaises(VmbFeatureError, self.feat_r.set, str(self.feat_r.get_entry(0)))

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, str(self.feat_rw.get_entry(2)))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by an invalid enum value
            self.assertRaises(VmbFeatureError, self.feat_rw.set, 'Hopefully invalid')

        finally:
            self.feat_rw.set(old_entry)

    def test_set_int(self):
        # Expectation: Set given enum entry int value if feature is writable.
        # Raises:
        # - VmbFeatureError if given int is not associated with this feature.
        # - VmbFeatureError if feature is read only

        # Read Only Feature
        if not self.feat_r.is_writeable():
            self.assertRaises(VmbFeatureError, self.feat_r.set, int(self.feat_r.get_entry(0)))

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, int(self.feat_rw.get_entry(2)))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by an invalid enum value
            self.assertRaises(VmbFeatureError, self.feat_rw.set, -23)

        finally:
            self.feat_rw.set(old_entry)

    def test_set_in_callback(self):
        # Expected behavior: A set operation within a change handler must
        # Raise a VmbFeatureError to prevent an endless handler execution.

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VmbFeatureError:
                    self.raised = True

                self.event.set()

        old_entry = self.feat_rw.get()

        try:
            handler = Handler()
            self.feat_rw.register_change_handler(handler)

            # Trigger change handler and wait for callback execution.
            self.feat_rw.set(self.feat_rw.get())
            handler.event.wait()

            self.assertTrue(handler.raised)

        finally:
            self.feat_rw.unregister_change_handler(handler)
            self.feat_rw.set(old_entry)


class CamFloatFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.feat_r = self.vmb.get_feature_by_name('Elapsed')

        except VmbFeatureError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'Elapsed\' not available.')

        try:
            self.feat_rw = self.cam.get_feature_by_name('ExposureTime')

        except VmbFeatureError:
            # Some Cameras name ExposureTime as ExposureTimeAbs
            try:
                self.feat_rw = self.cam.get_feature_by_name('ExposureTimeAbs')

            except VmbFeatureError:
                self.cam._close()
                self.vmb._shutdown()
                self.skipTest('Required Feature \'ExposureTime\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: FloatFeature returns FloatFeature on get_type.
        self.assertEqual(self.feat_r.get_type(), FloatFeature)
        self.assertEqual(self.feat_rw.get_type(), FloatFeature)

    def test_get(self):
        # Expectation: Get current value.

        self.assertNoRaise(self.feat_r.get)
        self.assertNoRaise(self.feat_rw.get)

    def test_get_range(self):
        # Expectation: Get value range. Raise VmbFeatureError on non-read access.
        self.assertNoRaise(self.feat_r.get_range)
        self.assertNoRaise(self.feat_rw.get_range)

    def test_get_increment(self):
        # Expectation: Get value increment if existing. If this Feature has no
        # increment, None is returned.

        self.assertNoRaise(self.feat_r.get_increment)
        self.assertNoRaise(self.feat_rw.get_increment)

    def test_set(self):
        # Expectation: Set value. Errors:
        # VmbFeatureError if access right are not writable
        # VmbFeatureError if value is out of bounds

        # Read only feature
        self.assertRaises(VmbFeatureError, self.feat_r.set, 0.0)

        # Read/Write Feature
        old_value = self.feat_rw.get()

        try:
            delta = 0.1

            # Range test
            min_, max_ = self.feat_rw.get_range()

            # Within bounds (no error)
            self.assertNoRaise(self.feat_rw.set, min_)
            self.assertAlmostEqual(self.feat_rw.get(), min_)
            self.assertNoRaise(self.feat_rw.set, max_)
            self.assertAlmostEqual(self.feat_rw.get(), max_)

            # Out of bounds (must raise)
            self.assertRaises(VmbFeatureError, self.feat_rw.set, min_ - delta)
            self.assertRaises(VmbFeatureError, self.feat_rw.set, max_ + delta)

        finally:
            self.feat_rw.set(old_value)

    def test_set_in_callback(self):
        # Expectation: Calling set within change_handler must raise an VmbFeatureError

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VmbFeatureError:
                    self.raised = True

                self.event.set()

        old_entry = self.feat_rw.get()

        try:
            handler = Handler()
            self.feat_rw.register_change_handler(handler)

            # Trigger change handler and wait for callback execution.
            self.feat_rw.set(self.feat_rw.get())
            handler.event.wait()

            self.assertTrue(handler.raised)

        finally:
            self.feat_rw.unregister_change_handler(handler)
            self.feat_rw.set(old_entry)


class CamIntFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.feat_r = self.cam.get_feature_by_name('HeightMax')

        except VmbFeatureError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'HeightMax\' not available.')

        try:
            self.feat_rw = self.cam.get_feature_by_name('Height')

        except VmbFeatureError:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'Height\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: IntFeature must return IntFeature on get_type
        self.assertEqual(self.feat_r.get_type(), IntFeature)
        self.assertEqual(self.feat_rw.get_type(), IntFeature)

    def test_get(self):
        # Expectation: Get current value

        self.assertNoRaise(self.feat_r.get)
        self.assertNoRaise(self.feat_rw.get)

    def test_get_range(self):
        # Expectation: Get range of accepted values
        self.assertNoRaise(self.feat_r.get_range)
        self.assertNoRaise(self.feat_rw.get_range)

    def test_get_increment(self):
        # Expectation: Get step between valid values
        self.assertNoRaise(self.feat_r.get_increment)
        self.assertNoRaise(self.feat_rw.get_increment)

    def test_set(self):
        # Expectation: Set value or raise VmbFeatureError under the following conditions.
        # 1) Invalid Access Rights
        # 2) Misaligned value.
        # 3) Out-of-bounds Access

        # Read only feature
        self.assertRaises(VmbFeatureError, self.feat_r.set, 0)

        # Writable feature
        old_value = self.feat_rw.get()

        try:
            inc = self.feat_rw.get_increment()
            min_, max_ = self.feat_rw.get_range()

            # Normal usage
            self.assertNoRaise(self.feat_rw.set, min_)
            self.assertEqual(self.feat_rw.get(), min_)
            self.assertNoRaise(self.feat_rw.set, max_)
            self.assertEqual(self.feat_rw.get(), max_)

            # Out of bounds access.
            self.assertRaises(VmbFeatureError, self.feat_rw.set, min_ - inc)
            self.assertRaises(VmbFeatureError, self.feat_rw.set, max_ + inc)

        finally:
            self.feat_rw.set(old_value)

    def test_set_in_callback(self):
        # Expectation: Setting a value within a Callback must raise a VmbFeatureError

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VmbFeatureError:
                    self.raised = True

                self.event.set()

        old_entry = self.feat_rw.get()

        try:
            handler = Handler()
            self.feat_rw.register_change_handler(handler)

            # Trigger change handler and wait for callback execution.
            min_, _ = self.feat_rw.get_range()
            inc = self.feat_rw.get_increment()

            if min_ <= (old_entry - inc):
                self.feat_rw.set(old_entry - inc)

            else:
                self.feat_rw.set(old_entry + inc)

            handler.event.wait()

            self.assertTrue(handler.raised)

        finally:
            self.feat_rw.unregister_change_handler(handler)
            self.feat_rw.set(old_entry)


class CamStringFeatureTest(VmbPyTestCase):
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

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to open Camera.') from e

        self.feat_r = None
        feats = self.cam.get_features_by_type(StringFeature)

        for feat in feats:
            if feat.get_access_mode() == (True, False):
                self.feat_r = feat
                n = feat.get_name()
                print(f"Set read-only feature '{n}'")
                break

        if self.feat_r is None:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Test requires read only StringFeature.')

        self.feat_rw = None
        feats = self.cam.get_features_by_type(StringFeature)

        for feat in feats:
            if feat.get_access_mode() == (True, True):
                self.feat_rw = feat
                n = feat.get_name()
                print(f"Set read-write feature '{n}'")
                break

        if self.feat_rw is None:
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Test requires read/write StringFeature.')

    def tearDown(self):
        self.cam._close()
        self.vmb._shutdown()

    def test_get_type(self):
        # Expectation: StringFeature must return StringFeature on get_type
        self.assertEqual(self.feat_r.get_type(), StringFeature)
        self.assertEqual(self.feat_rw.get_type(), StringFeature)

    def test_get(self):
        # Expectation: Get current value without raising an exception
        self.assertNoRaise(self.feat_r.get)
        self.assertNoRaise(self.feat_rw.get)

    def test_get_max_length(self):
        # Expectation: Get maximum string length
        self.assertNoRaise(self.feat_r.get_max_length)
        self.assertNoRaise(self.feat_rw.get_max_length)

    def test_set(self):
        # Expectation:
        # 1) Setting a read only feature must raise a VmbFeatureError
        # 2) Setting a read/write must raise VmbFeatureError if the string is
        #    longer than max length
        # 3) Setting a read/write feature must work if string is long enough

        # Ensure Expectation 1
        self.assertRaises(VmbFeatureError, self.feat_r.set, self.feat_r.get())
        self.assertNoRaise(self.feat_rw.set, self.feat_rw.get())

        # Ensure Expectation 2
        old_val = self.feat_rw.get()

        try:
            invalid = 'a' * (self.feat_rw.get_max_length() + 1)
            self.assertRaises(VmbFeatureError, self.feat_rw.set, invalid)

        finally:
            self.feat_rw.set(old_val)

        # Ensure Expectation 3
        try:
            valid = 'a' * (self.feat_rw.get_max_length() - 1)
            self.assertNoRaise(self.feat_rw.set, valid)
            self.assertEqual(valid, self.feat_rw.get())

        finally:
            self.feat_rw.set(old_val)

    def test_set_in_callback(self):
        # Expectation: Setting a value within a Callback must raise a VmbFeatureError

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VmbFeatureError:
                    self.raised = True

                self.event.set()

        try:
            handler = Handler()
            self.feat_rw.register_change_handler(handler)

            self.feat_rw.set(self.feat_rw.get())

            handler.event.wait()

            self.assertTrue(handler.raised)

        finally:
            self.feat_rw.unregister_change_handler(handler)
