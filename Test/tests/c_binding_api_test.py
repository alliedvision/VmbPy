import unittest
import ctypes

from vimba.c_binding import *


class CBindingApiTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_call_vimba_c_valid(self):
        """ Expectation for valid call: No exceptions, no errors """
        expected_ver_info = (1, 8, 0)
        ver_info = VmbVersionInfo()

        call_vimba_c_func('VmbVersionQuery', byref(ver_info), sizeof(ver_info))

        ver_info = (ver_info.major, ver_info.minor, ver_info.patch)

        self.assertEqual(expected_ver_info, ver_info)

    def test_call_vimba_c_invalid_func_name(self):
        """ Expectation: An invalid function name must throw an AttributeError """

        ver_info = VmbVersionInfo()
        self.assertRaises(AttributeError, call_vimba_c_func, 'VmbVersionQuer', byref(ver_info), sizeof(ver_info))

    def test_call_vimba_c_invalid_arg_number(self):
        """ Expectation: Invalid number of arguments with sane types.
            must lead to TypeErrors
        """

        ver_info = VmbVersionInfo()
        self.assertRaises(TypeError, call_vimba_c_func, 'VmbVersionQuery', byref(ver_info))

    def test_call_vimba_c_invalid_arg_type(self):
        """ Expectation: Arguments with invalid types must lead to TypeErrors """

        # Call with unexpected base types
        self.assertRaises(ctypes.ArgumentError, call_vimba_c_func, 'VmbVersionQuery', 0, 'hi')

        # Call with valid ctypes used wrongly
        ver_info = VmbVersionInfo()
        self.assertRaises(ctypes.ArgumentError, call_vimba_c_func, 'VmbVersionQuery', byref(ver_info), ver_info)

    def test_call_vimba_c_exception(self):
        """ Expectation: Errors returned from the C-Layer must be mapped
            to a special Exception Type call VimbaCError. This error must
            contain the returned Error Code from the failed C-Call.
        """

        # VmbVersionQuery has two possible Errors (taken from VimbaC.h):
        # - VmbErrorStructSize:    The given struct size is not valid for this version of the API
        # - VmbErrorBadParameter:  If "pVersionInfo" is NULL.

        ver_info = VmbVersionInfo()

        try:
            call_vimba_c_func('VmbVersionQuery', byref(ver_info), sizeof(ver_info) - 1)
            self.fail("Previous call must raise Exception.")

        except VimbaCError as e:
            self.assertEqual(e.get_error_code(), VmbError.StructSize)

        try:
            call_vimba_c_func('VmbVersionQuery', None, sizeof(ver_info))
            self.fail("Previous call must raise Exception.")

        except VimbaCError as e:
            self.assertEqual(e.get_error_code(), VmbError.BadParameter)

