# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
import platform

from os.path import join
from ctypes import cdll


def static_var(var, val):
    def decorate(func):
        setattr(func, var, val)
        return func

    return decorate


def load_vimba_raw():
    platform_handlers = {
        'linux': _load_under_linux,
        'win32': _load_under_windows
    }

    if sys.platform not in platform_handlers:
        raise OSError('Abort. Unsupported Platform ({}) detected.'
                      .format(sys.platform))

    return platform_handlers[sys.platform]()


def decompose_into_powers_of_two(num: int):
    result = []
    powers = [2**i for i in range(32) if 2**i < num]

    for power in powers:
        if num & power:
            result.append(power)

    return result


def decompose_flags_to_enum(num: int, enum_type):
    result = decompose_into_powers_of_two(num)

    for i in range(len(result)):
        result[i] = enum_type(result[i])

    return result


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

    return cdll.LoadLibrary(lib_path)


def _get_arch():
    arch = platform.machine()
    if arch == 'AMD64':
        return '64Bit'

    elif arch == 'i386':
        return '32Bit'

    else:
        raise OSError('Unknown OS Architecture')
