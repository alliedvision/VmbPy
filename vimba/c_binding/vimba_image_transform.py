"""Submodule encapsulating the VimbaImageTransform access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import ctypes

from ctypes import byref, POINTER as c_ptr
from typing import Callable, Any, Tuple

from ..error import VimbaSystemError
from ..util import TraceEnable
from .vimba_common import VmbUint32, VmbError, VimbaCError, load_vimba_lib


EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION = '1.6'

# For detailed information on the signatures see "VimbaImageTransform.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbGetVersion': (VmbError, [c_ptr(VmbUint32)])
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
    """

    global _lib_instance
    getattr(_lib_instance, func_name)(*args)
