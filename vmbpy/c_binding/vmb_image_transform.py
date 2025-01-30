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
from ctypes import POINTER as c_ptr
from ctypes import byref, sizeof
from typing import Any, Callable, Dict, List, Tuple

from ..error import VmbSystemError
from ..util import TraceEnable
from .vmb_common import (Uint32Enum, VmbCError, VmbError, VmbFloat, VmbInt32, VmbPixelFormat,
                         VmbUint32, fmt_enum_repr, fmt_repr, load_vimbax_lib)

__all__ = [
    'VmbBayerPattern',
    'VmbEndianness',
    'VmbAligment',
    'VmbAPIInfo',
    'VmbPixelLayout',
    'VmbDebayerMode',
    'VmbImage',
    'VmbImageInfo',
    'VmbTransformInfo',
    'VMB_IMAGE_TRANSFORM_VERSION',
    'EXPECTED_VMB_IMAGE_TRANSFORM_VERSION',
    'call_vmb_image_transform',
    'PIXEL_FORMAT_TO_LAYOUT',
    'LAYOUT_TO_PIXEL_FORMAT',
    'PIXEL_FORMAT_CONVERTIBILITY_MAP'
]


class VmbBayerPattern(Uint32Enum):
    """Enum defining BayerPatterns."""
    RGGB = 0    #: RGGB pattern, red pixel comes first
    GBRG = 1    #: RGGB pattern, green pixel of blue row comes first
    GRBG = 2    #: RGGB pattern, green pixel of red row comes first
    BGGR = 3    #: RGGB pattern, blue pixel comes first
    CYGM = 128  #: CYGM pattern, cyan pixel comes first in the first row, green in the second row
    GMCY = 129  #: CYGM pattern, green pixel comes first in the first row, cyan in the second row
    CYMG = 130  #: CYGM pattern, cyan pixel comes first in the first row, magenta in the second row
    MGCY = 131  #: CYGM pattern, magenta pixel comes first in the first row, cyan in the second row
    LAST = 255  #: Indicator for end of defined range

    def __str__(self):
        return self._name_


class VmbEndianness(Uint32Enum):
    """Enum defining Endian Formats."""
    LITTLE = 0  #: Little Endian
    BIG = 1     #: Big Endian
    LAST = 255  #: Indicator for end of defined range

    def __str__(self):
        return self._name_


class VmbAligment(Uint32Enum):
    """Enum defining image alignment."""
    MSB = 0     #: Alignment (pppp pppp pppp ....)
    LSB = 1     #: Alignment (.... pppp pppp pppp)
    LAST = 255  #: Indicator for end of defined range

    def __str__(self):
        return self._name_


class VmbAPIInfo(Uint32Enum):
    """API Info Types."""
    ALL = 0         #: All Infos
    PLATFORM = 1    #: Platform the API was built for
    BUILD = 2       #: Build Types (debug or release)
    TECHNOLOGY = 3  #: Special technology info
    LAST = 4        #: Indicator for end of defined range

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


