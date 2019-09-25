import unittest
from vimba.c_binding import *


class CBindingTypesTest(unittest.TestCase):
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
        self.assertEqual(VmbInterface.Unknown, 0)
        self.assertEqual(VmbInterface.Firewire, 1)
        self.assertEqual(VmbInterface.Ethernet, 2)
        self.assertEqual(VmbInterface.Usb, 3)
        self.assertEqual(VmbInterface.CL, 4)
        self.assertEqual(VmbInterface.CSI2, 5)

    def test_enum_vmb_access_mode(self):
        self.assertEqual(VmbAccessMode.None_, 0)
        self.assertEqual(VmbAccessMode.Full, 1)
        self.assertEqual(VmbAccessMode.Read, 2)
        self.assertEqual(VmbAccessMode.Config, 4)
        self.assertEqual(VmbAccessMode.Lite, 8)

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