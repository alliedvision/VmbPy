"""Access to VimbaC API.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from ctypes import CDLL, byref, sizeof, c_void_p, POINTER as c_ptr, c_char_p as c_str
from typing import Any, Callable, Tuple
from vimba.util import TraceEnable
from vimba.error import VimbaSystemError
from .util import load_vimba_raw
from .types import VmbBool, VmbUint32, VmbInt64, VmbUint64, VmbDouble, VmbError, VmbHandle, \
                   VmbFeatureEnumEntry, VmbFeatureInfo, VmbVersionInfo, VmbFrame, \
                   VmbInvalidationCallback, VmbAccessMode, VmbInterfaceInfo, \
                   VmbCameraInfo, VmbFeaturePersistSettings, VimbaCError


__all__ = [
    'EXPECTED_VIMBA_C_VERSION',
    'call_vimba_c_func',
]

EXPECTED_VIMBA_C_VERSION = '1.8.0'

# For detailed information on the signatures see "VimbaC.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbVersionQuery': (VmbError, [c_ptr(VmbVersionInfo), VmbUint32]),
    'VmbStartup': (VmbError, None),
    'VmbShutdown': (None, None),
    'VmbCamerasList': (VmbError, [c_ptr(VmbCameraInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),
    'VmbCameraInfoQuery': (VmbError, [c_str, c_ptr(VmbCameraInfo), VmbUint32]),
    'VmbCameraOpen': (VmbError, [c_str, VmbAccessMode, c_ptr(VmbHandle)]),
    'VmbCameraClose': (VmbError, [VmbHandle]),
    'VmbFeaturesList': (VmbError, [VmbHandle, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                # noqa: E501
    'VmbFeatureInfoQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32]),
    'VmbFeatureListAffected': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),  # noqa: E501
    'VmbFeatureListSelected': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),  # noqa: E501
    'VmbFeatureAccessQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool), c_ptr(VmbBool)]),
    'VmbFeatureIntGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64)]),
    'VmbFeatureIntSet': (VmbError, [VmbHandle, c_str, VmbInt64]),
    'VmbFeatureIntRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64), c_ptr(VmbInt64)]),                              # noqa: E501
    'VmbFeatureIntIncrementQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64)]),
    'VmbFeatureFloatGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbDouble)]),
    'VmbFeatureFloatSet': (VmbError, [VmbHandle, c_str, VmbDouble]),
    'VmbFeatureFloatRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbDouble), c_ptr(VmbDouble)]),
    'VmbFeatureFloatIncrementQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool), c_ptr(VmbDouble)]),                        # noqa: E501
    'VmbFeatureEnumGet': (VmbError, [VmbHandle, c_str, c_ptr(c_str)]),
    'VmbFeatureEnumSet': (VmbError, [VmbHandle, c_str, c_str]),
    'VmbFeatureEnumRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(c_str), VmbUint32, c_ptr(VmbUint32)]),                    # noqa: E501
    'VmbFeatureEnumIsAvailable': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbBool)]),
    'VmbFeatureEnumAsInt': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbInt64)]),
    'VmbFeatureEnumAsString': (VmbError, [VmbHandle, c_str, VmbInt64, c_ptr(c_str)]),
    'VmbFeatureEnumEntryGet': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbFeatureEnumEntry)]),                              # noqa: E501
    'VmbFeatureStringGet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32, c_ptr(VmbUint32)]),                                # noqa: E501
    'VmbFeatureStringSet': (VmbError, [VmbHandle, c_str, c_str]),
    'VmbFeatureStringMaxlengthQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbUint32)]),
    'VmbFeatureBoolGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool)]),
    'VmbFeatureBoolSet': (VmbError, [VmbHandle, c_str, VmbBool]),
    'VmbFeatureCommandRun': (VmbError, [VmbHandle, c_str]),
    'VmbFeatureCommandIsDone': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool)]),
    'VmbFeatureRawGet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32, c_ptr(VmbUint32)]),
    'VmbFeatureRawSet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32]),
    'VmbFeatureRawLengthQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbUint32)]),
    'VmbFeatureInvalidationRegister': (VmbError, [VmbHandle, c_str, VmbInvalidationCallback, c_void_p]),                      # noqa: E501
    'VmbFeatureInvalidationUnregister': (VmbError, [VmbHandle, c_str, VmbInvalidationCallback]),
    'VmbFrameAnnounce': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbFrameRevoke': (VmbError, [VmbHandle, c_ptr(VmbFrame)]),
    'VmbFrameRevokeAll': (VmbError, [VmbHandle]),
    'VmbCaptureStart': (VmbError, [VmbHandle]),
    'VmbCaptureEnd': (VmbError, [VmbHandle]),
    'VmbCaptureFrameQueue': (VmbError, [VmbHandle, c_ptr(VmbFrame), c_void_p]),
    'VmbCaptureFrameWait': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbCaptureQueueFlush': (VmbError, [VmbHandle]),
    'VmbInterfacesList': (VmbError, [c_ptr(VmbInterfaceInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                       # noqa: E501
    'VmbInterfaceOpen': (VmbError, [c_str, c_ptr(VmbHandle)]),
    'VmbInterfaceClose': (VmbError, [VmbHandle]),
    'VmbAncillaryDataOpen': (VmbError, [c_ptr(VmbFrame), c_ptr(VmbHandle)]),
    'VmbAncillaryDataClose': (VmbError, [VmbHandle]),
    'VmbMemoryRead': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbMemoryWrite': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbRegistersRead': (VmbError, [VmbHandle, VmbUint32, c_ptr(VmbUint64), c_ptr(VmbUint64), c_ptr(VmbUint32)]),             # noqa: E501
    'VmbRegistersWrite': (VmbError, [VmbHandle, VmbUint32, c_ptr(VmbUint64), c_ptr(VmbUint64), c_ptr(VmbUint32)]),            # noqa: E501
    'VmbCameraSettingsSave': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32]),                     # noqa: E501
    'VmbCameraSettingsLoad': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32])                      # noqa: E501
}


def _load_vimba() -> CDLL:
    return _check_version(_attach_signatures(load_vimba_raw()))


def _attach_signatures(vimba_handle: CDLL) -> CDLL:
    # Apply given signatures onto loaded library
    for function_name, signature in _SIGNATURES.items():
        fn = getattr(vimba_handle, function_name)
        fn.restype, fn.argtypes = signature
        fn.errcheck = _eval_vmberror

    return vimba_handle


def _eval_vmberror(result: VmbError, func: Callable[..., Any], *args: Tuple[Any, ...]):
    if result not in (VmbError.Success, None):
        raise VimbaCError(result)


def _check_version(vimba_handle: CDLL) -> CDLL:
    ver = VmbVersionInfo()
    vimba_handle.VmbVersionQuery(byref(ver), sizeof(ver))

    if (str(ver) != EXPECTED_VIMBA_C_VERSION):
        msg = 'Invalid VimbaC Version: Expected: {}, Found:{}'
        raise VimbaSystemError(msg.format(EXPECTED_VIMBA_C_VERSION, str(ver)))

    return vimba_handle


_vimba_instance: CDLL = _load_vimba()


@TraceEnable()
def call_vimba_c_func(func_name: str, *args):
    """This function encapsulates the entire VimbaC access.

    For Details on valid function signatures see the 'VimbaC.h'.

    Arguments:
        func_name: The function name from VimbaC to be called.
        args: Varargs passed directly to the underlaying C-Function.

    Raises:
        TypeError if given are do not match the signature of the function.
        AttributeError if func with name 'func_name' does not exist.
        VimbaCError if the function call is valid but neither None or VmbError.Success was returned.

    The following functions of VimbaC can be executed:
        VmbVersionQuery
        VmbStartup
        VmbShutdown
        VmbCamerasList
        VmbCameraInfoQuery
        VmbCameraOpen
        VmbCameraClose
        VmbFeaturesList
        VmbFeatureInfoQuery
        VmbFeatureListAffected
        VmbFeatureListSelected
        VmbFeatureAccessQuery
        VmbFeatureIntGet
        VmbFeatureIntSet
        VmbFeatureIntRangeQuery
        VmbFeatureIntIncrementQuery
        VmbFeatureFloatGet
        VmbFeatureFloatSet
        VmbFeatureFloatRangeQuery
        VmbFeatureFloatIncrementQuery
        VmbFeatureEnumGet
        VmbFeatureEnumSet
        VmbFeatureEnumRangeQuery
        VmbFeatureEnumIsAvailable
        VmbFeatureEnumAsInt
        VmbFeatureEnumAsString
        VmbFeatureEnumEntryGet
        VmbFeatureStringGet
        VmbFeatureStringSet
        VmbFeatureStringMaxlengthQuery
        VmbFeatureBoolGet
        VmbFeatureBoolSet
        VmbFeatureCommandRun
        VmbFeatureCommandIsDone
        VmbFeatureRawGet
        VmbFeatureRawSet
        VmbFeatureRawLengthQuery
        VmbFeatureInvalidationRegister
        VmbFeatureInvalidationUnregister
        VmbFrameAnnounce
        VmbFrameRevoke
        VmbFrameRevokeAll
        VmbCaptureStart
        VmbCaptureEnd
        VmbCaptureFrameQueue
        VmbCaptureFrameWait
        VmbCaptureQueueFlush
        VmbInterfacesList
        VmbInterfaceOpen
        VmbInterfaceClose
        VmbAncillaryDataOpen
        VmbAncillaryDataClose
        VmbMemoryRead
        VmbMemoryWrite
        VmbRegistersRead
        VmbRegistersWrite
        VmbCameraSettingsSave
        VmbCameraSettingsLoad
    """
    global _vimba_instance

    getattr(_vimba_instance, func_name)(*args)