class VmbPixelInfo(ctypes.Structure):
    """Structure containing pixel information. C Header offers no further documentation."""
    _fields_ = [
        ('BitsPerPixel', VmbUint32),
        ('BitsUsed', VmbUint32),
        ('Alignment', VmbUint32),
        ('Endianness', VmbUint32),
        ('PixelLayout', VmbUint32),
        ('BayerPattern', VmbUint32),
        ('Reserved', VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbPixelInfo'
        rep += fmt_repr('(BitsPerPixel={}', self.BitsPerPixel)
        rep += fmt_repr(',BitsUsed={}', self.BitsUsed)
        rep += fmt_enum_repr(',Alignment={}', VmbAligment, self.Alignment)
        rep += fmt_enum_repr(',Endianness={}', VmbEndianness, self.Endianness)
        rep += fmt_enum_repr(',PixelLayout={}', VmbPixelLayout, self.PixelLayout)
        rep += fmt_enum_repr(',BayerPattern={}', VmbBayerPattern, self.BayerPattern)
        rep += fmt_enum_repr(',Reserved={}', VmbColorSpace, self.Reserved)
        rep += ')'
        return rep


class VmbImageInfo(ctypes.Structure):
    """Structure containing image information. C Header offers no further documentation."""
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
    """Structure containing image. C Header offers no further documentation."""
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
    """C Header offers no further documentation."""
    _fields_ = [
        ('Matrix', VmbFloat * 9)
    ]


class VmbTransformParameterGamma(ctypes.Structure):
    """C Header offers no further documentation."""
    _fields_ = [
        ('Gamma', VmbFloat)
    ]


class VmbTransformParameterDebayer(ctypes.Structure):
    """C Header offers no further documentation."""
    _fields_ = [
        ('Method', VmbUint32)
    ]


class VmbTransformParameterOffset(ctypes.Structure):
    """C Header offers no further documentation."""
    _fields_ = [
        ('Offset', VmbInt32)
    ]


class VmbTransformParameterGain(ctypes.Structure):
    """C Header offers no further documentation."""
    _fields_ = [
        ('Gain', VmbUint32)
    ]


class VmbTransformParameter(ctypes.Union):
    """C Header offers no further documentation."""
    _fields_ = [
        ('Matrix3x3', VmbTransformParameterMatrix3x3),
        ('Debayer', VmbTransformParameterDebayer),
        ('Gamma', VmbTransformParameterGamma),
        ('Offset', VmbTransformParameterOffset),
        ('Gain', VmbTransformParameterGain)
    ]


class VmbTransformInfo(ctypes.Structure):
    """Struct holding transformation information"""
    _fields_ = [
        ('TransformType', VmbUint32),
        ('Parameter', VmbTransformParameter)
    ]


# API
VMB_IMAGE_TRANSFORM_VERSION = None
EXPECTED_VMB_IMAGE_TRANSFORM_VERSION = '2.2'

# For detailed information on the signatures see "VmbTransform.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbGetImageTransformVersion': (VmbError, [c_ptr(VmbUint32)]),
    'VmbSetDebayerMode': (VmbError, [VmbDebayerMode, c_ptr(VmbTransformInfo)]),
    'VmbSetImageInfoFromPixelFormat': (VmbError, [VmbPixelFormat, VmbUint32, VmbUint32, c_ptr(VmbImage)]),       # noqa: E501
    'VmbSetImageInfoFromInputImage': (VmbError, [c_ptr(VmbImage), VmbPixelLayout, VmbUint32, c_ptr(VmbImage)]),  # noqa: E501
    'VmbImageTransform': (VmbError, [c_ptr(VmbImage), c_ptr(VmbImage), c_ptr(VmbTransformInfo), VmbUint32])      # noqa: E501
}


def _attach_signatures(lib_handle):
    global _SIGNATURES

    for function_name, signature in _SIGNATURES.items():
        fn = getattr(lib_handle, function_name)
        fn.restype, fn.argtypes = signature
        fn.errcheck = _eval_vmberror

    return lib_handle


def _check_version(lib_handle):
    global EXPECTED_VMB_IMAGE_TRANSFORM_VERSION
    global VMB_IMAGE_TRANSFORM_VERSION

    v = VmbUint32()
    lib_handle.VmbGetImageTransformVersion(byref(v))

    VMB_IMAGE_TRANSFORM_VERSION = '{}.{}'.format((v.value >> 24) & 0xff, (v.value >> 16) & 0xff)

    loaded_version = tuple(map(int, VMB_IMAGE_TRANSFORM_VERSION.split(".")))
    expected_version = tuple(map(int, EXPECTED_VMB_IMAGE_TRANSFORM_VERSION.split(".")))
    # Major version must match. minor version may be equal or greater
    if not (loaded_version[0] == expected_version[0] and
            loaded_version[1] >= expected_version[1]):
        msg = 'Invalid VmbImageTransform Version: Expected: {}, Found:{}'
        raise VmbSystemError(msg.format(EXPECTED_VMB_IMAGE_TRANSFORM_VERSION,
                                        VMB_IMAGE_TRANSFORM_VERSION))

    return lib_handle


def _eval_vmberror(result: VmbError, func: Callable[..., Any], *args: Tuple[Any, ...]):
    if result not in (VmbError.Success, None):
        raise VmbCError(result)


_lib_instance = _check_version(_attach_signatures(load_vimbax_lib('VmbImageTransform')))


@TraceEnable()
def call_vmb_image_transform(func_name: str, *args):
    """This function encapsulates the entire VmbImageTransform access.

    For Details on valid function signatures see the 'VmbTransform.h'.

    Arguments:
        func_name:
            The function name from VmbImageTransform to be called.
        args:
            Varargs passed directly to the underlying C-Function.

    Raises:
        TypeError:
            If given are do not match the signature of the function.
        AttributeError:
            If func with name 'func_name' does not exist.
        VmbCError:
            If the function call is valid but neither ``None`` or ``VmbError.Success`` was returned.

    The following functions of VmbImageTransform can be executed:
        - VmbGetImageTransformVersion
        - VmbGetTechnoInfo
        - VmbSetDebayerMode
        - VmbSetImageInfoFromPixelFormat
        - VmbSetImageInfoFromInputImage
        - VmbImageTransform
    """

    global _lib_instance
    getattr(_lib_instance, func_name)(*args)


PIXEL_FORMAT_TO_LAYOUT: Dict[VmbPixelFormat, Tuple[VmbPixelLayout, int]] = {
    VmbPixelFormat.Mono8: (VmbPixelLayout.Mono, 8),
    VmbPixelFormat.Mono10: (VmbPixelLayout.Mono, 16),
    VmbPixelFormat.Mono12: (VmbPixelLayout.Mono, 16),
    VmbPixelFormat.Mono14: (VmbPixelLayout.Mono, 16),
    VmbPixelFormat.Mono16: (VmbPixelLayout.Mono, 16),
    VmbPixelFormat.BayerGR8: (VmbPixelLayout.Raw, 8),
    VmbPixelFormat.BayerRG8: (VmbPixelLayout.Raw, 8),
    VmbPixelFormat.BayerGB8: (VmbPixelLayout.Raw, 8),
    VmbPixelFormat.BayerBG8: (VmbPixelLayout.Raw, 8),
    VmbPixelFormat.BayerGR10: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerRG10: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerGB10: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerBG10: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerGR12: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerRG12: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerGB12: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerBG12: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerGR16: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerRG16: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerGB16: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.BayerBG16: (VmbPixelLayout.Raw, 16),
    VmbPixelFormat.Rgb8: (VmbPixelLayout.RGB, 8),
    VmbPixelFormat.Rgb10: (VmbPixelLayout.RGB, 16),
    VmbPixelFormat.Rgb12: (VmbPixelLayout.RGB, 16),
    VmbPixelFormat.Rgb14: (VmbPixelLayout.RGB, 16),
    VmbPixelFormat.Rgb16: (VmbPixelLayout.RGB, 16),
    VmbPixelFormat.Bgr8: (VmbPixelLayout.BGR, 8),
    VmbPixelFormat.Bgr10: (VmbPixelLayout.BGR, 16),
    VmbPixelFormat.Bgr12: (VmbPixelLayout.BGR, 16),
    VmbPixelFormat.Bgr14: (VmbPixelLayout.BGR, 16),
    VmbPixelFormat.Bgr16: (VmbPixelLayout.BGR, 16),
    VmbPixelFormat.Rgba8: (VmbPixelLayout.RGBA, 8),
    VmbPixelFormat.Rgba10: (VmbPixelLayout.RGBA, 16),
    VmbPixelFormat.Rgba12: (VmbPixelLayout.RGBA, 16),
    VmbPixelFormat.Rgba14: (VmbPixelLayout.RGBA, 16),
    VmbPixelFormat.Rgba16: (VmbPixelLayout.RGBA, 16),
    VmbPixelFormat.Bgra8: (VmbPixelLayout.BGRA, 8),
    VmbPixelFormat.Bgra10: (VmbPixelLayout.BGRA, 16),
    VmbPixelFormat.Bgra12: (VmbPixelLayout.BGRA, 16),
    VmbPixelFormat.Bgra14: (VmbPixelLayout.BGRA, 16),
    VmbPixelFormat.Bgra16: (VmbPixelLayout.BGRA, 16)
}

LAYOUT_TO_PIXEL_FORMAT = dict([(v, k) for k, v in PIXEL_FORMAT_TO_LAYOUT.items()])


def _query_compatibility(pixel_format: VmbPixelFormat) -> Tuple[VmbPixelFormat, ...]:
    global LAYOUT_TO_PIXEL_FORMAT

    # Query compatible formats from ImageTransform
    output_pixel_layouts = (VmbPixelLayout.Mono, VmbPixelLayout.MonoPacked, VmbPixelLayout.Raw,
                            VmbPixelLayout.RawPacked, VmbPixelLayout.RGB, VmbPixelLayout.BGR,
                            VmbPixelLayout.RGBA, VmbPixelLayout.BGRA)

    output_bits_per_pixel = (8, 16)
    output_layouts = tuple([(layouts, bits)
                            for layouts in output_pixel_layouts
                            for bits in output_bits_per_pixel])

    result: List[VmbPixelFormat] = []

    src_image = VmbImage()
    src_image.Size = sizeof(src_image)

    call_vmb_image_transform('VmbSetImageInfoFromPixelFormat', pixel_format, 0, 0,
                             byref(src_image))

    dst_image = VmbImage()
    dst_image.Size = sizeof(dst_image)

    for layout, bits in output_layouts:

        try:
            call_vmb_image_transform('VmbSetImageInfoFromInputImage', byref(src_image), layout,
                                     bits, byref(dst_image))

            fmt = LAYOUT_TO_PIXEL_FORMAT[(layout, bits)]

            if fmt not in result:
                result.append(fmt)

        except VmbCError as e:
            if e.get_error_code() not in (VmbError.NotImplemented_, VmbError.BadParameter):
                raise e

    return tuple(result)


PIXEL_FORMAT_CONVERTIBILITY_MAP: Dict[VmbPixelFormat, Tuple[VmbPixelFormat, ...]] = {
    VmbPixelFormat.Mono8: _query_compatibility(VmbPixelFormat.Mono8),
    VmbPixelFormat.Mono10: _query_compatibility(VmbPixelFormat.Mono10),
    VmbPixelFormat.Mono10p: _query_compatibility(VmbPixelFormat.Mono10p),
    VmbPixelFormat.Mono12: _query_compatibility(VmbPixelFormat.Mono12),
    VmbPixelFormat.Mono12Packed: _query_compatibility(VmbPixelFormat.Mono12Packed),
    VmbPixelFormat.Mono12p: _query_compatibility(VmbPixelFormat.Mono12p),
    VmbPixelFormat.Mono14: _query_compatibility(VmbPixelFormat.Mono14),
    VmbPixelFormat.Mono16: _query_compatibility(VmbPixelFormat.Mono16),

    VmbPixelFormat.BayerGR8: _query_compatibility(VmbPixelFormat.BayerGR8),
    VmbPixelFormat.BayerRG8: _query_compatibility(VmbPixelFormat.BayerRG8),
    VmbPixelFormat.BayerGB8: _query_compatibility(VmbPixelFormat.BayerGB8),
    VmbPixelFormat.BayerBG8: _query_compatibility(VmbPixelFormat.BayerBG8),
    VmbPixelFormat.BayerGR10: _query_compatibility(VmbPixelFormat.BayerGR10),
    VmbPixelFormat.BayerRG10: _query_compatibility(VmbPixelFormat.BayerRG10),
    VmbPixelFormat.BayerGB10: _query_compatibility(VmbPixelFormat.BayerGB10),
    VmbPixelFormat.BayerBG10: _query_compatibility(VmbPixelFormat.BayerBG10),
    VmbPixelFormat.BayerGR12: _query_compatibility(VmbPixelFormat.BayerGR12),
    VmbPixelFormat.BayerRG12: _query_compatibility(VmbPixelFormat.BayerRG12),
    VmbPixelFormat.BayerGB12: _query_compatibility(VmbPixelFormat.BayerGB12),
    VmbPixelFormat.BayerBG12: _query_compatibility(VmbPixelFormat.BayerBG12),
    VmbPixelFormat.BayerGR12Packed: _query_compatibility(VmbPixelFormat.BayerGR12Packed),
    VmbPixelFormat.BayerRG12Packed: _query_compatibility(VmbPixelFormat.BayerRG12Packed),
    VmbPixelFormat.BayerGB12Packed: _query_compatibility(VmbPixelFormat.BayerGB12Packed),
    VmbPixelFormat.BayerBG12Packed: _query_compatibility(VmbPixelFormat.BayerBG12Packed),
    VmbPixelFormat.BayerGR10p: _query_compatibility(VmbPixelFormat.BayerGR10p),
    VmbPixelFormat.BayerRG10p: _query_compatibility(VmbPixelFormat.BayerRG10p),
    VmbPixelFormat.BayerGB10p: _query_compatibility(VmbPixelFormat.BayerGB10p),
    VmbPixelFormat.BayerBG10p: _query_compatibility(VmbPixelFormat.BayerBG10p),
    VmbPixelFormat.BayerGR12p: _query_compatibility(VmbPixelFormat.BayerGR12p),
    VmbPixelFormat.BayerRG12p: _query_compatibility(VmbPixelFormat.BayerRG12p),
    VmbPixelFormat.BayerGB12p: _query_compatibility(VmbPixelFormat.BayerGB12p),
    VmbPixelFormat.BayerBG12p: _query_compatibility(VmbPixelFormat.BayerBG12p),
    VmbPixelFormat.BayerGR16: _query_compatibility(VmbPixelFormat.BayerGR16),
    VmbPixelFormat.BayerRG16: _query_compatibility(VmbPixelFormat.BayerRG16),
    VmbPixelFormat.BayerGB16: _query_compatibility(VmbPixelFormat.BayerGB16),
    VmbPixelFormat.BayerBG16: _query_compatibility(VmbPixelFormat.BayerBG16),

    VmbPixelFormat.Rgb8: _query_compatibility(VmbPixelFormat.Rgb8),
    VmbPixelFormat.Bgr8: _query_compatibility(VmbPixelFormat.Bgr8),
    VmbPixelFormat.Rgb10: _query_compatibility(VmbPixelFormat.Rgb10),
    VmbPixelFormat.Bgr10: _query_compatibility(VmbPixelFormat.Bgr10),
    VmbPixelFormat.Rgb12: _query_compatibility(VmbPixelFormat.Rgb12),
    VmbPixelFormat.Bgr12: _query_compatibility(VmbPixelFormat.Bgr12),
    VmbPixelFormat.Rgb14: _query_compatibility(VmbPixelFormat.Rgb14),
    VmbPixelFormat.Bgr14: _query_compatibility(VmbPixelFormat.Bgr14),
    VmbPixelFormat.Rgb16: _query_compatibility(VmbPixelFormat.Rgb16),
    VmbPixelFormat.Bgr16: _query_compatibility(VmbPixelFormat.Bgr16),
    VmbPixelFormat.Argb8: _query_compatibility(VmbPixelFormat.Argb8),
    VmbPixelFormat.Rgba8: _query_compatibility(VmbPixelFormat.Rgba8),
    VmbPixelFormat.Bgra8: _query_compatibility(VmbPixelFormat.Bgra8),
    VmbPixelFormat.Rgba10: _query_compatibility(VmbPixelFormat.Rgba10),
    VmbPixelFormat.Bgra10: _query_compatibility(VmbPixelFormat.Bgra10),
    VmbPixelFormat.Rgba12: _query_compatibility(VmbPixelFormat.Rgba12),
    VmbPixelFormat.Bgra12: _query_compatibility(VmbPixelFormat.Bgra12),
    VmbPixelFormat.Rgba14: _query_compatibility(VmbPixelFormat.Rgba14),
    VmbPixelFormat.Bgra14: _query_compatibility(VmbPixelFormat.Bgra14),
    VmbPixelFormat.Rgba16: _query_compatibility(VmbPixelFormat.Rgba16),
    VmbPixelFormat.Bgra16: _query_compatibility(VmbPixelFormat.Bgra16),

    VmbPixelFormat.Yuv411: _query_compatibility(VmbPixelFormat.Yuv411),
    VmbPixelFormat.Yuv422: _query_compatibility(VmbPixelFormat.Yuv422),
    VmbPixelFormat.Yuv444: _query_compatibility(VmbPixelFormat.Yuv444),
    VmbPixelFormat.YCbCr411_8_CbYYCrYY: _query_compatibility(VmbPixelFormat.YCbCr411_8_CbYYCrYY),
    VmbPixelFormat.YCbCr422_8_CbYCrY: _query_compatibility(VmbPixelFormat.YCbCr422_8_CbYCrY),
    VmbPixelFormat.YCbCr8_CbYCr: _query_compatibility(VmbPixelFormat.YCbCr8_CbYCr)
}
