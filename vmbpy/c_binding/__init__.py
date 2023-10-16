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

-------------------------------------------------------------------------

NOTE: Vmb naming convention.
VmbPy is based on VmbC, this submodule contains all wrapped types and functions provided by VmbC to
make them usable from Python. By convention, all VmbC Types and Functions are prefixed with 'Vmb',
this convention is kept for all python types interfacing with the C - Layer. VmbC developers should
be able to understand the interface to VmbC and keeping the name convention helps a lot in that
regard.

However prefixing everything with 'Vmb' is not required in VmbPy, therefore most Types of the public
API have no prefix.
"""

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__all__ = [
    # Exports from vmb_common
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
    'VmbCError',
    'VmbPixelFormat',
    'decode_cstr',
    'decode_flags',

    # Exports from vmb_c
    'VmbTransportLayer',
    'VmbAccessMode',
    'VmbFeatureData',
    'VmbFeaturePersist',
    'VmbModulePersistFlags',
    'VmbFeatureVisibility',
    'VmbFeatureFlags',
    'VmbFrameStatus',
    'VmbPayloadType',
    'VmbFrameFlags',
    'VmbVersionInfo',
    'VmbTransportLayerInfo',
    'VmbInterfaceInfo',
    'VmbCameraInfo',
    'VmbFeatureInfo',
    'VmbFeatureEnumEntry',
    'VmbFrame',
    'VmbFeaturePersistSettings',
    'G_VMB_C_HANDLE',
    'VMB_C_VERSION',
    'EXPECTED_VMB_C_VERSION',
    'call_vmb_c',

    # Exports from vmb_image_transform
    'VmbImage',
    'VmbImageInfo',
    'VmbDebayerMode',
    'VmbTransformInfo',
    'VMB_IMAGE_TRANSFORM_VERSION',
    'EXPECTED_VMB_IMAGE_TRANSFORM_VERSION',
    'call_vmb_image_transform',
    'PIXEL_FORMAT_TO_LAYOUT',
    'LAYOUT_TO_PIXEL_FORMAT',
    'PIXEL_FORMAT_CONVERTIBILITY_MAP',

    # Exports from wrapped_types
    'AccessMode',
    'Debayer',
    'FeatureFlags',
    'FeatureVisibility',
    'FrameStatus',
    'PayloadType',
    'PersistType',
    'ModulePersistFlags',
    'PixelFormat',
    'TransportLayerType',

    # Exports from ctypes
    'byref',
    'sizeof',
    'create_string_buffer'
]

from ctypes import byref, create_string_buffer, sizeof

from .vmb_c import (EXPECTED_VMB_C_VERSION, G_VMB_C_HANDLE, VMB_C_VERSION, VmbAccessMode,
                    VmbCameraInfo, VmbFeatureData, VmbFeatureEnumEntry, VmbFeatureFlags,
                    VmbFeatureInfo, VmbFeaturePersist, VmbFeaturePersistSettings,
                    VmbFeatureVisibility, VmbFrame, VmbFrameFlags, VmbFrameStatus, VmbPayloadType,
                    VmbInterfaceInfo, VmbModulePersistFlags, VmbTransportLayer, VmbTransportLayerInfo,
                    VmbVersionInfo, call_vmb_c)
from .vmb_common import (VmbBool, VmbCError, VmbDouble, VmbError, VmbHandle, VmbInt8, VmbInt16,
                         VmbInt32, VmbInt64, VmbPixelFormat, VmbUchar, VmbUint8, VmbUint16,
                         VmbUint32, VmbUint64, _as_vmb_file_path, _select_vimbax_home, decode_cstr,
                         decode_flags)
from .vmb_image_transform import (EXPECTED_VMB_IMAGE_TRANSFORM_VERSION, LAYOUT_TO_PIXEL_FORMAT,
                                  PIXEL_FORMAT_CONVERTIBILITY_MAP, PIXEL_FORMAT_TO_LAYOUT,
                                  VMB_IMAGE_TRANSFORM_VERSION, VmbDebayerMode, VmbImage,
                                  VmbImageInfo, VmbTransformInfo, call_vmb_image_transform)
from .wrapped_types import (AccessMode, Debayer, FeatureFlags, FeatureVisibility, FrameStatus,
                            PayloadType, ModulePersistFlags, PersistType, PixelFormat, TransportLayerType)
