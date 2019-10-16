"""Submodule encapsulating the VimbaC access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__all__ = [
    # Exports from vimba_common
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
    'VmbPixelFormat',
    'decode_cstr',
    'decode_flags',

    # Exports from vimba_c
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
    'G_VIMBA_C_HANDLE',
    'EXPECTED_VIMBA_C_VERSION',
    'call_vimba_c',

    # Exports from vimba_image_transform
    'VmbTechInfo',
    'VmbImage',
    'VmbImageInfo',
    'EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION',
    'call_vimba_image_transform',
    'PIXEL_FORMAT_TO_LAYOUT',
    'LAYOUT_TO_PIXEL_FORMAT',
    'PIXEL_FORMAT_CONVERTIBILTY_MAP',

    # Exports from ctypes
    'byref',
    'sizeof',
    'create_string_buffer'
]

from .vimba_common import VmbInt8, VmbUint8, VmbInt16, VmbUint16, VmbInt32, VmbUint32, \
                          VmbInt64, VmbUint64, VmbHandle, VmbBool, VmbUchar, VmbDouble, VmbError, \
                          VimbaCError, VmbPixelFormat, decode_cstr, decode_flags

from .vimba_c import VmbInterface, VmbAccessMode, VmbFeatureData, \
                   VmbFeaturePersist, VmbFeatureVisibility, VmbFeatureFlags, VmbFrameStatus, \
                   VmbFrameFlags, VmbVersionInfo, VmbInterfaceInfo, VmbCameraInfo, VmbFeatureInfo, \
                   VmbFeatureEnumEntry, VmbFrame, VmbFeaturePersistSettings, \
                   VmbInvalidationCallback, VmbFrameCallback, G_VIMBA_C_HANDLE, \
                   EXPECTED_VIMBA_C_VERSION, call_vimba_c

from .vimba_image_transform import VmbTechInfo, VmbImage, VmbImageInfo, \
                                   EXPECTED_VIMBA_IMAGE_TRANSFORM_VERSION, \
                                   call_vimba_image_transform, PIXEL_FORMAT_TO_LAYOUT, \
                                   LAYOUT_TO_PIXEL_FORMAT, PIXEL_FORMAT_CONVERTIBILTY_MAP

from ctypes import byref, sizeof, create_string_buffer
