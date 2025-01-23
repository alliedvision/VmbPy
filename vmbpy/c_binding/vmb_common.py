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
# Disable flake8 line length error for this file due to long lines in Pixel formats. Unfortunately
# disabling errors only in a particular block seems currently not possible
# flake8: noqa E501

import ctypes
import functools
import os
import platform
import sys
from typing import List, Tuple, Optional

from ..error import VmbSystemError
from ..util import VmbIntEnum, VmbFlagEnum, Log

__all__ = [
    'Int32Enum',
    'Uint32Enum',
    'VmbInt8',
    'VmbUint8',
    'VmbInt16',
    'VmbUint16',
    'VmbInt32',
    'VmbUint32',
    'VmbInt64',
    'VmbUint64',
    'VmbHandle',
    'VmbBool',
    'VmbUchar',
    'VmbFloat',
    'VmbDouble',
    'VmbError',
    'VmbCError',
    'VmbPixelFormat',
    'decode_cstr',
    'decode_flags',
    'fmt_repr',
    'fmt_enum_repr',
    'fmt_flags_repr',
    'load_vimbax_lib'
]


# Types
class Int32Enum(VmbIntEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_int(obj)


class Uint32Enum(VmbIntEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_uint(obj)


class Uint32Flag(VmbFlagEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_uint(obj)


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
VmbFloat = ctypes.c_float
VmbDouble = ctypes.c_double
# hint: use _as_vmb_file_path to convert a python string to VmbFilePathChar for use with VmbC
if sys.platform == 'win32':
    VmbFilePathChar = ctypes.c_wchar
else:
    VmbFilePathChar = ctypes.c_char


class VmbError(Int32Enum):
    """Enum containing error types returned."""
    Success = 0                    #: No error
    InternalFault = -1             #: Unexpected fault in VmbC or driver
    ApiNotStarted = -2             #: VmbStartup() was not called before the current command
    NotFound = -3                  #: The designated instance (camera, feature etc.) cannot be found
    BadHandle = -4                 #: The given handle is not valid
    DeviceNotOpen = -5             #: Device was not opened for usage
    InvalidAccess = -6             #: Operation is invalid with the current access mode
    BadParameter = -7              #: One of the parameters is invalid (usually an illegal pointer)
    StructSize = -8                #: The given struct size is not valid for this version of the API
    MoreData = -9                  #: More data available in a string/list than space is provided
    WrongType = -10                #: Wrong feature type for this access function
    InvalidValue = -11             #: The value is not valid; either out of bounds or not an increment of the minimum
    Timeout = -12                  #: Timeout during wait
    Other = -13                    #: Other error
    Resources = -14                #: Resources not available (e.g. memory)
    InvalidCall = -15              #: Call is invalid in the current context (e.g. callback)
    NoTL = -16                     #: No transport layers are found
    NotImplemented_ = -17          #: API feature is not implemented
    NotSupported = -18             #: API feature is not supported
    Incomplete = -19               #: The current operation was not completed
    IO = -20                       #: Low level IO error in transport layer
    ValidValueSetNotPresent = -21  #: The valid value set could not be retrieved, since the feature does not provide this property
    GenTLUnspecified = -22         #: Unspecified GenTL runtime error
    Unspecified = -23              #: Unspecified runtime error
    Busy = -24                     #: The responsible module/entity is busy executing actions
    NoData = -25                   #: The function has no data to work on
    ParsingChunkData = -26         #: An error occurred parsing a buffer containing chunk data
    InUse = -27                    #: Something is already in use
    Unknown = -28                  #: Error condition unknown
    Xml = -29                      #: Error parsing XML
    NotAvailable = -30             #: Something is not available
    NotInitialized = -31           #: Something is not initialized
    InvalidAddress = -32           #: The given address is out of range or invalid for internal reasons
    Already = -33                  #: Something has already been done
    NoChunkData = -34              #: A frame expected to contain chunk data does not contain chunk data
    UserCallbackException = -35    #: A callback provided by the user threw an exception
    FeaturesUnavailable = -36      #: The XML for the module is currently not loaded; the module could be in the wrong state or the XML could not be retrieved or could not be parsed properly
    TLNotFound = -37               #: A required transport layer could not be found or loaded
    Ambiguous = -39                #: An entity cannot be uniquely identified based on the information provided
    RetriesExceeded = -40          #: Something could not be accomplished with a given number of retries
    InsufficientBufferCount = -41  #: The operation requires more buffers
    Custom = 1                     #: The minimum error code to use for user defined error codes to avoid conflict with existing error codes

    def __str__(self):
        return self._name_


class _VmbPixel(Uint32Enum):
    Mono = 0x01000000
    Color = 0x02000000


class _VmbPixelOccupy(Uint32Enum):
    Bit8 = 0x00080000
    Bit10 = 0x000A0000
    Bit12 = 0x000C0000
    Bit14 = 0x000E0000
    Bit16 = 0x00100000
    Bit24 = 0x00180000
    Bit32 = 0x00200000
    Bit48 = 0x00300000
    Bit64 = 0x00400000

class VmbPixelFormat(Uint32Enum):
    """Enum containing Pixelformats."""
    None_ = 0
    Mono8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0001                  #: Monochrome, 8 bits (PFNC:Mono8)
    Mono10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0003                #: Monochrome, 10 bits in 16 bits (PFNC:Mono10)
    Mono10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0046               #: Monochrome, 4x10 bits continuously packed in 40 bits (PFNC:Mono10p)
    Mono12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0005                #: Monochrome, 12 bits in 16 bits (PFNC:Mono12)
    Mono12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0006          #: Monochrome, 2x12 bits in 24 bits (GEV:Mono12Packed)
    Mono12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0047               #: Monochrome, 2x12 bits continuously packed in 24 bits (PFNC:Mono12p)
    Mono14 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0025                #: Monochrome, 14 bits in 16 bits (PFNC:Mono14)
    Mono16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0007                #: Monochrome, 16 bits (PFNC:Mono16)
    BayerGR8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0008               #: Bayer-color, 8 bits, starting with GR line (PFNC:BayerGR8)
    BayerRG8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x0009               #: Bayer-color, 8 bits, starting with RG line (PFNC:BayerRG8)
    BayerGB8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x000A               #: Bayer-color, 8 bits, starting with GB line (PFNC:BayerGB8)
    BayerBG8 = _VmbPixel.Mono | _VmbPixelOccupy.Bit8 | 0x000B               #: Bayer-color, 8 bits, starting with BG line (PFNC:BayerBG8)
    BayerGR10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000C             #: Bayer-color, 10 bits in 16 bits, starting with GR line (PFNC:BayerGR10)
    BayerRG10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000D             #: Bayer-color, 10 bits in 16 bits, starting with RG line (PFNC:BayerRG10)
    BayerGB10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000E             #: Bayer-color, 10 bits in 16 bits, starting with GB line (PFNC:BayerGB10)
    BayerBG10 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x000F             #: Bayer-color, 10 bits in 16 bits, starting with BG line (PFNC:BayerBG10)
    BayerGR12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0010             #: Bayer-color, 12 bits in 16 bits, starting with GR line (PFNC:BayerGR12)
    BayerRG12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0011             #: Bayer-color, 12 bits in 16 bits, starting with RG line (PFNC:BayerRG12)
    BayerGB12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0012             #: Bayer-color, 12 bits in 16 bits, starting with GB line (PFNC:BayerGB12)
    BayerBG12 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0013             #: Bayer-color, 12 bits in 16 bits, starting with BG line (PFNC:BayerBG12)
    BayerGR12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002A       #: Bayer-color, 2x12 bits in 24 bits, starting with GR line (GEV:BayerGR12Packed)
    BayerRG12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002B       #: Bayer-color, 2x12 bits in 24 bits, starting with RG line (GEV:BayerRG12Packed)
    BayerGB12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002C       #: Bayer-color, 2x12 bits in 24 bits, starting with GB line (GEV:BayerGB12Packed)
    BayerBG12Packed = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x002D       #: Bayer-color, 2x12 bits in 24 bits, starting with BG line (GEV:BayerBG12Packed)
    BayerGR10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0056            #: Bayer-color, 4x10 bits continuously packed in 40 bits, starting with GR line (PFNC:BayerGR10p)
    BayerRG10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0058            #: Bayer-color, 4x10 bits continuously packed in 40 bits, starting with RG line (PFNC:BayerRG10p)
    BayerGB10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0054            #: Bayer-color, 4x10 bits continuously packed in 40 bits, starting with GB line (PFNC:BayerGB10p)
    BayerBG10p = _VmbPixel.Mono | _VmbPixelOccupy.Bit10 | 0x0052            #: Bayer-color, 4x10 bits continuously packed in 40 bits, starting with BG line (PFNC:BayerBG10p)
    BayerGR12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0057            #: Bayer-color, 2x12 bits continuously packed in 24 bits, starting with GR line (PFNC:BayerGR12p)
    BayerRG12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0059            #: Bayer-color, 2x12 bits continuously packed in 24 bits, starting with RG line (PFNC:BayerRG12p)
    BayerGB12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0055            #: Bayer-color, 2x12 bits continuously packed in 24 bits, starting with GB line (PFNC:BayerGB12p)
    BayerBG12p = _VmbPixel.Mono | _VmbPixelOccupy.Bit12 | 0x0053            #: Bayer-color, 2x12 bits continuously packed in 24 bits, starting with BG line (PFNC:BayerBG12p)
    BayerGR16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x002E             #: Bayer-color, 16 bits, starting with GR line (PFNC:BayerGR16)
    BayerRG16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x002F             #: Bayer-color, 16 bits, starting with RG line (PFNC:BayerRG16)
    BayerGB16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0030             #: Bayer-color, 16 bits, starting with GB line (PFNC:BayerGB16)
    BayerBG16 = _VmbPixel.Mono | _VmbPixelOccupy.Bit16 | 0x0031             #: Bayer-color, 16 bits, starting with BG line (PFNC:BayerBG16)
    Rgb8 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0014                 #: RGB, 8 bits x 3 (PFNC:RGB8)
    Bgr8 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0015                 #: BGR, 8 bits x 3 (PFNC:Bgr8)
    Rgb10 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0018                #: RGB, 10 bits in 16 bits x 3 (PFNC:RGB10)
    Bgr10 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0019                #: BGR, 10 bits in 16 bits x 3 (PFNC:BGR10)
    Rgb12 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x001A                #: RGB, 12 bits in 16 bits x 3 (PFNC:RGB12)
    Bgr12 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x001B                #: BGR, 12 bits in 16 bits x 3 (PFNC:BGR12)
    Rgb14 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x005E                #: RGB, 14 bits in 16 bits x 3 (PFNC:RGB14)
    Bgr14 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x004A                #: BGR, 14 bits in 16 bits x 3 (PFNC:BGR14)
    Rgb16 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x0033                #: RGB, 16 bits x 3 (PFNC:RGB16)
    Bgr16 = _VmbPixel.Color | _VmbPixelOccupy.Bit48 | 0x004B                #: BGR, 16 bits x 3 (PFNC:BGR16)
    Argb8 = _VmbPixel.Color | _VmbPixelOccupy.Bit32 | 0x0016                #: ARGB, 8 bits x 4 (PFNC:RGBa8)
    Rgba8 = Argb8                                                           #: RGBA, 8 bits x 4, legacy name
    Bgra8 = _VmbPixel.Color | _VmbPixelOccupy.Bit32 | 0x0017                #: BGRA, 8 bits x 4 (PFNC:BGRa8)
    Rgba10 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x005F               #: RGBA, 10 bits in 16 bits x 4
    Bgra10 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x004C               #: BGRA, 10 bits in 16 bits x 4
    Rgba12 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0061               #: RGBA, 12 bits in 16 bits x 4
    Bgra12 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x004E               #: BGRA, 12 bits in 16 bits x 4
    Rgba14 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0063               #: RGBA, 14 bits in 16 bits x 4
    Bgra14 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0050               #: BGRA, 14 bits in 16 bits x 4
    Rgba16 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0064               #: RGBA, 16 bits x 4
    Bgra16 = _VmbPixel.Color | _VmbPixelOccupy.Bit64 | 0x0051               #: BGRA, 16 bits x 4
    Yuv411 = _VmbPixel.Color | _VmbPixelOccupy.Bit12 | 0x001E               #: YUV 411 with 8 bits (GEV:YUV411Packed)
    Yuv422 = _VmbPixel.Color | _VmbPixelOccupy.Bit16 | 0x001F               #: YUV 422 with 8 bits (GEV:YUV422Packed)
    Yuv444 = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x0020               #: YUV 444 with 8 bits (GEV:YUV444Packed)
    YCbCr411_8_CbYYCrYY = _VmbPixel.Color | _VmbPixelOccupy.Bit12 | 0x003C  #: YCbCr 411 with 8 bits (PFNC:YCbCr411_8_CbYYCrYY) - identical to Yuv411
    YCbCr422_8_CbYCrY = _VmbPixel.Color | _VmbPixelOccupy.Bit16 | 0x0043    #: YCbCr 422 with 8 bits (PFNC:YCbCr422_8_CbYCrY) - identical to Yuv422
    YCbCr8_CbYCr = _VmbPixel.Color | _VmbPixelOccupy.Bit24 | 0x003A         #: YCbCr 444 with 8 bits (PFNC:YCbCr8_CbYCr) - identical to Yuv444

    def __str__(self):
        return self._name_


class VmbCError(Exception):
    """Error Type containing an error code from the C-Layer. This error code is highly context
       sensitive. All wrapped C-Functions that do not return VmbError.Success or None must
       raise a VmbCError and the surrounding code must deal if the Error is possible.
    """

    def __init__(self, c_error: VmbError):
        super().__init__(repr(c_error))
        self.__c_error = c_error

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'VmbCError({})'.format(repr(self.__c_error))

    def get_error_code(self) -> VmbError:
        """ Get contained Error Code """
        return self.__c_error


# Utility Functions
def _split_into_powers_of_two(num: int) -> Tuple[int, ...]:
    result = []
    for mask in [1 << i for i in range(32)]:
        if mask & num:
            result.append(mask)

    if not result:
        result.append(0)

    return tuple(result)


def _split_flags_into_enum(num: int, enum_type):
    return [enum_type(val) for val in _split_into_powers_of_two(num)]


def _repr_flags_list(enum_type, flag_val: int):
    values = _split_flags_into_enum(flag_val, enum_type)

    if values:
        def fold_func(acc, arg):
            return '{} {}'.format(acc, repr(arg))

        return functools.reduce(fold_func, values, '')

    else:
        return '{}'.format(repr(enum_type(0)))


def decode_cstr(val: bytes) -> str:
    """Converts c_char_p stored in interface structures to a str.

    Arguments:
        val:
            Byte sequence to convert into str.

    Returns:
        str represented by ``val``
    """
    return val.decode() if val else ''


def decode_flags(enum_type, enum_val: int):
    """Splits C-styled bit mask into a set of flags from a given Enumeration.

    Arguments:
        enum_val:
            Bit mask to decode.
        enum_type:
            Enum Type represented within 'enum_val'

    Returns:
        A set of all values of ``enum_type`` occurring in ``enum_val``.

    Raises:
        AttributeError:
            A set value is not within the given ``enum_type``.
    """
    return tuple(_split_flags_into_enum(enum_val, enum_type))


def fmt_repr(fmt: str, val):
    """Append repr to a format string."""
    return fmt.format(repr(val))


def fmt_enum_repr(fmt: str, enum_type, enum_val):
    """Append repr of a given enum type to a format string.

    Arguments:
        fmt:
            Format string
        enum_type:
            Enum Type to construct.
        enum_val:
            Enum value.

    Returns:
        formatted string
    """
    return fmt.format(repr(enum_type(enum_val)))


def fmt_flags_repr(fmt: str, enum_type, enum_val):
    """Append repr of a c-style flag value in the form of a set containing all bits set from a given
       ``enum_type``.

    Arguments:
        fmt:
            Format string
        enum_type:
            Enum Type to construct.
        enum_val:
            Enum value.

    Returns:
        formatted string
    """
    return fmt.format(_repr_flags_list(enum_type, enum_val))


def load_vimbax_lib(vimbax_project: str):
    """Load shared library shipped with the VimbaX installation

    Arguments:
        vimbax_project:
            Library name without prefix or extension

    Return:
        ``CDLL`` or ``WinDLL`` Handle on loaded library

    Raises:
        VmbSystemError:
            If given library could not be loaded.
    """

    platform_handlers = {
        'linux':  _load_under_linux,
        'win32':  _load_under_windows,
        'darwin': _load_under_macos
    }

    if sys.platform not in platform_handlers:
        msg = 'Abort. Unsupported Platform ({}) detected.'
        raise VmbSystemError(msg.format(sys.platform))

    return platform_handlers[sys.platform](vimbax_project)


def _load_under_macos(vimbax_project: str):
    bundled_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', vimbax_project + '.framework', vimbax_project)
    # If file is not included with whl fall back to trying to load from global installation
    if os.path.exists(bundled_lib):
        lib_path = bundled_lib
    else:
        # Assume global installation in /Library/Frameworks by default,
        # but allow user override using VIMBA_X_HOME.
        vimbax_home = os.environ.get('VIMBA_X_HOME')

        if vimbax_home is None:
            vimbax_home = '/Library/Frameworks'

        lib_path = os.path.join(vimbax_home, vimbax_project + '.framework', vimbax_project)

    try:
        Log.get_instance().debug(f'Loading {vimbax_project} from {lib_path}')
        lib = ctypes.cdll.LoadLibrary(lib_path)
    except OSError as e:
        msg = 'Failed to load library \'{}\'. It should have been included as part of the VmbPy ' \
            'or Vimba X installation but can not be found.'
        raise VmbSystemError(msg.format(lib_path)) from e

    return lib


def _load_under_linux(vimbax_project: str):
    lib_name = 'lib{}.so'.format(vimbax_project)
    bundled_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', lib_name)
    # If file is not included with whl fall back to trying to load from VIMBA_X_HOME guess
    if os.path.exists(bundled_lib):
        lib_path = bundled_lib
    else:
        # Construct VIMBA_X_HOME based on TL installation paths
        path_list: List[str] = []
        tl32_path = os.environ.get('GENICAM_GENTL32_PATH', "")
        if tl32_path:
            path_list += tl32_path.split(':')
        tl64_path = os.environ.get('GENICAM_GENTL64_PATH', "")
        if tl64_path:
            path_list += tl64_path.split(':')

        # Remove empty strings from path_list if there are any.
        # Necessary because the GENICAM_GENTLXX_PATH variable might start with a :
        path_list = [path for path in path_list if path]

        # Early return if required variables are not set.
        if not path_list:
            raise VmbSystemError('No TL detected. Please verify Vimba X installation.')

        vimbax_home_candidates: List[str] = []
        for path in path_list:
            # home directory is one up from the cti directory that is added to the
            # GENICAM_GENTLXX_PATH variable
            vimbax_home = os.path.dirname(path)

            # Make sure we do not add the same directory twice
            if vimbax_home not in vimbax_home_candidates:
                vimbax_home_candidates.append(vimbax_home)

        # Select the most likely directory from the candidates
        vimbax_home = _select_vimbax_home(vimbax_home_candidates)
        lib_path = os.path.join(vimbax_home, 'api', 'lib', lib_name)


    try:
        Log.get_instance().debug(f'Loading {vimbax_project} from {lib_path}')
        lib = ctypes.cdll.LoadLibrary(lib_path)

    except OSError as e:
        msg = 'Failed to load library \'{}\'. It should have been included as part of the VmbPy ' \
            'or Vimba X installation but can not be found.'
        raise VmbSystemError(msg.format(lib_path)) from e

    return lib


def _load_under_windows(vimbax_project: str):
    def _load_lib(lib_path: str):
        """Helper to load 64 or 32 bit dlls depending on platform"""
        Log.get_instance().debug(f'Loading {vimbax_project} from {lib_path}')
        load_64bit = True if (platform.machine() == 'AMD64') and _is_python_64_bit() else False
        if load_64bit:
            return ctypes.cdll.LoadLibrary(lib_path)
        else:
            # Tell mypy to ignore this line to allow type checking on both windows and linux as
            # windll is not available on linux and would therefore produce an error there
            return ctypes.windll.LoadLibrary(lib_path)  # type: ignore

    lib_name = '{}.dll'.format(vimbax_project)
    bundled_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', lib_name)
    # If file is not included in whl fall back to trying to load from VIMBA_X_HOME
    if os.path.isfile(bundled_lib):
        lib_path = bundled_lib
    else:
        vimbax_home = os.environ.get('VIMBA_X_HOME')
        if vimbax_home is None:
            msg = 'Expected {} to be included with VmbPy wheel at {} or to find VIMBA_X_HOME ' \
                'variable but could not find either. Please verify the installed VmbPy wheel or ' \
                'the Vimba X installation.'
            raise VmbSystemError(msg.format(vimbax_project, bundled_lib))
        lib_path = os.path.join(vimbax_home, 'api', 'bin', lib_name)
    os.environ["PATH"] = os.path.dirname(lib_path) + os.pathsep + os.environ["PATH"]

    try:
        lib = _load_lib(lib_path)

    except OSError as e:
        # library could not be loaded. Probably missing some dependency. On Windows most likely
        # vcredist is not installed.
        try:
            _load_lib('MSVCP140.dll')
        except OSError as vcredist_error:
            msg = 'Failed to load library \'{}\'. This is likely caused by a missing vcredist ' \
                   'dependency. Please download and install the latest vcredist from microsoft ' \
                   'here: https://aka.ms/vs/17/release/vc_redist.x64.exe'
            raise VmbSystemError(msg.format(lib_path)) from vcredist_error
        msg = 'Failed to load library \'{}\'. It should have been included as part of the VmbPy ' \
            'or Vimba X installation but can not be found.'
        raise VmbSystemError(msg.format(lib_path)) from e

    return lib


def _select_vimbax_home(candidates: List[str]) -> str:
    """
    Select the most likely candidate for ``VIMBA_X_HOME`` from the given list of candidates

    Arguments:
        candidates:
            List of strings pointing to possible VimbaX home directories

    Return:
        Path that represents the most likely ``VIMBA_X_HOME`` directory

    Raises:
        VmbSystemError:
            If multiple ``VIMBA_X_HOME`` directories were found in candidates
    """
    most_likely_candidates = []
    for candidate in candidates:
        if 'vimbax' in candidate.lower():
            most_likely_candidates.append(candidate)

    if len(most_likely_candidates) == 0:
        raise VmbSystemError('No suitable VimbaX installation found. The following paths '
                             'were considered: {}'.format(candidates))
    elif len(most_likely_candidates) > 1:
        raise VmbSystemError('Multiple VimbaX installations found. Can\'t decide which to select: '
                             '{}'.format(most_likely_candidates))

    return most_likely_candidates[0]


def _as_vmb_file_path(file_path: Optional[str]) -> Optional[VmbFilePathChar]:
    """Encode a python string to VmbFilePathChar so it can be passed to VmbC

    Parses a python string object into the appropriate VmbFilePathChar type depending on the used
    operating system. The result of this function may be used to pass the correct encoding of some
    path variable to VmbC functions that expect a VmbFilePathChar input parameter.

    Arguments:
        file_path:
            Python string containing the file path that should be passed to a VmbC function, or
            ``None``. If ``None`` is passed, ``None`` will also be returned so that ctypes may
            interpret it as a nullptr

    Return:
        Given string with correct encoding so that ctypes handles the conversion when passed to a
        VmbC function
    """
    if sys.platform == 'win32':
        return file_path  # type: ignore
    else:
        return file_path.encode('utf-8') if file_path else None  # type: ignore


def _is_python_64_bit() -> bool:
    # Query if the currently running python interpreter is build as 64 bit binary.
    # The default method of getting this information seems to be rather hacky
    # (check if maxint > 2^32) but it seems to be the way to do this....
    return True if sys.maxsize > 2**32 else False
