"""Submodule encapsulating the VimbaCommon access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import ctypes
import enum
import os
import platform
import functools
from typing import Tuple, Optional

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
    'VmbDouble',
    'VmbError',
    'VimbaCError',
    'decode_cstr',
    'decode_flags',
    'fmt_repr',
    'fmt_enum_repr',
    'fmt_flags_repr',
    'get_vimba_home',
    'is_arch_64_bit'
]


# Types
class Int32Enum(enum.IntEnum):
    @classmethod
    def from_param(cls, obj):
        return ctypes.c_int(obj)


class Uint32Enum(enum.IntEnum):
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
VmbDouble = ctypes.c_double


class VmbError(Int32Enum):
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


class VimbaCError(Exception):
    """Error Type containing an error code from the C-Layer. This error code is highly context
       sensitive. All wrapped C-Functions that do not return VmbError.Success or None must
       raise a VimbaCError and the surrounding code must deal if the Error is possible.
    """

    def __init__(self, c_error: VmbError):
        super().__init__(repr(c_error))
        self.__c_error = c_error

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'VimbaCError({})'.format(repr(self.__c_error))

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
        val - Byte sequence to convert into str.

    Returns:
        str represented by 'val'
    """
    return val.decode() if val else ''


def decode_flags(enum_type, enum_val: int):
    """Splits C-styled bit mask into a set of flags from a given Enumeration.

    Arguments:
        enum_val - Bit mask to decode.
        enum_type - Enum Type represented within 'enum_val'

    Returns:
        A set of all values of enum_type occurring in enum_val.

    Raises:
        Attribute error a set value is not within the given 'enum_type'.
    """

    return tuple(_split_flags_into_enum(enum_val, enum_type))


def fmt_repr(fmt: str, val):
    """Append repr to a format string."""
    return fmt.format(repr(val))


def fmt_enum_repr(fmt: str, enum_type, enum_val):
    """Append repr of a given enum type to a format string.

    Arguments:
        fmt - Format string
        enum_type - Enum Type to construct.
        enum_val - Enum value.

    Returns:
        formatted string
    """
    return fmt.format(repr(enum_type(enum_val)))


def fmt_flags_repr(fmt: str, enum_type, enum_val):
    """Append repr of a c-style flag value in the form of a set containing
       all bits set from a given enum_type.

    Arguments:
        fmt - Format string
        enum_type - Enum Type to construct.
        enum_val - Enum value.

    Returns:
        formatted string
    """
    return fmt.format(_repr_flags_list(enum_type, enum_val))


def get_vimba_home() -> Optional[str]:
    """Get Vimba home directory of None is not found"""
    return os.environ.get('VIMBA_HOME')


def is_arch_64_bit() -> bool:
    """True if Host system is a 64 Bit Architecture, False if not."""
    return True if platform.machine() == 'AMD64' else False
