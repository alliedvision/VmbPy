import unittest
import ctypes

from vimba.c_binding import *


class CBindingUtilTest(unittest.TestCase):
    def test_decode_cstr_behavior(self):
        """ Expected Behavior:
            c_char_p() == ''
            c_char_p(b'foo') == 'foo'
        """

        expected = ''
        actual = decode_cstr(ctypes.c_char_p())
        self.assertEqual(expected, actual)

        expected = 'test'
        actual = decode_cstr(ctypes.c_char_p(b'test').value)
        self.assertEqual(expected, actual)

    def test_decode_flags_zero(self):
        """ Expected Behavior: In case no bytes are set the
            zero value of the Flag Enum must be returned
        """

        expected = (VmbFeatureFlags.None_,)
        actual = decode_flags(VmbFeatureFlags, 0)
        self.assertEqual(expected, actual)

    def test_decode_flags_some(self):
        """ Expected Behavior: Given Integer must be decided correctly.
            the order of the fields does not matter for this test.
        """
        expected = (
            VmbFeatureFlags.Write,
            VmbFeatureFlags.Read,
            VmbFeatureFlags.ModifyWrite
        )

        input_data = 0

        for val in expected:
            input_data |= int(val)

        actual = decode_flags(VmbFeatureFlags, input_data)

        # Convert both collections into a list and sort it.
        # That way order doesn't matter. It is only important that values are
        # decoded correctly.
        self.assertEqual(list(expected).sort(), list(actual).sort())




