# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

from ctypes import byref, sizeof, c_void_p, POINTER as c_ptr, c_char_p as c_str
from vimba.log import trace_enable
from vimba.error import VimbaCError
from .util import static_var, load_vimba_raw
from .types import VmbBool, VmbUint32, VmbInt64, VmbUint64, VmbDouble, \
                   VmbError, VmbHandle, VmbFeatureEnumEntry, VmbFeatureInfo, \
                   VmbVersionInfo, VmbFrame, VmbFrameCallback, \
                   VmbInvalidationCallback, VmbAccessMode, VmbInterfaceInfo, \
                   VmbCameraInfo, VmbFeaturePersistSettings


# For detailed information on the signatures see "VimbaC.h"
# To improve readability, suppress 'E501 line too long (104 > 79 characters)'
# check of flake8
_SIGNATURES = {
    'VmbVersionQuery': (VmbError, [c_ptr(VmbVersionInfo), VmbUint32]),
    'VmbStartup': (VmbError, None),
    'VmbShutdown': (None, None),
    'VmbCamerasList': (VmbError, [c_ptr(VmbCameraInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                             # noqa: E501
    'VmbCameraInfoQuery': (VmbError, [c_str, c_ptr(VmbCameraInfo), VmbUint32]),
    'VmbCameraOpen': (VmbError, [c_str, VmbAccessMode, c_ptr(VmbHandle)]),
    'VmbCameraClose': (VmbError, [VmbHandle]),
    'VmbFeaturesList': (VmbError, [VmbHandle, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                # noqa: E501
    'VmbFeatureInfoQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32]),                                  # noqa: E501
    'VmbFeatureListAffected': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),  # noqa: E501
    'VmbFeatureListSelected': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),  # noqa: E501
    'VmbFeatureAccessQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool), c_ptr(VmbBool)]),                                  # noqa: E501
    'VmbFeatureIntGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64)]),
    'VmbFeatureIntSet': (VmbError, [VmbHandle, c_str, VmbInt64]),
    'VmbFeatureIntRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64), c_ptr(VmbInt64)]),                              # noqa: E501
    'VmbFeatureIntIncrementQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64)]),                                           # noqa: E501
    'VmbFeatureFloatGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbDouble)]),
    'VmbFeatureFloatSet': (VmbError, [VmbHandle, c_str, VmbDouble]),
    'VmbFeatureFloatRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbDouble), c_ptr(VmbDouble)]),                          # noqa: E501
    'VmbFeatureFloatIncrementQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool), c_ptr(VmbDouble)]),                        # noqa: E501
    'VmbFeatureEnumGet': (VmbError, [VmbHandle, c_str, c_ptr(c_str)]),
    'VmbFeatureEnumSet': (VmbError, [VmbHandle, c_str, c_str]),
    'VmbFeatureEnumRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(c_str), VmbUint32, c_ptr(VmbUint32)]),                    # noqa: E501
    'VmbFeatureEnumIsAvailable': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbBool)]),                                       # noqa: E501
    'VmbFeatureEnumAsInt': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbInt64)]),                                            # noqa: E501
    'VmbFeatureEnumAsString': (VmbError, [VmbHandle, c_str, VmbInt64, c_ptr(c_str)]),                                         # noqa: E501
    'VmbFeatureEnumEntryGet': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbFeatureEnumEntry)]),                              # noqa: E501
    'VmbFeatureStringGet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32, c_ptr(VmbUint32)]),                                # noqa: E501
    'VmbFeatureStringSet': (VmbError, [VmbHandle, c_str, c_str]),
    'VmbFeatureStringMaxlengthQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbUint32)]),                                       # noqa: E501
    'VmbFeatureBoolGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool)]),
    'VmbFeatureBoolSet': (VmbError, [VmbHandle, c_str, VmbBool]),
    'VmbFeatureCommandRun': (VmbError, [VmbHandle, c_str]),
    'VmbFeatureCommandIsDone': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool)]),
    'VmbFeatureRawGet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32, c_ptr(VmbUint32)]),                                   # noqa: E501
    'VmbFeatureRawSet': (VmbError, [VmbHandle, c_str, c_str, VmbUint32]),
    'VmbFeatureRawLengthQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbUint32)]),                                             # noqa: E501
    'VmbFeatureInvalidationRegister': (VmbError, [VmbHandle, c_str, VmbInvalidationCallback, c_void_p]),                      # noqa: E501
    'VmbFeatureInvalidationUnregister': (VmbError, [VmbHandle, c_str, VmbInvalidationCallback]),                              # noqa: E501
    'VmbFrameAnnounce': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbFrameRevoke': (VmbError, [VmbHandle, c_ptr(VmbFrame)]),
    'VmbFrameRevokeAll': (VmbError, [VmbHandle]),
    'VmbCaptureStart': (VmbError, [VmbHandle]),
    'VmbCaptureEnd': (VmbError, [VmbHandle]),
    'VmbCaptureFrameQueue': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbFrameCallback]),                                       # noqa: E501
    'VmbCaptureFrameWait': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbCaptureQueueFlush': (VmbError, [VmbHandle]),
    'VmbInterfacesList': (VmbError, [c_ptr(VmbInterfaceInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                       # noqa: E501
    'VmbInterfaceOpen': (VmbError, [c_str, c_ptr(VmbHandle)]),
    'VmbInterfaceClose': (VmbError, [VmbHandle]),
    'VmbAncillaryDataOpen': (VmbError, [c_ptr(VmbFrame), c_ptr(VmbHandle)]),
    'VmbAncillaryDataClose': (VmbError, [VmbHandle]),
    'VmbMemoryRead': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),                                  # noqa: E501
    'VmbMemoryWrite': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),                                 # noqa: E501
    'VmbRegistersRead': (VmbError, [VmbHandle, VmbUint32, c_ptr(VmbUint64), c_ptr(VmbUint64), c_ptr(VmbUint32)]),             # noqa: E501
    'VmbRegistersWrite': (VmbError, [VmbHandle, VmbUint32, c_ptr(VmbUint64), c_ptr(VmbUint64), c_ptr(VmbUint32)]),            # noqa: E501
    'VmbCameraSettingsSave': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32]),                     # noqa: E501
    'VmbCameraSettingsLoad': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32])                      # noqa: E501
}


def _load_vimba():
    return _check_version(_attach_signatures(load_vimba_raw()))


def _attach_signatures(vimba_handle):
    # Apply given signatures onto loaded library
    for function_name, signature in _SIGNATURES.items():
        fn = getattr(vimba_handle, function_name)
        fn.restype, fn.argtypes = signature
        fn.errcheck = _eval_vmberror

    return vimba_handle


def _eval_vmberror(result, func, args):
    if result not in (None, VmbError.Success):
        raise VimbaCError(result)


def _check_version(vimba_handle):
    ver = VmbVersionInfo()
    vimba_handle.VmbVersionQuery(byref(ver), sizeof(ver))

    assert str(ver) == EXPECTED_VIMBA_C_VERSION, \
        'Unsupported VimbaC Version: Expected: {}, Found: {}'\
        .format(EXPECTED_VIMBA_C_VERSION, ver)

    return vimba_handle


# Exposed Interface
EXPECTED_VIMBA_C_VERSION = '1.8.0'


@static_var("_vimba_instance", _load_vimba())
@trace_enable()
def call_vimba_c_func(func_name, *args):
    getattr(call_vimba_c_func._vimba_instance, func_name)(*args)


def print_vimba_c_func_signatures():
    for func, signature in _SIGNATURES.items():
        res, args = signature
        print('func={}, return_type={}, args_types={}'.format(func, res, args))
