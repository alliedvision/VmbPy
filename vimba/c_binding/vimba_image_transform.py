"""Submodule encapsulating the VimbaImageTransform access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import ctypes

from ctypes import byref, c_char_p, POINTER as c_ptr
from typing import Callable, Any, Tuple

from ..error import VimbaSystemError
from ..util import TraceEnable
from .vimba_common import Uint32Enum, VmbBool, VmbUint8, VmbUint32, VmbInt32, VmbError, VmbFloat, \
                          VimbaCError, VmbPixelFormat, load_vimba_lib, fmt_repr, fmt_enum_repr


__all__ = [
    'VmbBayerPattern',
    'VmbEndianness',
    'VmbAligment',
    'VmbAPIInfo',
    'VmbPixelLayout',
    'Vmb12BitPackedPair',
    'VmbSupportState',
    'VmbTechInfo',
    'EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION',
    'call_vimba_image_transform'
]


class VmbBayerPattern(Uint32Enum):
    """Enum defining BayerPatterns
    Values:
        RGGB - RGGB pattern, red pixel comes first
        GBRG - RGGB pattern, green pixel of blue row comes first
        GRBG - RGGB pattern, green pixel of red row comes first
        BGGR - RGGB pattern, blue pixel comes first
        CYGM - CYGM pattern, cyan pixel comes first in the first row, green in the second row
        GMCY - CYGM pattern, green pixel comes first in the first row, cyan in the second row
        CYMG - CYGM pattern, cyan pixel comes first in the first row, magenta in the second row
        MGCY - CYGM pattern, magenta pixel comes first in the first row, cyan in the second row
        LAST - Indicator for end of defined range
    """
    RGGB = 0
    GBRG = 1
    GRBG = 2
    BGGR = 3
    CYGM = 128
    GMCY = 129
    CYMG = 130
    MGCY = 131
    LAST = 255

    def __str__(self):
        return self._name_


class VmbEndianness(Uint32Enum):
    """Enum defining Endian Formats
    Values:
        LITTLE - Little Endian
        BIG - Big Endian
        LAST - Indicator for end of defined range
    """
    LITTLE = 0
    BÍG = 1
    LAST = 255

    def __str__(self):
        return self._name_


class VmbAligment(Uint32Enum):
    """Enum defining image alignment
    Values:
        MSB - Alignment (pppp pppp pppp ....)
        LSB - Alignment (.... pppp pppp pppp)
        LAST - Indicator for end of defined range
    """
    MSB = 0
    LSB = 1
    LAST = 255

    def __str__(self):
        return self._name_


class VmbAPIInfo(Uint32Enum):
    """API Info Types
    Values:
        ALL        - All Infos
        PLATFORM   - Platform the API was built for
        BUILD      - Build Types (debug or release)
        TECHNOLOGY - Special technology info
        LAST       - Indicator for end of defined range
    """
    ALL = 0
    PLATFORM = 1
    BUILD = 2
    TECHNOLOGY = 3
    LAST = 4

    def __str__(self):
        return self._name_


class VmbPixelLayout(Uint32Enum):
    """Image Pixel Layout Information. C Header offers no further documentation."""
    Mono = 0
    MonoPacked = 1
    Raw = 2
    RawPacked = 3
    RGB = 4
    BGR = 5
    RGBA = 6
    BGRA = 7
    YUV411 = 8
    YUV422 = 9
    YUV444 = 10
    MonoP = 11
    MonoPl = 12
    RawP = 13
    RawPl = 14
    YYCbYYCr411 = 15
    CbYYCrYY411 = YUV411,
    YCbYCr422 = 16
    CbYCrY422 = YUV422
    YCbCr444 = 17
    CbYCr444 = YUV444
    LAST = 19

    def __str__(self):
        return self._name_


class VmbColorSpace(Uint32Enum):
    """Image Color space. C Header offers no further documentation."""
    Undefined = 0
    ITU_BT709 = 1
    ITU_BT601 = 2

    def __str__(self):
        return self._name_


class VmbDebayerMode(Uint32Enum):
    """Debayer Mode. C Header offers no further documentation."""
    Mode_2x2 = 0
    Mode_3x3 = 1
    Mode_LCAA = 2
    Mode_LCAAV = 3
    Mode_YUV422 = 4

    def __str__(self):
        return self._name_


class VmbTransformType(Uint32Enum):
    """TransformType Mode. C Header offers no further documentation."""
    None_ = 0
    DebayerMode = 1
    ColorCorrectionMatrix = 2
    GammaCorrection = 3
    Offset = 4
    Gain = 5

    def __str__(self):
        return self._name_


class Vmb12BitPackedPair(ctypes.Structure):
    """Data packed in 3 Byte transfer mode, two pixel packed in 3 byte.
    Fields:
        m_nVal8_1     - High byte of the first pixel
        m_nVal8_1_Low - Low nibble of the first pixel
        m_nVal8_2_Low - Low nibble of the second pixel
        m_nVal8_2     - High byte of the second pixel
    """

    _fields_ = [
        ('m_nVal8_1', VmbUint8),
        ('m_nVal8_1_Low', VmbUint8, 4),
        ('m_nVal8_2_Low', VmbUint8, 4),
        ('m_nVal8_2', VmbUint8)
    ]

    def __repr__(self):
        rep = 'Vmb12BitPackedPair'
        rep += fmt_repr('(m_nVal8_1={}', self.m_nVal8_1)
        rep += fmt_repr(',m_nVal8_1_Low={}', self.m_nVal8_1_Low)
        rep += fmt_repr(',m_nVal8_2_Low={}', self.m_nVal8_2_Low)
        rep += fmt_repr(',m_nVal8_2={}', self.m_nVal8_2)
        rep += ')'
        return rep


class VmbSupportState(ctypes.Structure):
    """State indicating if a technology is supported by the host system.
    Fields:
        Processor - Is technology supported by the CPU
        OperatingSystem - Is technology supported by the OS.
    """
    _fields_ = [
        ('Processor', VmbBool),
        ('OperatingSystem', VmbBool)
    ]

    def __repr__(self):
        rep = 'VmbSupportState'
        rep += fmt_repr('(Processor={}', self.Processor)
        rep += fmt_repr(',OperatingSystem={}', self.OperatingSystem)
        rep += ')'
        return rep


class VmbTechInfo(ctypes.Structure):
    """Holds support state for different technologies.
    Fields:
        IntelMMX      - MMX support
        IntelSSE      - SSE support
        IntelSSE2     - SSE2 support
        IntelSSE3     - SSE3 support
        IntelSSSE3    - SSSE3 support
        IntelAMD3DNow - AMD3DNow support
    """
    _fields_ = [
        ('IntelMMX', VmbSupportState),
        ('IntelSSE', VmbSupportState),
        ('IntelSSE2', VmbSupportState),
        ('IntelSSE3', VmbSupportState),
        ('IntelSSSE3', VmbSupportState),
        ('IntelAMD3DNow', VmbSupportState),
    ]

    def __repr__(self):
        rep = 'VmbTechInfo'
        rep += fmt_repr('(IntelMMX={}', self.IntelMMX)
        rep += fmt_repr(',IntelSSE={}', self.IntelSSE)
        rep += fmt_repr(',IntelSSE2={}', self.IntelSSE2)
        rep += fmt_repr(',IntelSSE3={}', self.IntelSSE3)
        rep += fmt_repr(',IntelSSSE3={}', self.IntelSSSE3)
        rep += fmt_repr(',IntelAMD3DNow={}', self.IntelAMD3DNow)
        rep += ')'
        return rep


class VmbPixelInfo(ctypes.Structure):
    """Structure containing pixel information. Sadly c_header contains no more documentation"""
    _fields_ = [
        ('BitsPerPixel', VmbUint32),
        ('BitsUsed', VmbUint32),
        ('Alignment', VmbUint32),
        ('Endianess', VmbUint32),
        ('BayerPattern', VmbUint32),
        ('Reserved', VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbPixelInfo'
        rep += fmt_repr('(BitsPerPixel={}', self.BitsPerPixel)
        rep += fmt_repr(',BitsUsed={}', self.BitsUsed)
        rep += fmt_enum_repr(',Alignment={}', VmbAligment, self.Alignment)
        rep += fmt_enum_repr(',Endianess={}', VmbEndianness, self.Endianess)
        rep += fmt_enum_repr(',BayerPattern={}', VmbBayerPattern, self.BayerPattern)
        rep += fmt_enum_repr(',Reserved={}', VmbColorSpace, self.Reserved)
        rep += ')'
        return rep


class VmbImageInfo(ctypes.Structure):
    """Structure containing image information. Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Width', VmbUint32),
        ('Height', VmbUint32),
        ('Stride', VmbInt32),
        ('PixelInfo', VmbPixelInfo)
    ]

    def __repr__(self):
        rep = 'VmbImageInfo'
        rep += fmt_repr('(Width={}', self.Width)
        rep += fmt_repr(',Height={}', self.Height)
        rep += fmt_repr(',Stride={}', self.Stride)
        rep += fmt_repr(',PixelInfo={}', self.PixelInfo)
        rep += ')'
        return rep


