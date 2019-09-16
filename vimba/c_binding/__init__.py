# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__all__ = [
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
    'VmbPixelFormat',
    'VmbInterface',
    'VmbAccessMode',
    'VmbFeatureData',
    'VmbFeaturePersist',
    'VmbFeatureVisibility',
    'VmbFeatureFlags',
    'VmbFrameStatus',
    'VmbFrameFlags',
    'VmbVersionInfo',
    'VmbInterfaceInfo',
    'VmbCameraInfo',
    'VmbFeatureInfo',
    'VmbFeatureEnumEntry',
    'VmbFrame',
    'VmbFeaturePersistSettings',
    'VmbInvalidationCallback',
    'VmbFrameCallback',
    'G_VIMBA_HANDLE',
    'VimbaCError',

    'EXPECTED_VIMBA_C_VERSION',
    'call_vimba_c_func',
    'print_vimba_c_func_signatures',

    'decode_cstr',
    'decode_flags',

    'byref',
    'sizeof',
    'create_string_buffer'
]

from .types import VmbInt8,  VmbUint8,  VmbInt16,  VmbUint16,  VmbInt32, VmbUint32, VmbInt64, \
                   VmbUint64, VmbHandle, VmbBool, VmbUchar, VmbDouble, VmbError, VmbPixelFormat, \
                   VmbInterface, VmbAccessMode, VmbFeatureData, VmbFeaturePersist, \
                   VmbFeatureVisibility, VmbFeatureFlags, VmbFrameStatus, VmbFrameFlags, \
                   VmbVersionInfo, VmbInterfaceInfo, VmbCameraInfo, VmbFeatureInfo, \
                   VmbFeatureEnumEntry, VmbFrame, VmbFeaturePersistSettings, \
                   VmbInvalidationCallback, VmbFrameCallback, G_VIMBA_HANDLE, VimbaCError

from .api import EXPECTED_VIMBA_C_VERSION, call_vimba_c_func, print_vimba_c_func_signatures

from .util import decode_cstr, decode_flags

# Alias for commonly used ctypes helper functions
from ctypes import byref, sizeof, create_string_buffer
