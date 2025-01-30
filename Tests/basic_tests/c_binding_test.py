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
import ctypes
import os
import sys

from vmbpy.c_binding import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class VmbCommonTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_decode_cstr_behavior(self):
        # Expected Behavior:
        #    c_char_p() == ''
        #    c_char_p(b'foo') == 'foo'

        expected = ''
        actual = decode_cstr(ctypes.c_char_p())
        self.assertEqual(expected, actual)

        expected = 'test'
        actual = decode_cstr(ctypes.c_char_p(b'test').value)
        self.assertEqual(expected, actual)

    def test_decode_flags_zero(self):
        # Expected Behavior: In case no bytes are set the
        #    zero value of the Flag Enum must be returned

        expected = (VmbFeatureFlags.None_,)
        actual = decode_flags(VmbFeatureFlags, 0)
        self.assertEqual(expected, actual)

    def test_decode_flags_some(self):
        # Expected Behavior: Given Integer must be decided correctly.
        # the order of the fields does not matter for this test.

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


class CBindingVmbCTypesTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_enum_vmb_error(self):
        self.assertEqual(VmbError.Success, 0)
        self.assertEqual(VmbError.InternalFault, -1)
        self.assertEqual(VmbError.ApiNotStarted, -2)
        self.assertEqual(VmbError.NotFound, -3)
        self.assertEqual(VmbError.BadHandle, -4)
        self.assertEqual(VmbError.DeviceNotOpen, -5)
        self.assertEqual(VmbError.InvalidAccess, -6)
        self.assertEqual(VmbError.BadParameter, -7)
        self.assertEqual(VmbError.StructSize, -8)
        self.assertEqual(VmbError.MoreData, -9)
        self.assertEqual(VmbError.WrongType, -10)
        self.assertEqual(VmbError.InvalidValue, -11)
        self.assertEqual(VmbError.Timeout, -12)
        self.assertEqual(VmbError.Other, -13)
        self.assertEqual(VmbError.Resources, -14)
        self.assertEqual(VmbError.InvalidCall, -15)
        self.assertEqual(VmbError.NoTL, -16)
        self.assertEqual(VmbError.NotImplemented_, -17)
        self.assertEqual(VmbError.NotSupported, -18)
        self.assertEqual(VmbError.Incomplete, -19)
        self.assertEqual(VmbError.IO, -20)

    def test_enum_vmb_pixel_format(self):
        self.assertEqual(VmbPixelFormat.Mono8, 0x01080001)
        self.assertEqual(VmbPixelFormat.Mono10, 0x01100003)
        self.assertEqual(VmbPixelFormat.Mono10p, 0x010A0046)
        self.assertEqual(VmbPixelFormat.Mono12, 0x01100005)
        self.assertEqual(VmbPixelFormat.Mono12Packed, 0x010C0006)
        self.assertEqual(VmbPixelFormat.Mono12p, 0x010C0047)
        self.assertEqual(VmbPixelFormat.Mono14, 0x01100025)
        self.assertEqual(VmbPixelFormat.Mono16, 0x01100007)
        self.assertEqual(VmbPixelFormat.BayerGR8, 0x01080008)
        self.assertEqual(VmbPixelFormat.BayerRG8, 0x01080009)
        self.assertEqual(VmbPixelFormat.BayerGB8, 0x0108000A)
        self.assertEqual(VmbPixelFormat.BayerBG8, 0x0108000B)
        self.assertEqual(VmbPixelFormat.BayerGR10, 0x0110000C)
        self.assertEqual(VmbPixelFormat.BayerRG10, 0x0110000D)
        self.assertEqual(VmbPixelFormat.BayerGB10, 0x0110000E)
        self.assertEqual(VmbPixelFormat.BayerBG10, 0x0110000F)
        self.assertEqual(VmbPixelFormat.BayerGR12, 0x01100010)
        self.assertEqual(VmbPixelFormat.BayerRG12, 0x01100011)
        self.assertEqual(VmbPixelFormat.BayerGB12, 0x01100012)
        self.assertEqual(VmbPixelFormat.BayerBG12, 0x01100013)
        self.assertEqual(VmbPixelFormat.BayerGR12Packed, 0x010C002A)
        self.assertEqual(VmbPixelFormat.BayerRG12Packed, 0x010C002B)
        self.assertEqual(VmbPixelFormat.BayerGB12Packed, 0x010C002C)
        self.assertEqual(VmbPixelFormat.BayerBG12Packed, 0x010C002D)
        self.assertEqual(VmbPixelFormat.BayerGR10p, 0x010A0056)
        self.assertEqual(VmbPixelFormat.BayerRG10p, 0x010A0058)
        self.assertEqual(VmbPixelFormat.BayerGB10p, 0x010A0054)
        self.assertEqual(VmbPixelFormat.BayerBG10p, 0x010A0052)
        self.assertEqual(VmbPixelFormat.BayerGR12p, 0x010C0057)
        self.assertEqual(VmbPixelFormat.BayerRG12p, 0x010C0059)
        self.assertEqual(VmbPixelFormat.BayerGB12p, 0x010C0055)
        self.assertEqual(VmbPixelFormat.BayerBG12p, 0x010C0053)
        self.assertEqual(VmbPixelFormat.BayerGR16, 0x0110002E)
        self.assertEqual(VmbPixelFormat.BayerRG16, 0x0110002F)
        self.assertEqual(VmbPixelFormat.BayerGB16, 0x01100030)
        self.assertEqual(VmbPixelFormat.BayerBG16, 0x01100031)
        self.assertEqual(VmbPixelFormat.Rgb8, 0x02180014)
        self.assertEqual(VmbPixelFormat.Bgr8, 0x02180015)
        self.assertEqual(VmbPixelFormat.Rgb10, 0x02300018)
        self.assertEqual(VmbPixelFormat.Bgr10, 0x02300019)
        self.assertEqual(VmbPixelFormat.Rgb12, 0x0230001A)
        self.assertEqual(VmbPixelFormat.Bgr12, 0x0230001B)
        self.assertEqual(VmbPixelFormat.Rgb14, 0x0230005E)
        self.assertEqual(VmbPixelFormat.Bgr14, 0x0230004A)
        self.assertEqual(VmbPixelFormat.Rgb16, 0x02300033)
        self.assertEqual(VmbPixelFormat.Bgr16, 0x0230004B)
        self.assertEqual(VmbPixelFormat.Argb8, 0x02200016)
        self.assertEqual(VmbPixelFormat.Rgba8, 0x02200016)
        self.assertEqual(VmbPixelFormat.Bgra8, 0x02200017)
        self.assertEqual(VmbPixelFormat.Rgba10, 0x0240005F)
        self.assertEqual(VmbPixelFormat.Bgra10, 0x0240004C)
        self.assertEqual(VmbPixelFormat.Rgba12, 0x02400061)
        self.assertEqual(VmbPixelFormat.Bgra12, 0x0240004E)
        self.assertEqual(VmbPixelFormat.Rgba14, 0x02400063)
        self.assertEqual(VmbPixelFormat.Bgra14, 0x02400050)
        self.assertEqual(VmbPixelFormat.Rgba16, 0x02400064)
        self.assertEqual(VmbPixelFormat.Bgra16, 0x02400051)
        self.assertEqual(VmbPixelFormat.Yuv411, 0x020C001E)
        self.assertEqual(VmbPixelFormat.Yuv422, 0x0210001F)
        self.assertEqual(VmbPixelFormat.Yuv444, 0x02180020)
        self.assertEqual(VmbPixelFormat.YCbCr411_8_CbYYCrYY, 0x020C003C)
        self.assertEqual(VmbPixelFormat.YCbCr422_8_CbYCrY, 0x02100043)
        self.assertEqual(VmbPixelFormat.YCbCr8_CbYCr, 0x0218003A)

    def test_enum_vmb_interface(self):
        self.assertEqual(VmbTransportLayer.Unknown, 0)
        self.assertEqual(VmbTransportLayer.GEV, 1)
        self.assertEqual(VmbTransportLayer.CL, 2)
        self.assertEqual(VmbTransportLayer.IIDC, 3)
        self.assertEqual(VmbTransportLayer.UVC, 4)
        self.assertEqual(VmbTransportLayer.CXP, 5)
        self.assertEqual(VmbTransportLayer.CLHS, 6)
        self.assertEqual(VmbTransportLayer.U3V, 7)
        self.assertEqual(VmbTransportLayer.Ethernet, 8)
        self.assertEqual(VmbTransportLayer.PCI, 9)
        self.assertEqual(VmbTransportLayer.Custom, 10)
        self.assertEqual(VmbTransportLayer.Mixed, 11)

    def test_enum_vmb_access_mode(self):
        self.assertEqual(VmbAccessMode.None_, 0)
        self.assertEqual(VmbAccessMode.Full, 1)
        self.assertEqual(VmbAccessMode.Read, 2)
        self.assertEqual(VmbAccessMode.Unknown, 4)
        self.assertEqual(VmbAccessMode.Exclusive, 8)

    def test_enum_vmb_feature_data(self):
        self.assertEqual(VmbFeatureData.Unknown, 0)
        self.assertEqual(VmbFeatureData.Int, 1)
        self.assertEqual(VmbFeatureData.Float, 2)
        self.assertEqual(VmbFeatureData.Enum, 3)
        self.assertEqual(VmbFeatureData.String, 4)
        self.assertEqual(VmbFeatureData.Bool, 5)
        self.assertEqual(VmbFeatureData.Command, 6)
        self.assertEqual(VmbFeatureData.Raw, 7)
        self.assertEqual(VmbFeatureData.None_, 8)

    def test_enum_vmb_feature_persist(self):
        self.assertEqual(VmbFeaturePersist.All, 0)
        self.assertEqual(VmbFeaturePersist.Streamable, 1)
        self.assertEqual(VmbFeaturePersist.NoLUT, 2)

    def test_enum_vmb_feature_visibility(self):
        self.assertEqual(VmbFeatureVisibility.Unknown, 0)
        self.assertEqual(VmbFeatureVisibility.Beginner, 1)
        self.assertEqual(VmbFeatureVisibility.Expert, 2)
        self.assertEqual(VmbFeatureVisibility.Guru, 3)
        self.assertEqual(VmbFeatureVisibility.Invisible, 4)

    def test_enum_vmb_feature_flags(self):
        self.assertEqual(VmbFeatureFlags.None_, 0)
        self.assertEqual(VmbFeatureFlags.Read, 1)
        self.assertEqual(VmbFeatureFlags.Write, 2)
        self.assertEqual(VmbFeatureFlags.Volatile, 8)
        self.assertEqual(VmbFeatureFlags.ModifyWrite, 16)

    def test_enum_vmb_frame_status(self):
        self.assertEqual(VmbFrameStatus.Complete, 0)
        self.assertEqual(VmbFrameStatus.Incomplete, -1)
        self.assertEqual(VmbFrameStatus.TooSmall, -2)
        self.assertEqual(VmbFrameStatus.Invalid, -3)

    def test_enum_vmd_frame_flags(self):
        self.assertEqual(VmbFrameFlags.None_, 0)
        self.assertEqual(VmbFrameFlags.Dimension, 1)
        self.assertEqual(VmbFrameFlags.Offset, 2)
        self.assertEqual(VmbFrameFlags.FrameID, 4)
        self.assertEqual(VmbFrameFlags.Timestamp, 8)


class VmbCTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_call_vmb_c_valid(self):
        # Expectation for valid call: No exceptions, no errors
        expected_ver_info = (0, 1, 0)
        ver_info = VmbVersionInfo()

        call_vmb_c('VmbVersionQuery', byref(ver_info), sizeof(ver_info))

        ver_info = (ver_info.major, ver_info.minor, ver_info.patch)

        # Not an actual check for compatibility. Just make sure a sensible value was filled
        self.assertGreaterEqual(ver_info, expected_ver_info)

    def test_loaded_and_expected_vmbc_version_match(self):
        # Expectation: Loaded VmbC Version matches what is expected in vmb_c.py
        expected_version = tuple(map(int, EXPECTED_VMB_C_VERSION.split('.')))
        v = VmbVersionInfo()

        call_vmb_c('VmbVersionQuery', byref(v), sizeof(v))

        loaded_version = (v.major, v.minor, v.patch)

        # Note: A version mismatch does not automatically mean that VmbC and VmbPy are incompatible.
        # The minor and patch version may be greater than the defined expected version. This test
        # case will still fail to indicate a *possible* incompatibility
        self.assertEqual(expected_version, loaded_version)

    def test_call_vmb_c_invalid_func_name(self):
        # Expectation: An invalid function name must throw an AttributeError

        ver_info = VmbVersionInfo()
        self.assertRaises(AttributeError, call_vmb_c, 'VmbVersionQuer', byref(ver_info),
                          sizeof(ver_info))

    def test_call_vmb_c_invalid_arg_number(self):
        # Expectation: Invalid number of arguments with sane types.
        # must lead to TypeErrors

        ver_info = VmbVersionInfo()
        self.assertRaises(TypeError, call_vmb_c, 'VmbVersionQuery', byref(ver_info))

    def test_call_vmb_c_invalid_arg_type(self):
        # Expectation: Arguments with invalid types must lead to TypeErrors

        # Call with unexpected base types
        self.assertRaises(ctypes.ArgumentError, call_vmb_c, 'VmbVersionQuery', 0, 'hi')

        # Call with valid ctypes used wrongly
        ver_info = VmbVersionInfo()
        self.assertRaises(ctypes.ArgumentError, call_vmb_c, 'VmbVersionQuery', byref(ver_info),
                          ver_info)

    def test_call_vmb_c_exception(self):
        # Expectation: Errors returned from the C-Layer must be mapped
        # to a special Exception Type call VmbCError. This error must
        # contain the returned Error Code from the failed C-Call.

        # VmbVersionQuery has two possible Errors (taken from VmbC.h):
        # - VmbErrorStructSize:    The given struct size is not valid for this version of the API
        # - VmbErrorBadParameter:  If "pVersionInfo" is NULL.

        ver_info = VmbVersionInfo()

        try:
            call_vmb_c('VmbVersionQuery', byref(ver_info), sizeof(ver_info) - 1)
            self.fail("Previous call must raise Exception.")

        except VmbCError as e:
            self.assertEqual(e.get_error_code(), VmbError.StructSize)

        try:
            call_vmb_c('VmbVersionQuery', None, sizeof(ver_info))
            self.fail("Previous call must raise Exception.")

        except VmbCError as e:
            self.assertEqual(e.get_error_code(), VmbError.BadParameter)


class ImageTransformTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_call_vmb_image_transform_valid(self):
        # Expectation for valid call: No exceptions, no errors
        v = VmbUint32()
        self.assertEqual(v.value, 0)

        call_vmb_image_transform('VmbGetImageTransformVersion', byref(v))

        self.assertNotEqual(v.value, 0)

    def test_loaded_and_expected_vmbimagetransform_versions_match(self):
        # Expectation: Loaded VmbImageTransform Version matches what is expected in
        # vmb_image_transform.py
        expected_version = tuple(map(int, EXPECTED_VMB_IMAGE_TRANSFORM_VERSION.split('.')))
        v = VmbUint32()

        call_vmb_image_transform('VmbGetImageTransformVersion', byref(v))

        loaded_version = ((v.value >> 24 & 0xff), (v.value >> 16 & 0xff))

        # Note: A version mismatch does not automatically mean that VmbImageTransform and VmbPy are
        # incompatible. The minor version may be greater than the defined expected version. This
        # test case will still fail to indicate a *possible* incompatibility
        self.assertEqual(expected_version, loaded_version)

    def test_call_vmb_c_invalid_func_name(self):
        # Expectation: An invalid function name must throw an AttributeError
        v = VmbUint32()
        self.assertRaises(AttributeError, call_vmb_image_transform, 'DoesNotExist', byref(v))

    def test_call_vmb_c_invalid_arg_number(self):
        # Expectation: Invalid number of arguments with sane types must lead to TypeErrors
        self.assertRaises(TypeError, call_vmb_image_transform, 'VmbGetImageTransformVersion')

    def test_call_vmb_c_invalid_arg_type(self):
        # Expectation: Arguments with invalid types must lead to TypeErrors
        self.assertRaises(ctypes.ArgumentError,
                          call_vmb_image_transform,
                          'VmbGetImageTransformVersion',
                          VmbDouble())
        self.assertRaises(ctypes.ArgumentError,
                          call_vmb_image_transform,
                          'VmbGetImageTransformVersion',
                          0)
        self.assertRaises(ctypes.ArgumentError,
                          call_vmb_image_transform,
                          'VmbGetImageTransformVersion',
                          'invalid')

    def test_call_vmb_c_exception(self):
        # Expectation: Failed operations must raise a VmbCError
        self.assertRaises(VmbCError,
                          call_vmb_image_transform,
                          'VmbGetImageTransformVersion',
                          None)