class VmbImage(ctypes.Structure):
    """Structure containing image. Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Size', VmbUint32),
        ('Data', ctypes.c_void_p),
        ('ImageInfo', VmbImageInfo)
    ]

    def __repr__(self):
        rep = 'VmbImage'
        rep += fmt_repr('(Size={}', self.Size)
        rep += fmt_repr(',Data={}', self.Data)
        rep += fmt_repr(',ImageInfo={}', self.ImageInfo)
        rep += ')'
        return rep


class VmbTransformParameterMatrix3x3(ctypes.Structure):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Matrix', VmbFloat * 9)
    ]


class VmbTransformParameterGamma(ctypes.Structure):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Gamma', VmbFloat)
    ]


class VmbTransformParameterDebayer(ctypes.Structure):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Method', VmbUint32)
    ]


class VmbTransformParameterOffset(ctypes.Structure):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Offset', VmbInt32)
    ]


class VmbTransformParameterGain(ctypes.Structure):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Gain', VmbUint32)
    ]


class VmbTransformParameter(ctypes.Union):
    """Sadly c_header contains no more documentation"""
    _fields_ = [
        ('Matrix3x3', VmbTransformParameterMatrix3x3),
        ('Debayer', VmbTransformParameterDebayer),
        ('Gamma', VmbTransformParameterGamma),
        ('Offset', VmbTransformParameterOffset),
        ('Gain', VmbTransformParameterGain)
    ]


class VmbTransformInfo(ctypes.Structure):
    """Struct holding transformation information"""
    _field_ = [
        ('TransformType', VmbUint32),
        ('Parameter', VmbTransformParameter)
    ]


# API
EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION = '1.6'

# For detailed information on the signatures see "VimbaImageTransform.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbGetVersion': (VmbError, [c_ptr(VmbUint32)]),
    'VmbGetTechnoInfo': (VmbError, [c_ptr(VmbTechInfo)]),
    'VmbGetErrorInfo': (VmbError, [VmbError, c_char_p, VmbUint32]),
    'VmbGetApiInfoString': (VmbError, [VmbAPIInfo, c_char_p, VmbUint32]),
    'VmbSetDebayerMode': (VmbError, [VmbDebayerMode, c_ptr(VmbTransformInfo)]),
    'VmbSetColorCorrectionMatrix3x3': (VmbError, [c_ptr(VmbFloat), c_ptr(VmbTransformInfo)]),
    'VmbSetGammaCorrection': (VmbError, [VmbFloat, c_ptr(VmbTransformInfo)]),
    'VmbSetImageInfoFromPixelFormat': (VmbError, [VmbPixelFormat, VmbUint32, VmbUint32, c_ptr(VmbImage)]),                                 # noqa: E501
    'VmbSetImageInfoFromString': (VmbError, [c_char_p, VmbUint32, VmbUint32, VmbUint32, c_ptr(VmbImage)]),                                 # noqa: E501
    'VmbSetImageInfoFromInputParameters': (VmbError, [VmbPixelFormat, VmbUint32, VmbUint32, VmbPixelLayout, VmbUint32, c_ptr(VmbImage)]),  # noqa: E501
    'VmbSetImageInfoFromInputImage': (VmbError, [c_ptr(VmbImage), VmbPixelLayout, VmbUint32, c_ptr(VmbImage)]),                            # noqa: E501
    'VmbImageTransform': (VmbError, [c_ptr(VmbImage), c_ptr(VmbImage), c_ptr(VmbTransformInfo), VmbUint32])                                # noqa: E501
}


def _attach_signatures(lib_handle: ctypes.CDLL) -> ctypes.CDLL:
    global _SIGNATURES

    for function_name, signature in _SIGNATURES.items():
        fn = getattr(lib_handle, function_name)
        fn.restype, fn.argtypes = signature
        fn.errcheck = _eval_vmberror

    return lib_handle


def _check_version(lib_handle: ctypes.CDLL) -> ctypes.CDLL:
    global EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION

    v = VmbUint32()
    lib_handle.VmbGetVersion(byref(v))

    ver = '{}.{}'.format((v.value >> 24) & 0xff, (v.value >> 16) & 0xff)
    expected_ver = EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION

    if (ver != expected_ver):
        msg = 'Invalid VimbaImageTransform Version: Expected: {}, Found:{}'
        raise VimbaSystemError(msg.format(expected_ver, ver))

    return lib_handle


def _eval_vmberror(result: VmbError, func: Callable[..., Any], *args: Tuple[Any, ...]):
    if result not in (VmbError.Success, None):
        raise VimbaCError(result)


_lib_instance: ctypes.CDLL = _check_version(_attach_signatures(
    load_vimba_lib('VimbaImageTransform'))
)


@TraceEnable()
def call_vimba_image_transform(func_name: str, *args):
    """This function encapsulates the entire VimbaImageTransform access.

    For Details on valid function signatures see the 'VimbaImageTransform.h'.

    Arguments:
        func_name: The function name from VimbaImageTransform to be called.
        args: Varargs passed directly to the underlaying C-Function.

    Raises:
        TypeError if given are do not match the signature of the function.
        AttributeError if func with name 'func_name' does not exist.
        VimbaCError if the function call is valid but neither None or VmbError.Success was returned.

    The following functions of VimbaC can be executed:
        VmbGetVersion
        VmbGetTechnoInfo
        VmbGetErrorInfo
        VmbGetApiInfoString
        VmbSetDebayerMode
        VmbSetColorCorrectionMatrix3x3
        VmbSetGammaCorrection
        VmbSetImageInfoFromPixelFormat
        VmbSetImageInfoFromString
        VmbSetImageInfoFromInputParameters
        VmbSetImageInfoFromInputImage
        VmbImageTransform
    """

    global _lib_instance
    getattr(_lib_instance, func_name)(*args)
