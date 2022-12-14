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
import enum
from typing import Tuple

from .vmb_c import (VmbAccessMode, VmbFeatureFlags, VmbFeaturePersist, VmbFeatureVisibility,
                    VmbFrameStatus, VmbModulePersistFlags, VmbTransportLayer)
from .vmb_image_transform import PIXEL_FORMAT_CONVERTIBILITY_MAP, VmbDebayerMode, VmbPixelFormat

__all__ = [
    'AccessMode',
    'Debayer',
    'FeatureFlags',
    'FeatureVisibility',
    'FrameStatus',
    'PersistType',
    'ModulePersistFlags',
    'PixelFormat',
    'TransportLayerType'
]


class AccessMode(enum.IntEnum):
    """Enum specifying all available camera access modes.

    Enum values:
        None_     - No access.
        Full      - Read and write access. Use this mode to configure the camera features and
                    to acquire images (Camera Link cameras: configuration only).
        Read      - Read-only access. Setting features is not possible.
        Unknown   - Access type unknown.
        Exclusive - Read and write access without permitting access for other consumers.
    """
    None_ = VmbAccessMode.None_
    Full = VmbAccessMode.Full
    Read = VmbAccessMode.Read
    Unknown = VmbAccessMode.Unknown
    Exclusive = VmbAccessMode.Exclusive


class Debayer(enum.IntEnum):
    """Enum specifying debayer modes.

    Enum values:
        Mode2x2    - 2x2 with green averaging (this is the default if no debayering algorithm
                     is added as transformation option).
        Mode3x3    - 3x3 with equal green weighting per line (8-bit images only).
        ModeLCAA   - Debayering with horizontal local color anti-aliasing (8-bit images only).
        ModeLCAAV  - Debayering with horizontal and vertical local color anti-aliasing
        (            8-bit images only).
        ModeYuv422 - Debayering with YUV422-alike sub-sampling (8-bit images only).
    """
    Mode2x2 = VmbDebayerMode.Mode_2x2
    Mode3x3 = VmbDebayerMode.Mode_3x3
    ModeLCAA = VmbDebayerMode.Mode_LCAA
    ModeLCAAV = VmbDebayerMode.Mode_LCAAV
    ModeYuv422 = VmbDebayerMode.Mode_YUV422

    def __str__(self):
        return 'DebayerMode.{}'.format(self._name_)

    def __repr__(self):
        return str(self)


class FeatureFlags(enum.IntEnum):
    """Enumeration specifying additional information on the feature.

    Enumeration values:
        None_       - No additional information is provided
        Read        - Static info about read access.
        Write       - Static info about write access.
        Volatile    - Value may change at any time
        ModifyWrite - Value may change after a write
    """

    None_ = VmbFeatureFlags.None_
    Read = VmbFeatureFlags.Read
    Write = VmbFeatureFlags.Write
    Volatile = VmbFeatureFlags.Volatile
    ModifyWrite = VmbFeatureFlags.ModifyWrite


class FeatureVisibility(enum.IntEnum):
    """Enumeration specifying UI feature visibility.

    Enumeration values:
        Unknown   - Feature visibility is not known
        Beginner  - Feature is visible in feature list (beginner level)
        Expert    - Feature is visible in feature list (expert level)
        Guru      - Feature is visible in feature list (guru level)
        Invisible - Feature is not visible in feature listSu
    """

    Unknown = VmbFeatureVisibility.Unknown
    Beginner = VmbFeatureVisibility.Beginner
    Expert = VmbFeatureVisibility.Expert
    Guru = VmbFeatureVisibility.Guru
    Invisible = VmbFeatureVisibility.Invisible


class FrameStatus(enum.IntEnum):
    """Enum specifying the current status of internal Frame data.

    Enum values:
        Complete   - Frame data is complete without errors.
        Incomplete - Frame could not be filled to the end.
        TooSmall   - Frame buffer was too small.
        Invalid    - Frame buffer was invalid.
    """

    Complete = VmbFrameStatus.Complete
    Incomplete = VmbFrameStatus.Incomplete
    TooSmall = VmbFrameStatus.TooSmall
    Invalid = VmbFrameStatus.Invalid


class PersistType(enum.IntEnum):
    """Persistence Type for camera configuration storing and loading.
    Enum values:
        All        - Save all features to XML, including look-up tables (if possible)
        Streamable - Save only features marked as streamable, excluding look-up tables
        NoLUT      - Save all features except look-up tables
    """
    All = VmbFeaturePersist.All
    Streamable = VmbFeaturePersist.Streamable
    NoLUT = VmbFeaturePersist.NoLUT


