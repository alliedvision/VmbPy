# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
import platform
import functools
import ctypes

from os.path import join


def static_var(var, val):
    def decorate(func):
        setattr(func, var, val)
        return func

    return decorate


def _split_into_powers_of_two(num: int):
    result = []
    for mask in [1 << i for i in range(32)]:
        if mask & num:
            result.append(mask)

    if not result:
        result.append(0)

    return tuple(result)


def _split_flags_into_enum(num: int, enum_type):
    return [enum_type(val) for val in _split_into_powers_of_two(num)]


def _stringify_enum_list(enum_type, flag_val: int, string_func):
    values = _split_flags_into_enum(flag_val, enum_type)

    if values:
        def fold_func(acc, arg):
            return '{} {}'.format(acc, string_func(arg))

        return functools.reduce(fold_func, values, '')

    else:
        return '{}'.format(string_func(enum_type(0)))


def decode_cstr(val: bytes) -> str:
    return val.decode() if val else ''


def decode_flags(enum_type, enum_val: int):
    return tuple(_split_flags_into_enum(enum_val, enum_type))


def fmt_str(fmt: str, val):
    return fmt.format(str(val))


def fmt_cstr_str(fmt: str, val: ctypes.c_char_p) -> str:
    return fmt.format('"{}"'.format(val.value.decode() if val.value else ''))


def fmt_enum_str(fmt: str, enum_type, enum_val):
    return fmt.format(str(enum_type(enum_val)))


def fmt_flags_str(fmt: str, enum_type, enum_val):
    return fmt.format(_stringify_enum_list(enum_type, enum_val, str))


def fmt_repr(fmt: str, val):
    return fmt.format(repr(val))


def fmt_enum_repr(fmt: str, enum_type, enum_val):
    return fmt.format(repr(enum_type(enum_val)))


def fmt_flags_repr(fmt: str, enum_type, enum_val):
    return fmt.format(_stringify_enum_list(enum_type, enum_val, repr))


def load_vimba_raw():
    platform_handlers = {
        'linux': _load_under_linux,
        'win32': _load_under_windows
    }

    if sys.platform not in platform_handlers:
        raise OSError('Abort. Unsupported Platform ({}) detected.'
                      .format(sys.platform))

    return platform_handlers[sys.platform]()


def _get_vimba_home():
    try:
        vimba_home = os.environ['VIMBA_HOME']

    except KeyError:
        vimba_home = None

    return vimba_home


def _load_under_linux():
    # TODO: Implement loading under Linux.
    raise NotImplementedError('Loading of libVimbaC.so')


def _load_under_windows():
    vimba_home = _get_vimba_home()

    if vimba_home:
        arch = 'Win64' if _get_arch() == '64Bit' else 'Win32'
        lib_path = join(vimba_home, 'VimbaC', 'Bin', arch, 'VimbaC.dll')

    else:
        # TODO: Clarify if additional search is required
        raise NotImplementedError('Loading of VimbaC.dll')

    return ctypes.cdll.LoadLibrary(lib_path)


def _get_arch():
    arch = platform.machine()
    if arch == 'AMD64':
        return '64Bit'

    elif arch == 'i386':
        return '32Bit'

    else:
        raise OSError('Unknown OS Architecture')
