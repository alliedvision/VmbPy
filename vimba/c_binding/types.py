# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import ctypes
import enum

from .util import fmt_repr, fmt_enum_repr, fmt_flags_repr


class _Int32Enum(enum.IntEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_int(obj)


class _Uint32Enum(enum.IntEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_uint(obj)


class _VmbPixel(_Uint32Enum):
    Mono = 0x01000000
    Color = 0x02000000


class _VmbPixelOccupy(_Uint32Enum):
    Bit8 = 0x00080000
    Bit10 = 0x000A0000
    Bit12 = 0x000C0000
    Bit14 = 0x000E0000
    Bit16 = 0x00100000
    Bit24 = 0x00180000
    Bit32 = 0x00200000
    Bit48 = 0x00300000
    Bit64 = 0x00400000


# Aliases for vmb base types
VmbInt8 = ctypes.c_byte
VmbUint8 = ctypes.c_ubyte
VmbInt16 = ctypes.c_short
VmbUint16 = ctypes.c_ushort
VmbInt32 = ctypes.c_int
VmbUint32 = ctypes.c_uint
VmbInt64 = ctypes.c_longlong
VmbUint64 = ctypes.c_ulonglong
VmbHandle = ctypes.c_void_p
VmbBool = ctypes.c_bool
VmbUchar = ctypes.c_char
VmbDouble = ctypes.c_double


class VmbError(_Int32Enum):
    """
    Enum containing error types returned
        Success         - No error
        InternalFault   - Unexpected fault in VimbaC or driver
        ApiNotStarted   - VmbStartup() was not called before the current
                          command
        NotFound        - The designated instance (camera, feature etc.)
                          cannot be found
        BadHandle       - The given handle is not valid
        DeviceNotOpen   - Device was not opened for usage
        InvalidAccess   - Operation is invalid with the current access mode
        BadParameter    - One of the parameters is invalid (usually an illegal
                          pointer)
        StructSize      - The given struct size is not valid for this version
                          of the API
        MoreData        - More data available in a string/list than space is
                          provided
        WrongType       - Wrong feature type for this access function
        InvalidValue    - The value is not valid; Either out of bounds or not
                          an increment of the minimum
        Timeout         - Timeout during wait
        Other           - Other error
        Resources       - Resources not available (e.g. memory)
        InvalidCall     - Call is invalid in the current context (callback)
        NoTL            - No transport layers are found
        NotImplemented_ - API feature is not implemented
        NotSupported    - API feature is not supported
        Incomplete      - A multiple registers read or write is partially
                          completed
        IO              - low level IO error in transport layer
    """
    Success = 0
    InternalFault = -1
    ApiNotStarted = -2
    NotFound = -3
    BadHandle = -4
    DeviceNotOpen = -5
    InvalidAccess = -6
    BadParameter = -7
    StructSize = -8
    MoreData = -9
    WrongType = -10
    InvalidValue = -11
    Timeout = -12
    Other = -13
    Resources = -14
    InvalidCall = -15
    NoTL = -16
    NotImplemented_ = -17
    NotSupported = -18
    Incomplete = -19
    IO = -20

    def __str__(self):
        return self._name_


class VmbPixelFormat(_Uint32Enum):
    """
    Enum containing Pixelformats
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
    None_ = 0
    Mono8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0001
    Mono10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0003
    Mono10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0046
    Mono12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0005
    Mono12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0006
    Mono12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0047
    Mono14 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0025
    Mono16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0007
    BayerGR8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0008
    BayerRG8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0009
    BayerGB8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x000A
    BayerBG8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x000B
    BayerGR10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000C
    BayerRG10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000D
    BayerGB10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000E
    BayerBG10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000F
    BayerGR12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0010
    BayerRG12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0011
    BayerGB12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0012
    BayerBG12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0013
    BayerGR12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002A
    BayerRG12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002B
    BayerGB12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002C
    BayerBG12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002D
    BayerGR10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0056
    BayerRG10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0058
    BayerGB10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0054
    BayerBG10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0052
    BayerGR12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0057
    BayerRG12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0059
    BayerGB12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0055
    BayerBG12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0053
    BayerGR16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x002E
    BayerRG16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x002F
    BayerGB16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0030
    BayerBG16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0031
    Rgb8 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0014
    Bgr8 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0015
    Rgb10 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0018
    Bgr10 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0019
    Rgb12 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x001A
    Bgr12 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x001B
    Rgb14 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x005E
    Bgr14 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x004A
    Rgb16 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0033
    Bgr16 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x004B
    Argb8 = _VmbPixel.Color | _VmbPixelOccupy.Bit32 | 0x0016
    Rgba8 = Argb8
    Bgra8 = _VmbPixel.Color | _VmbPixelOccupy.Bit32 | 0x0017
    Rgba10 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x005F
    Bgra10 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x004C
    Rgba12 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0061
    Bgra12 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x004E
    Rgba14 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0063
    Bgra14 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0050
    Rgba16 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0064
    Bgra16 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0051
    Yuv411 = _VmbPixel.Color | _VmbPixelOccupy.Bit12 | 0x001E
    Yuv422 = _VmbPixel.Color | _VmbPixelOccupy.Bit16 | 0x001F
    Yuv444 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0020
    YCbCr411_8_CbYYCrYY = _VmbPixel.Color | _VmbPixelOccupy.Bit12 | 0x003C
    YCbCr422_8_CbYCrY = _VmbPixel.Color | _VmbPixelOccupy.Bit16 | 0x0043
    YCbCr8_CbYCr = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x003A

    def __str__(self):
        return self._name_


class VmbInterface(_Uint32Enum):
    """
    Camera Interface Types:
        Unknown  - Interface is not known to this version of the API
        Firewire - 1394
        Ethernet - GigE
        Usb      - USB 3.0
        CL       - Camera Link
        CSI2     - CSI-2
    """
    Unknown = 0
    Firewire = 1
    Ethernet = 2
    Usb = 3
    CL = 4
    CSI2 = 5

    def __str__(self):
        return self._name_


class VmbAccessMode(_Uint32Enum):
    """
    Camera Access Mode:
        None_  - No access
        Full   - Read and write access
        Read   - Read-only access
        Config - Configuration access (GeV)
        Lite   - Read and write access without feature access (only addresses)
    """
    None_ = 0
    Full = 1
    Read = 2
    Config = 4
    Lite = 8

    def __str__(self):
        return self._name_


class VmbFeatureData(_Uint32Enum):
    """
    Feature Data Types
        Unknown - Unknown feature type
        Int     - 64 bit integer feature
        Float   - 64 bit floating point feature
        Enum    - Enumeration feature
        String  - String feature
        Bool    - Boolean feature
        Command - Command feature
        Raw     - Raw (direct register access) feature
        None_   - Feature with no data
    """
    Unknown = 0
    Int = 1
    Float = 2
    Enum = 3
    String = 4
    Bool = 5
    Command = 6
    Raw = 7
    None_ = 8

    def __str__(self):
        return self._name_


class VmbFeaturePersist(_Uint32Enum):
    """
    Type of features that are to be saved (persisted) to the XML file
    when using VmbCameraSettingsSave

        All        - Save all features to XML, including look-up tables
        Streamable - Save only features marked as streamable, excluding
                     look-up tables
        NoLUT      - Save all features except look-up tables (default)
    """
    All = 0
    Streamable = 1
    NoLUT = 2

    def __str__(self):
        return self._name_


class VmbFeatureVisibility(_Uint32Enum):
    """
    Feature Visibility
        Unknown   - Feature visibility is not known
        Beginner  - Feature is visible in feature list (beginner level)
        Expert    - Feature is visible in feature list (expert level)
        Guru      - Feature is visible in feature list (guru level)
        Invisible - Feature is not visible in feature list
    """
    Unknown = 0
    Beginner = 1
    Expert = 2
    Guru = 3
    Invisible = 4

    def __str__(self):
        return self._name_


class VmbFeatureFlags(_Uint32Enum):
    """
    Feature Flags
        None_       - No additional information is provided
        Read        - Static info about read access.
                      Current status depends on access mode, check with
                      VmbFeatureAccessQuery()
        Write       - Static info about write access.
                      Current status depends on access mode, check with
                      VmbFeatureAccessQuery()
        Volatile    - Value may change at any time
        ModifyWrite - Value may change after a write
    """
    None_ = 0
    Read = 1
    Write = 2
    Undocumented = 4
    Volatile = 8
    ModifyWrite = 16

    def __str__(self):
        return self._name_


class VmbFrameStatus(_Int32Enum):
    """
    Frame transfer status
        Complete   - Frame has been completed without errors
        Incomplete - Frame could not be filled to the end
        TooSmall   - Frame buffer was too small
        Invalid    - Frame buffer was invalid
    """
    Complete = 0
    Incomplete = -1
    TooSmall = -2
    Invalid = -3

    def __str__(self):
        return self._name_


class VmbFrameFlags(_Uint32Enum):
    """
    Frame Flags
        None_     - No additional information is provided
        Dimension - Frame's dimension is provided
        Offset    - Frame's offset is provided (ROI)
        FrameID   - Frame's ID is provided
        Timestamp - Frame's timestamp is provided
    """
    None_ = 0
    Dimension = 1
    Offset = 2
    FrameID = 4
    Timestamp = 8

    def __str__(self):
        return self._name_


class VmbVersionInfo(ctypes.Structure):
    """
    Version Information
        Fields:
            major - Type: VmbUint32, Info: Major version number
            minor - Type: VmbUint32, Info: Minor version number
            patch - Type: VmbUint32, Info: Patch version number
    """
    _fields_ = [
        ("major", VmbUint32),
        ("minor", VmbUint32),
        ("patch", VmbUint32)
    ]

    def __str__(self):
        return '{}.{}.{}'.format(self.major, self.minor, self.patch)

    def __repr__(self):
        rep = 'VmbVersionInfo'
        rep += '(major=' + repr(self.major)
        rep += ',minor=' + repr(self.minor)
        rep += ',patch=' + repr(self.patch)
        rep += ')'
        return rep


class VmbInterfaceInfo(ctypes.Structure):
    """
    Interface information. Holds read-only information about an interface.
        Fields:
            interfaceIdString - Type: c_char_p
                                Info: Unique identifier for each interface
            interfaceType     - Type: VmbInterface (VmbUint32)
                                Info: Interface type, see VmbInterface
            interfaceName     - Type: c_char_p
                                Info: Interface name, given by transport layer
            serialString      - Type: c_char_p
                                Info: Serial number
            permittenAccess   - Type: VmbAccessMode (VmbUint32)
                                Info: Used access mode, see VmbAccessMode
    """
    _fields_ = [
        ("interfaceIdString", ctypes.c_char_p),
        ("interfaceType", VmbUint32),
        ("interfaceName", ctypes.c_char_p),
        ("serialString", ctypes.c_char_p),
        ("permittedAccess", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbInterfaceInfo'
        rep += fmt_repr('(interfaceIdString={}', self.interfaceIdString)
        rep += fmt_enum_repr(',interfaceType={}', VmbInterface, self.interfaceType)
        rep += fmt_repr(',interfaceName={}', self.interfaceName)
        rep += fmt_repr(',serialString={}', self.serialString)
        rep += fmt_flags_repr(',permittedAccess={}', VmbAccessMode, self.permittedAccess)
        rep += ')'
        return rep


class VmbCameraInfo(ctypes.Structure):
    """
    Camera information. Holds read-only information about a camera.
        Fields:
            cameraIdString    - Type: c_char_p
                                Info: Unique identifier for each camera
            cameraName        - Type: c_char_p
                                Info: Name of the camera
            modelName         - Type: c_char_p
                                Info: Model name
            serialString      - Type: c_char_p
                                Info: Serial number
            permittedAccess   - Type: VmbAccessMode (VmbUint32)
                                Info: Used access mode, see VmbAccessMode
            interfaceIdString - Type: c_char_p
                                Info: Unique value for each interface or bus
    """
    _fields_ = [
        ("cameraIdString", ctypes.c_char_p),
        ("cameraName", ctypes.c_char_p),
        ("modelName", ctypes.c_char_p),
        ("serialString", ctypes.c_char_p),
        ("permittedAccess", VmbUint32),
        ("interfaceIdString", ctypes.c_char_p)
    ]

    def __repr__(self):
        rep = 'VmbCameraInfo'
        rep += fmt_repr('(cameraIdString={}', self.cameraIdString)
        rep += fmt_repr(',cameraName={}', self.cameraName)
        rep += fmt_repr(',modelName={}', self.modelName)
        rep += fmt_repr(',serialString={}', self.serialString)
        rep += fmt_flags_repr(',permittedAccess={}', VmbAccessMode, self.permittedAccess)
        rep += fmt_repr(',interfaceIdString={}', self.interfaceIdString)
        rep += ')'
        return rep


class VmbFeatureInfo(ctypes.Structure):
    """
    Feature information. Holds read-only information about a feature.
        Fields:
            name                - Type: c_char_p
                                  Info: Name used in the API
            featureDataType     - Type: VmbFeatureData (VmbUint32)
                                  Info: Data type of this feature
            featureFlags        - Type: VmbFeatureFlags (VmbUint32)
                                  Info: Access flags for this feature
            category            - Type: c_char_p
                                  Info: Category this feature can be found in
            displayName         - Type: c_char_p
                                  Info: Feature name to be used in GUIs
            pollingTime         - Type: VmbUint32
                                  Info: Predefined polling time for volatile
                                        features
            unit                - Type: c_char_p
                                  Info: Measuring unit as given in the XML file
            representation      - Type: c_char_p
                                  Info: Representation of a numeric feature
            visibility          - Type: VmbFeatureVisibility (VmbUint32)
                                  Info: GUI visibility
            tooltip             - Type: c_char_p
                                  Info: Short description, e.g. for a tooltip
            description         - Type: c_char_p
                                  Info: Longer description
            sfncNamespace       - Type: c_char_p
                                  Info: Namespace this feature resides in
            isStreamable        - Type: VmbBool
                                  Info: Indicates if a feature can be stored
                                        to / loaded from a file
            hasAffectedFeatures - Type: VmbBool
                                  Info: Indicates if the feature potentially
                                        affects other features
            hasSelectedFeatures - Type: VmbBool
                                  Info: Indicates if the feature selects other
                                        features
    """
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("featureDataType", VmbUint32),
        ("featureFlags", VmbUint32),
        ("category", ctypes.c_char_p),
        ("displayName", ctypes.c_char_p),
        ("pollingTime", VmbUint32),
        ("unit", ctypes.c_char_p),
        ("representation", ctypes.c_char_p),
        ("visibility", VmbUint32),
        ("tooltip", ctypes.c_char_p),
        ("description", ctypes.c_char_p),
        ("sfncNamespace", ctypes.c_char_p),
        ("isStreamable", VmbBool),
        ("hasAffectedFeatures", VmbBool),
        ("hasSelectedFeatures", VmbBool)
    ]

    def __repr__(self):
        rep = 'VmbFeatureInfo'
        rep += fmt_repr('(name={}', self.name)
        rep += fmt_enum_repr(',featureDataType={}', VmbFeatureData, self.featureDataType)
        rep += fmt_flags_repr(',featureFlags={}', VmbFeatureFlags, self.featureFlags)
        rep += fmt_repr(',category={}', self.category)
        rep += fmt_repr(',displayName={}', self.displayName)
        rep += fmt_repr(',pollingTime={}', self.pollingTime)
        rep += fmt_repr(',unit={}', self.unit)
        rep += fmt_repr(',representation={}', self.representation)
        rep += fmt_enum_repr(',visibility={}', VmbFeatureVisibility, self.visibility)
        rep += fmt_repr(',tooltip={}', self.tooltip)
        rep += fmt_repr(',description={}', self.description)
        rep += fmt_repr(',sfncNamespace={}', self.sfncNamespace)
        rep += fmt_repr(',isStreamable={}', self.isStreamable)
        rep += fmt_repr(',hasAffectedFeatures={}', self.hasAffectedFeatures)
        rep += fmt_repr(',hasSelectedFeatures={}', self.hasSelectedFeatures)
        rep += ')'
        return rep


class VmbFeatureEnumEntry(ctypes.Structure):
    """
    Info about possible entries of an enumeration feature:
        Fields:
            name          - Type: c_char_p
                            Info: Name used in the API
            displayName   - Type: c_char_p
                            Info: Enumeration entry name to be used in GUIs
            visibility    - Type: VmbFeatureVisibility (VmbUint32)
                            Info: GUI visibility
            tooltip       - Type: c_char_p
                            Info: Short description, e.g. for a tooltip
            description   - Type: c_char_p
                            Info: Longer description
            sfncNamespace - Type: c_char_p
                            Info: Namespace this feature resides in
            intValue      - Type: VmbInt64
                            Info: Integer value of this enumeration entry
    """
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("displayName", ctypes.c_char_p),
        ("visibility", VmbUint32),
        ("tooltip", ctypes.c_char_p),
        ("description", ctypes.c_char_p),
        ("sfncNamespace", ctypes.c_char_p),
        ("intValue", VmbInt64)
    ]

    def __repr__(self):
        rep = 'VmbFeatureEnumEntry'
        rep += fmt_repr('(name={}', self.name)
        rep += fmt_repr(',displayName={}', self.displayName)
        rep += fmt_enum_repr(',visibility={}', VmbFeatureVisibility, self.visibility)
        rep += fmt_repr(',tooltip={}', self.tooltip)
        rep += fmt_repr(',description={}', self.description)
        rep += fmt_repr(',sfncNamespace={}', self.sfncNamespace)
        rep += fmt_repr(',intValue={},', self.intValue)
        rep += ')'
        return rep


class VmbFrame(ctypes.Structure):
    """
    Frame delivered by Camera
        Fields (in):
            buffer     - Type: c_void_p
                         Info: Comprises image and ancillary data
            bufferSize - Type: VmbUint32_t
                         Info: Size of the data buffer
            context    - Type: c_void_p[4]
                         Info: 4 void pointers that can be employed by the user
                               (e.g. for storing handles)

        Fields (out):
            receiveStatus - Type: VmbFrameStatus (VmbInt32)
                            Info: Resulting status of the receive operation
            receiveFlags  - Type: VmbFrameFlags (VmbUint32)
                            Info: Flags indicating which additional frame
                                  information is available
            imageSize     - Type: VmbUint32
                            Info: Size of the image data inside the data buffer
            ancillarySize - Type: VmbUint32
                            Info: Size of the ancillary data inside the
                                  data buffer
            pixelFormat   - Type: VmbPixelFormat (VmbUint32)
                            Info: Pixel format of the image
            width         - Type: VmbUint32
                            Info: Width of an image
            height        - Type: VmbUint32
                            Info: Height of an image
            offsetX       - Type: VmbUint32
                            Info: Horizontal offset of an image
            offsetY       - Type: VmbUint32
                            Info: Vertical offset of an image
            frameID       - Type: VmbUint64
                            Info: Unique ID of this frame in this stream
            timestamp     - Type: VmbUint64
                            Info: Timestamp set by the camera
    """
    _fields_ = [
        ("buffer", ctypes.c_void_p),
        ("bufferSize", VmbUint32),
        ("context", ctypes.c_void_p * 4),
        ("receiveStatus", VmbInt32),
        ("receiveFlags", VmbUint32),
        ("imageSize", VmbUint32),
        ("ancillarySize", VmbUint32),
        ("pixelFormat", VmbUint32),
        ("width", VmbUint32),
        ("height", VmbUint32),
        ("offsetX", VmbUint32),
        ("offsetY", VmbUint32),
        ("frameID", VmbUint64),
        ("timestamp", VmbUint64)
    ]

    def __repr__(self):
        rep = 'VmbFrame'
        rep += fmt_repr('(buffer={}', self.buffer)
        rep += fmt_repr(',bufferSize={}', self.bufferSize)
        rep += fmt_repr(',context={}', self.context)
        rep += fmt_enum_repr('receiveStatus: {}', VmbFrameStatus, self.receiveStatus)
        rep += fmt_flags_repr(',receiveFlags={}', VmbFrameFlags, self.receiveFlags)
        rep += fmt_repr(',imageSize={}', self.imageSize)
        rep += fmt_repr(',ancillarySize={}', self.ancillarySize)
        rep += fmt_enum_repr(',pixelFormat={}', VmbPixelFormat, self.pixelFormat)
        rep += fmt_repr(',width={}', self.width)
        rep += fmt_repr(',height={}', self.height)
        rep += fmt_repr(',offsetX={}', self.offsetX)
        rep += fmt_repr(',offsetY={}', self.offsetY)
        rep += fmt_repr(',frameID={}', self.frameID)
        rep += fmt_repr(',timestamp={}', self.timestamp)
        rep += ')'
        return rep


class VmbFeaturePersistSettings(ctypes.Structure):
    """
    Parameters determining the operation mode of VmbCameraSettingsSave
    and VmbCameraSettingsLoad
        Fields:
            persistType   - Type: VmbFeaturePersist (VmbUint32)
                            Info: Type of features that are to be saved
            maxIterations - Type: VmbUint32
                            Info: Number of iterations when loading settings
            loggingLevel  - Type: VmbUint32
                            Info: Determines level of detail for load/save
                                  settings logging
    """
    _fields_ = [
        ("persistType", VmbUint32),
        ("maxIterations", VmbUint32),
        ("loggingLevel", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbFrame'
        rep += fmt_enum_repr('(persistType={}', VmbFeaturePersist, self.persistType)
        rep += fmt_repr(',maxIterations={}', self.maxIterations)
        rep += fmt_repr(',loggingLevel={}', self.loggingLevel)
        rep += ')'
        return rep


VmbInvalidationCallback = ctypes.CFUNCTYPE(None, VmbHandle, ctypes.c_char_p,
                                           ctypes.c_void_p)

VmbFrameCallback = ctypes.CFUNCTYPE(None, VmbHandle, ctypes.POINTER(VmbFrame))


G_VIMBA_HANDLE = VmbHandle(1)