class ModulePersistFlags(enum.IntFlag):
    """
    Parameters determining the operation mode of VmbSettingsSave and VmbSettingsLoad

        None_          - Persist/Load features for no module
        TransportLayer - Persist/Load the transport layer features
        Interface      - Persist/Load the interface features
        RemoteDevice   - Persist/Load the remote device features
        LocalDevice    - Persist/Load the local device features
        Streams        - Persist/Load the features of stream modules
        All            - Persist/Load features for all modules
    """
    None_ = VmbModulePersistFlags.None_
    TransportLayer = VmbModulePersistFlags.TransportLayer
    Interface = VmbModulePersistFlags.Interface
    RemoteDevice = VmbModulePersistFlags.RemoteDevice
    LocalDevice = VmbModulePersistFlags.LocalDevice
    Streams = VmbModulePersistFlags.Streams
    All = VmbModulePersistFlags.All

    def __str__(self):
        return self._name_


class PixelFormat(enum.IntEnum):
    """Enum specifying all PixelFormats. Note: Not all Cameras support all Pixelformats.

    Mono formats:
        Mono8        - Monochrome, 8 bits (PFNC:Mono8)
        Mono10       - Monochrome, 10 bits in 16 bits (PFNC:Mono10)
        Mono10p      - Monochrome, 4x10 bits continuously packed in 40 bits
                       (PFNC:Mono10p)
        Mono12       - Monochrome, 12 bits in 16 bits (PFNC:Mono12)
        Mono12Packed - Monochrome, 2x12 bits in 24 bits (GEV:Mono12Packed)
        Mono12p      - Monochrome, 2x12 bits continuously packed in 24 bits
                       (PFNC:Mono12p)
        Mono14       - Monochrome, 14 bits in 16 bits (PFNC:Mono14)
        Mono16       - Monochrome, 16 bits (PFNC:Mono16)

    Bayer formats:
        BayerGR8        - Bayer-color, 8 bits, starting with GR line
                          (PFNC:BayerGR8)
        BayerRG8        - Bayer-color, 8 bits, starting with RG line
                          (PFNC:BayerRG8)
        BayerGB8        - Bayer-color, 8 bits, starting with GB line
                          (PFNC:BayerGB8)
        BayerBG8        - Bayer-color, 8 bits, starting with BG line
                          (PFNC:BayerBG8)
        BayerGR10       - Bayer-color, 10 bits in 16 bits, starting with GR
                          line (PFNC:BayerGR10)
        BayerRG10       - Bayer-color, 10 bits in 16 bits, starting with RG
                          line (PFNC:BayerRG10)
        BayerGB10       - Bayer-color, 10 bits in 16 bits, starting with GB
                          line (PFNC:BayerGB10)
        BayerBG10       - Bayer-color, 10 bits in 16 bits, starting with BG
                          line (PFNC:BayerBG10)
        BayerGR12       - Bayer-color, 12 bits in 16 bits, starting with GR
                          line (PFNC:BayerGR12)
        BayerRG12       - Bayer-color, 12 bits in 16 bits, starting with RG
                          line (PFNC:BayerRG12)
        BayerGB12       - Bayer-color, 12 bits in 16 bits, starting with GB
                          line (PFNC:BayerGB12)
        BayerBG12       - Bayer-color, 12 bits in 16 bits, starting with BG
                          line (PFNC:BayerBG12)
        BayerGR12Packed - Bayer-color, 2x12 bits in 24 bits, starting with GR
                          line (GEV:BayerGR12Packed)
        BayerRG12Packed - Bayer-color, 2x12 bits in 24 bits, starting with RG
                          line (GEV:BayerRG12Packed)
        BayerGB12Packed - Bayer-color, 2x12 bits in 24 bits, starting with GB
                          line (GEV:BayerGB12Packed)
        BayerBG12Packed - Bayer-color, 2x12 bits in 24 bits, starting with BG
                          line (GEV:BayerBG12Packed)
        BayerGR10p      - Bayer-color, 4x10 bits continuously packed in 40
                          bits, starting with GR line (PFNC:BayerGR10p)
        BayerRG10p      - Bayer-color, 4x10 bits continuously packed in 40
                          bits, starting with RG line (PFNC:BayerRG10p)
        BayerGB10p      - Bayer-color, 4x10 bits continuously packed in 40
                          bits, starting with GB line (PFNC:BayerGB10p)
        BayerBG10p      - Bayer-color, 4x10 bits continuously packed in 40
                          bits, starting with BG line (PFNC:BayerBG10p)
        BayerGR12p      - Bayer-color, 2x12 bits continuously packed in 24
                          bits, starting with GR line (PFNC:BayerGR12p)
        BayerRG12p      - Bayer-color, 2x12 bits continuously packed in 24
                          bits, starting with RG line (PFNC:BayerRG12p)
        BayerGB12p      - Bayer-color, 2x12 bits continuously packed in 24
                          bits, starting with GB line (PFNC:BayerGB12p)
        BayerBG12p      - Bayer-color, 2x12 bits continuously packed in 24
                          bits, starting with BG line (PFNC:BayerBG12p)
        BayerGR16       - Bayer-color, 16 bits, starting with GR line
                          (PFNC:BayerGR16)
        BayerRG16       - Bayer-color, 16 bits, starting with RG line
                          (PFNC:BayerRG16)
        BayerGB16       - Bayer-color, 16 bits, starting with GB line
                          (PFNC:BayerGB16)
        BayerBG16       - Bayer-color, 16 bits, starting with BG line
                          (PFNC:BayerBG16)

    RGB formats:
        Rgb8  - RGB, 8 bits x 3 (PFNC:RGB8)
        Bgr8  - BGR, 8 bits x 3 (PFNC:Bgr8)
        Rgb10 - RGB, 10 bits in 16 bits x 3 (PFNC:RGB10)
        Bgr10 - BGR, 10 bits in 16 bits x 3 (PFNC:BGR10)
        Rgb12 - RGB, 12 bits in 16 bits x 3 (PFNC:RGB12)
        Bgr12 - BGR, 12 bits in 16 bits x 3 (PFNC:BGR12)
        Rgb14 - RGB, 14 bits in 16 bits x 3 (PFNC:RGB14)
        Bgr14 - BGR, 14 bits in 16 bits x 3 (PFNC:BGR14)
        Rgb16 - RGB, 16 bits x 3 (PFNC:RGB16)
        Bgr16 - BGR, 16 bits x 3 (PFNC:BGR16)

    RGBA formats:
        Argb8  - ARGB, 8 bits x 4 (PFNC:RGBa8)
        Rgba8  - RGBA, 8 bits x 4, legacy name
        Bgra8  - BGRA, 8 bits x 4 (PFNC:BGRa8)
        Rgba10 - RGBA, 10 bits in 16 bits x 4
        Bgra10 - BGRA, 10 bits in 16 bits x 4
        Rgba12 - RGBA, 12 bits in 16 bits x 4
        Bgra12 - BGRA, 12 bits in 16 bits x 4
        Rgba14 - RGBA, 14 bits in 16 bits x 4
        Bgra14 - BGRA, 14 bits in 16 bits x 4
        Rgba16 - RGBA, 16 bits x 4
        Bgra16 - BGRA, 16 bits x 4

    YUV/YCbCr formats:
        Yuv411              -  YUV 411 with 8 bits (GEV:YUV411Packed)
        Yuv422              -  YUV 422 with 8 bits (GEV:YUV422Packed)
        Yuv444              -  YUV 444 with 8 bits (GEV:YUV444Packed)
        YCbCr411_8_CbYYCrYY -  Y´CbCr 411 with 8 bits
                               (PFNC:YCbCr411_8_CbYYCrYY) - identical to Yuv411
        YCbCr422_8_CbYCrY   -  Y´CbCr 422 with 8 bits
                               (PFNC:YCbCr422_8_CbYCrY) - identical to Yuv422
        YCbCr8_CbYCr        -  Y´CbCr 444 with 8 bits
                               (PFNC:YCbCr8_CbYCr) - identical to Yuv444
    """
    # Mono Formats
    Mono8 = VmbPixelFormat.Mono8
    Mono10 = VmbPixelFormat.Mono10
    Mono10p = VmbPixelFormat.Mono10p
    Mono12 = VmbPixelFormat.Mono12
    Mono12Packed = VmbPixelFormat.Mono12Packed
    Mono12p = VmbPixelFormat.Mono12p
    Mono14 = VmbPixelFormat.Mono14
    Mono16 = VmbPixelFormat.Mono16

    # Bayer Formats
    BayerGR8 = VmbPixelFormat.BayerGR8
    BayerRG8 = VmbPixelFormat.BayerRG8
    BayerGB8 = VmbPixelFormat.BayerGB8
    BayerBG8 = VmbPixelFormat.BayerBG8
    BayerGR10 = VmbPixelFormat.BayerGR10
    BayerRG10 = VmbPixelFormat.BayerRG10
    BayerGB10 = VmbPixelFormat.BayerGB10
    BayerBG10 = VmbPixelFormat.BayerBG10
    BayerGR12 = VmbPixelFormat.BayerGR12
    BayerRG12 = VmbPixelFormat.BayerRG12
    BayerGB12 = VmbPixelFormat.BayerGB12
    BayerBG12 = VmbPixelFormat.BayerBG12
    BayerGR12Packed = VmbPixelFormat.BayerGR12Packed
    BayerRG12Packed = VmbPixelFormat.BayerRG12Packed
    BayerGB12Packed = VmbPixelFormat.BayerGB12Packed
    BayerBG12Packed = VmbPixelFormat.BayerBG12Packed
    BayerGR10p = VmbPixelFormat.BayerGR10p
    BayerRG10p = VmbPixelFormat.BayerRG10p
    BayerGB10p = VmbPixelFormat.BayerGB10p
    BayerBG10p = VmbPixelFormat.BayerBG10p
    BayerGR12p = VmbPixelFormat.BayerGR12p
    BayerRG12p = VmbPixelFormat.BayerRG12p
    BayerGB12p = VmbPixelFormat.BayerGB12p
    BayerBG12p = VmbPixelFormat.BayerBG12p
    BayerGR16 = VmbPixelFormat.BayerGR16
    BayerRG16 = VmbPixelFormat.BayerRG16
    BayerGB16 = VmbPixelFormat.BayerGB16
    BayerBG16 = VmbPixelFormat.BayerBG16

    # RGB Formats
    Rgb8 = VmbPixelFormat.Rgb8
    Bgr8 = VmbPixelFormat.Bgr8
    Rgb10 = VmbPixelFormat.Rgb10
    Bgr10 = VmbPixelFormat.Bgr10
    Rgb12 = VmbPixelFormat.Rgb12
    Bgr12 = VmbPixelFormat.Bgr12
    Rgb14 = VmbPixelFormat.Rgb14
    Bgr14 = VmbPixelFormat.Bgr14
    Rgb16 = VmbPixelFormat.Rgb16
    Bgr16 = VmbPixelFormat.Bgr16

    # RGBA Formats
    Rgba8 = VmbPixelFormat.Rgba8
    Bgra8 = VmbPixelFormat.Bgra8
    Argb8 = VmbPixelFormat.Argb8
    Rgba10 = VmbPixelFormat.Rgba10
    Bgra10 = VmbPixelFormat.Bgra10
    Rgba12 = VmbPixelFormat.Rgba12
    Bgra12 = VmbPixelFormat.Bgra12
    Rgba14 = VmbPixelFormat.Rgba14
    Bgra14 = VmbPixelFormat.Bgra14
    Rgba16 = VmbPixelFormat.Rgba16
    Bgra16 = VmbPixelFormat.Bgra16
    Yuv411 = VmbPixelFormat.Yuv411
    Yuv422 = VmbPixelFormat.Yuv422
    Yuv444 = VmbPixelFormat.Yuv444

    # YCbCr Formats
    YCbCr411_8_CbYYCrYY = VmbPixelFormat.YCbCr411_8_CbYYCrYY
    YCbCr422_8_CbYCrY = VmbPixelFormat.YCbCr422_8_CbYCrY
    YCbCr8_CbYCr = VmbPixelFormat.YCbCr8_CbYCr

    def __str__(self):
        return self._name_

    def __repr__(self):
        return 'PixelFormat.{}'.format(str(self))

    def get_convertible_formats(self) -> Tuple['PixelFormat', ...]:
        formats = PIXEL_FORMAT_CONVERTIBILITY_MAP[VmbPixelFormat(self)]
        return tuple([PixelFormat(fmt) for fmt in formats])


class TransportLayerType(enum.IntEnum):
    """Enum specifying all interface types.

    Enum values:
        Unknown  - Interface is not known to this version of the API
        GEV      - GigE Vision
        CL       - Camera Link
        IIDC     - IIDC 1394
        UVC      - USB video class
        CXP      - CoaXPress
        CLHS     - Camera Link HS
        U3V      - USB3 Vision Standard
        Ethernet - Generic Ethernet
        PCI      - PCI / PCIe
        Custom   - Non standard
        Mixed    - Mixed (transport layer only)
    """
    Unknown = VmbTransportLayer.Unknown
    GEV = VmbTransportLayer.GEV
    CL = VmbTransportLayer.CL
    IIDC = VmbTransportLayer.IIDC
    UVC = VmbTransportLayer.UVC
    CXP = VmbTransportLayer.CXP
    CLHS = VmbTransportLayer.CLHS
    U3V = VmbTransportLayer.U3V
    Ethernet = VmbTransportLayer.Ethernet
    PCI = VmbTransportLayer.PCI
    Custom = VmbTransportLayer.Custom
    Mixed = VmbTransportLayer.Mixed
