import unittest
import threading

from vimba import *
from vimba.feature import *

class TlBaseFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')
        self.cam._open()

        self.height = self.cam.get_feature_by_name('Height')
        self.device_id = self.cam.get_feature_by_name('DeviceID')

    def tearDown(self):
        self.cam._close()
        self.vimba._shutdown()

    def test_get_name(self):
        """Expectation: Return decoded FeatureName """
        self.assertEqual(self.height.get_name(), 'Height')
        self.assertEqual(self.device_id.get_name(), 'DeviceID')

    def test_get_flags(self):
        """Expectation: Return decoded FeatureFlags """
        self.assertEqual(self.height.get_flags(), (FeatureFlags.Read, FeatureFlags.Write))
        self.assertEqual(self.device_id.get_flags(), (FeatureFlags.Read,))

    def test_get_category(self):
        """Expectation: Return decoded category"""
        self.assertEqual(self.height.get_category(), '/ImageFormatControl')
        self.assertEqual(self.device_id.get_category(), '/DeviceControl')

    def test_get_display_name(self):
        """Expectation: Return decoded category"""
        self.assertEqual(self.height.get_display_name(), 'Height')
        self.assertEqual(self.device_id.get_display_name(), 'Device ID')

    def test_get_polling_time(self):
        """Expectation: Return polling time. Only volatile features return
        anything other than zero.
        """
        self.assertEqual(self.height.get_polling_time(), 0)
        self.assertEqual(self.device_id.get_polling_time(), 0)

    def test_get_unit(self):
        """Expectation: If Unit exists, return unit else return ''"""
        self.assertEqual(self.height.get_unit(), '')
        self.assertEqual(self.device_id.get_unit(), '')
        self.assertEqual(self.cam.get_feature_by_name('ExposureTime').get_unit(), 'us')

    def test_get_representation(self):
        """Expectation: Get numeric representation if existing else ''"""
        self.assertEqual(self.height.get_representation(), '')
        self.assertEqual(self.device_id.get_representation(), '')

    def test_get_visibility(self):
        """Expectation: Get UI Visibility"""
        self.assertEqual(self.height.get_visibility(), FeatureVisibility.Beginner)
        self.assertEqual(self.device_id.get_visibility(), FeatureVisibility.Expert)

    def test_get_tooltip(self):
        """Expectation: Get decoded UI tooltip"""
        self.assertEqual(self.height.get_tooltip(), 'Height of the image provided by the device (in pixels).')
        self.assertEqual(self.device_id.get_tooltip(), 'Device Identifier (string).')

    def test_get_description(self):
        """Expectation: Get decoded description"""
        self.assertEqual(self.height.get_description(), 'Height of the image provided by the device (in pixels).')
        self.assertEqual(self.device_id.get_description(), 'Device Identifier (string).')

    def test_get_sfnc_namespace(self):
        """Expectation: Get decoded sfnc namespace"""
        self.assertEqual(self.height.get_sfnc_namespace(), 'Standard')
        self.assertEqual(self.device_id.get_sfnc_namespace(), 'Standard')

    def test_is_streamable(self):
        """Expectation: Streamable features shall return True, others False"""
        self.assertFalse(self.height.is_streamable())
        self.assertFalse(self.device_id.is_streamable())

    def test_has_affected_features(self):
        """Expectation:Features that affect features shall return True, others False"""
        self.assertTrue(self.height.has_affected_features())
        self.assertFalse(self.device_id.has_affected_features())

    def test_has_selected_features(self):
        """Expectation:Features that select features shall return True, others False"""
        self.assertFalse(self.height.has_selected_features())
        self.assertFalse(self.device_id.has_selected_features())

    def test_get_access_mode(self):
        """Expectation: Read/Write Features return (True, True), ReadOnly return (True, False)"""
        self.assertEqual(self.height.get_access_mode(), (True, True))
        self.assertEqual(self.device_id.get_access_mode(), (True, False))

    def test_is_readable(self):
        """Expectation: True if feature grant read access else False"""
        self.assertTrue(self.height.is_readable())
        self.assertTrue(self.device_id.is_readable())

    def test_is_writeable(self):
        """Expectation: True if feature grant write access else False"""
        self.assertTrue(self.height.is_writeable())
        self.assertFalse(self.device_id.is_writeable())

    def test_change_handler(self):
        """Expectation: A given change handler is executed on value change.
        Adding the same handler multiple times shall not lead to multiple executions.
        The same goes for double unregister.
        """
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
        self.height.set(tmp + 1)

        handler.event.wait()

        self.height.unregister_change_handler(handler)
        self.height.unregister_change_handler(handler)

        self.height.set(tmp)

        self.assertEqual(handler.call_cnt, 1)


class TlBoolFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.feat = self.vimba.get_feature_by_name('UsbTLIsPresent')

    def tearDown(self):
        self.vimba._shutdown()

    def test_get_type(self):
        """Expectation: BoolFeature must return BoolFeature on get_type"""
        self.assertEqual(self.feat.get_type(), BoolFeature)

    def test_get(self):
        """Expectation: returns current boolean value."""
        self.assertTrue(self.feat.get())

    def test_set(self):
        """Expectation: Raises invalid Access on non-writeable features.
        Everything else is not testable from FileTL.
        """
        self.assertRaises(VimbaFeatureError, self.feat.set, True)

    def test_runtime_check_failure(self):
        """Expectation: Set must throw TypeError on non-boolean input."""
        self.assertRaises(TypeError, self.feat.set, 'Hi')

class TlCommandFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.feat = self.vimba.get_feature_by_name('ActionCommand')

    def tearDown(self):
        self.vimba._shutdown()

    def test_get_type(self):
        """Expectation: CommandFeature must return CommandFeature on get_type"""
        self.assertEqual(self.feat.get_type(), CommandFeature)


class TlEnumFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')
        self.cam._open()

        self.feat_r = self.cam.get_feature_by_name('DeviceScanType')
        self.feat_rw = self.cam.get_feature_by_name('AcquisitionMode')

    def tearDown(self):
        self.cam._close()
        self.vimba._shutdown()

    def test_get_type(self):
        """Expectation: EnumFeature must return EnumFeature on get_type"""
        self.assertEqual(self.feat_r.get_type(), EnumFeature)
        self.assertEqual(self.feat_rw.get_type(), EnumFeature)

    def test_entry_as_bytes(self):
        """Expectation: Get EnumEntry as encoded byte sequence """
        expected = 'MultiFrame'.encode('utf-8')
        entry = self.feat_rw.get_entry('MultiFrame')

        self.assertEqual(entry.as_bytes(), expected)

    def test_entry_as_int(self):
        """Expectation: Get EnumEntry as int """
        expected = 2
        entry = self.feat_rw.get_entry('MultiFrame')

        self.assertEqual(entry.as_int(), expected)
        self.assertEqual(int(entry), expected)

    def test_entry_as_str(self):
        """Expectation: Get EnumEntry as str """
        expected = 'MultiFrame'
        entry = self.feat_rw.get_entry('MultiFrame')

        self.assertEqual(entry.as_string(), expected)
        self.assertEqual(str(entry), expected)

    def test_entry_as_tuple(self):
        """Expectation: Get EnumEntry as (str, int) """
        expected = ('MultiFrame', 2)

        entry = self.feat_rw.get_entry('MultiFrame')
        self.assertEqual(entry.as_tuple(), expected)

        entry = self.feat_rw.get_entry(2)
        self.assertEqual(entry.as_tuple(), expected)

    def test_get_all_entries(self):
        """Expectation: Get all possible enum entries regardless of the availability"""
        expected = (self.feat_r.get_entry('Areascan'),)
        self.assertEqual(self.feat_r.get_all_entries(), expected)

        expected = (
            self.feat_rw.get_entry('SingleFrame'),
            self.feat_rw.get_entry('MultiFrame'),
            self.feat_rw.get_entry('Continuous')
        )
        self.assertEqual(self.feat_rw.get_all_entries(), expected)

    def test_get_avail_entries(self):
        """Expectation: All returned enum entries must be available"""
        for e in self.feat_r.get_available_entries():
            self.assertTrue(e.is_available())

        for e in self.feat_rw.get_available_entries():
            self.assertTrue(e.is_available())

    def test_get_entry_int(self):
        """Expectation: Lookup a given entry by using an int as key.
        Invalid keys must return VimbaFeatureError.
        """
        expected = self.feat_r.get_all_entries()[0]
        self.assertEqual(self.feat_r.get_entry(int(expected)), expected)

        expected = self.feat_rw.get_all_entries()[1]
        self.assertEqual(self.feat_rw.get_entry(int(expected)), expected)

        self.assertRaises(VimbaFeatureError, self.feat_r.get_entry, -1)
        self.assertRaises(VimbaFeatureError, self.feat_rw.get_entry, -1)

    def test_get_entry_str(self):
        """Expectation: Lookup a given entry by using a str as key.
        Invalid keys must return VimbaFeatureError.
        """
        expected = self.feat_r.get_all_entries()[0]
        self.assertEqual(self.feat_r.get_entry(str(expected)), expected)

        expected = self.feat_rw.get_all_entries()[1]
        self.assertEqual(self.feat_rw.get_entry(str(expected)), expected)

        self.assertRaises(VimbaFeatureError, self.feat_r.get_entry, 'Should be invalid')
        self.assertRaises(VimbaFeatureError, self.feat_rw.get_entry, 'Should be invalid')

    def test_get(self):
        """Expectation: Get must return the current value. If Feature is not readable, it
        Should return InvalidAccess. InvalidAccess is not testable under fileTL
        """
        self.assertNoRaise(self.feat_r.get)
        self.assertNoRaise(self.feat_rw.get)

    def test_set_entry(self):
        """Expectation: Set given enum entry if feature is writable.
        Raises:
        - VimbaFeatureError if enum entry is from other enum feature.
        - VimbaFeatureError if feature is read only
        """

        # Read Only Feature
        entry = self.feat_r.get_all_entries()[0]
        self.assertRaises(VimbaFeatureError, self.feat_r.set, entry)

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, self.feat_rw.get_entry(2))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by setting the feature from the ReadOnly entry.
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, entry)

        finally:
            self.feat_rw.set(old_entry)

    def test_set_str(self):
        """Expectation: Set given enum entry string value if feature is writable.
        Raises:
        - VimbaFeatureError if given string is not associated with this feature.
        - VimbaFeatureError if feature is read only
        """

        # Read Only Feature
        self.assertRaises(VimbaFeatureError, self.feat_r.set, str(self.feat_r.get_entry(0)))

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, str(self.feat_rw.get_entry(2)))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by an invalid enum value
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, 'Hopefully invalid')

        finally:
            self.feat_rw.set(old_entry)

    def test_set_int(self):
        """Expectation: Set given enum entry int value if feature is writable.
        Raises:
        - VimbaFeatureError if given int is not associated with this feature.
        - VimbaFeatureError if feature is read only
        """

        # Read Only Feature
        self.assertRaises(VimbaFeatureError, self.feat_r.set, int(self.feat_r.get_entry(0)))

        # Read/Write Feature
        old_entry = self.feat_rw.get()

        try:
            # Normal operation
            self.assertNoRaise(self.feat_rw.set, int(self.feat_rw.get_entry(2)))
            self.assertEqual(self.feat_rw.get(), self.feat_rw.get_entry(2))

            # Provoke FeatureError by an invalid enum value
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, -23)

        finally:
            self.feat_rw.set(old_entry)

    def test_set_in_callback(self):
        """Expected behavior: A set operation within a change handler must
        Raise a VimbaFeatureError to prevent an endless handler execution.
        """

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VimbaFeatureError:
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

    def test_runtime_check_failure(self):
        """ Expectation: TypeError must raise TypeError if:
        set() is called with non int, str, EnumEntry
        get_entry() is called with non int, str
        """
        self.assertRaises(TypeError, self.feat_r.set, 0.0)
        self.assertRaises(TypeError, self.feat_rw.set, b'bytes')

        self.assertRaises(TypeError, self.feat_r.get_entry, 0.0)
        self.assertRaises(TypeError, self.feat_rw.get_entry, b'bytes')


class TlFloatFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.feat_r = self.vimba.get_feature_by_name('Elapsed')

        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')
        self.cam._open()

        self.feat_rw = self.cam.get_feature_by_name('ExposureTime')

    def tearDown(self):
        self.cam._close()
        self.vimba._shutdown()

    def test_get_type(self):
        """Expectation: FloatFeature returns FloatFeature on get_type."""
        self.assertEqual(self.feat_r.get_type(), FloatFeature)
        self.assertEqual(self.feat_rw.get_type(), FloatFeature)

    def test_get(self):
        """Expectation: Get current value. Raise VimbaFeatureError on non-read access.
        Error is not testable on FileTL.
        """

        # Can't use self.feat_r because its a running counter. Hard to compare
        self.assertEqual(self.feat_rw.get(), 40000.0)

    def test_get_range(self):
        """Expectation: Get value range. Raise VimbaFeatureError on non-read access.
        Error is not testable on FileTL.
        """
        self.assertEqual(self.feat_r.get_range(), (0.0, 1.7976931348623157e+308))
        self.assertEqual(self.feat_rw.get_range(), (1.0, 4294967295.0))

    def test_get_increment(self):
        """Expectation: Get value increment if existing. If this Feature has no
        increment, None is returned. Raise VimbaFeatureError on non-read access.
        Error is not testable on FileTL.
        """
        self.assertEqual(self.feat_r.get_increment(), None)
        self.assertEqual(self.feat_rw.get_increment(), None)

    def test_set(self):
        """Expectation: Set value. Errors:
        VimbaFeatureError if access right are not writable
        VimbaFeatureError if value is out of bounds
        """
        # Read only feature
        self.assertRaises(VimbaFeatureError, self.feat_r.set, 0.0)

        # Read/Write Feature
        old_value = self.feat_rw.get()

        try:
            delta = 0.1

            # Range test
            min_, max_ = self.feat_rw.get_range()

            # Within bounds (no error)
            self.assertNoRaise(self.feat_rw.set, min_)
            self.assertEqual(self.feat_rw.get(), min_)
            self.assertNoRaise(self.feat_rw.set, max_)
            self.assertEqual(self.feat_rw.get(), max_)

            # Out of bounds (must raise)
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, min_ - delta)
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, max_ + delta)

        finally:
            self.feat_rw.set(old_value)

    def test_set_in_callback(self):
        """Expectation: Calling set within change_handler must raise an VimbaFeatureError"""

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VimbaFeatureError:
                    self.raised = True

                self.event.set()

        old_entry = self.feat_rw.get()

        try:
            handler = Handler()
            self.feat_rw.register_change_handler(handler)

            # Trigger change handler and wait for callback execution.
            self.feat_rw.set( self.feat_rw.get())
            handler.event.wait()

            self.assertTrue(handler.raised)

        finally:
            self.feat_rw.unregister_change_handler(handler)
            self.feat_rw.set(old_entry)

    def test_runtime_check_failure(self):
        """Expectation: TypeError must be thrown is param for set in not float"""
        self.assertRaises(TypeError, self.feat_r.set, 'str')
        self.assertRaises(TypeError, self.feat_rw.set, 0)

class TlIntFeatureTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()
        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')
        self.cam._open()

        self.feat_r = self.cam.get_feature_by_name('HeightMax')
        self.feat_rw = self.cam.get_feature_by_name('Height')

    def tearDown(self):
        self.cam._close()
        self.vimba._shutdown()

    def test_get_type(self):
        """Expectation: IntFeature must return IntFeature on get_type"""
        self.assertEqual(self.feat_r.get_type(), IntFeature)
        self.assertEqual(self.feat_rw.get_type(), IntFeature)

    def test_get(self):
        """Expectation: Get current value or Raise VimbaFeatureError if access right are
        not sufficient. FileTL has no features with invalid access rights. Therefore not testable.
        """
        self.assertEqual(self.feat_r.get(), 4096)
        self.assertEqual(self.feat_rw.get(), 768)

    def test_get_range(self):
        """Expectation: Get range of accepted values or Raise VimbaFeatureError if access right are
        not sufficient. FileTL has no features with invalid access rights. Therefore not testable.
        """
        self.assertEqual(self.feat_r.get_range(), (0, 4294967295))
        self.assertEqual(self.feat_rw.get_range(), (1, 4096))

    def test_get_increment(self):
        """Expectation: Get step between valid values or Raise VimbaFeatureError if access right are
        not sufficient. FileTL has no features with invalid access rights. Therefore not testable.
        """
        self.assertEqual(self.feat_r.get_increment(), 1)
        self.assertEqual(self.feat_rw.get_increment(), 1)

    def test_set(self):
        """Expectation: Set value or raise VimbaFeatureError under the following conditions.
        1) Invalid Access Rights
        2) Misaligned value: Not Testable in FileTL because all increments are +1
        3) Out-of-bounds Access
        """
        # Read only feature
        self.assertRaises(VimbaFeatureError, self.feat_r.set, 0)

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
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, min_ - inc)
            self.assertRaises(VimbaFeatureError, self.feat_rw.set, max_ + inc)

        finally:
            self.feat_rw.set(old_value)

    def test_set_in_callback(self):
        """Expectation: Setting a value within a Callback must raise a VimbaFeatureError"""

        class Handler:
            def __init__(self):
                self.raised = False
                self.event = threading.Event()

            def __call__(self, feat):
                try:
                    feat.set(feat.get())

                except VimbaFeatureError:
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

    def test_runtime_check_failure(self):
        """Expectation: set must raise TypeError on any non int param"""
        self.assertRaises(TypeError, self.feat_r.set, 0.0)
        self.assertRaises(TypeError, self.feat_rw.set, 'no int')