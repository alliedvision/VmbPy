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
import copy
import ctypes
import os

from ctypes import POINTER as c_ptr
from ctypes import byref
from ctypes import c_char_p
from ctypes import c_char_p as c_str
from ctypes import c_void_p, sizeof
from typing import Any, Callable, Tuple

from ..error import VmbSystemError
from ..util import TraceEnable
from .vmb_common import (Int32Enum, Uint32Enum, Uint32Flag, VmbBool, VmbCError, VmbDouble, VmbError,
                         VmbFilePathChar, VmbHandle, VmbInt32, VmbInt64, VmbPixelFormat, VmbUint8,
                         VmbUint32, VmbUint64, fmt_enum_repr, fmt_flags_repr, fmt_repr,
                         load_vimbax_lib)

__version__ = None

__all__ = [
    'VmbPixelFormat',
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
]

G_VMB_C_HANDLE = VmbHandle((1 << (sizeof(VmbHandle)*8-4)) | 1)

VMB_C_VERSION = None
EXPECTED_VMB_C_VERSION = '1.0.7'

_lib_instance = load_vimbax_lib('VmbC')


# Types
class VmbTransportLayer(Uint32Enum):
    """Camera Interface Types."""
    Unknown = 0   #: Interface is not known to this version of the API
    GEV = 1       #: GigE Vision
    CL = 2        #: Camera Link
    IIDC = 3      #: IIDC 1394
    UVC = 4       #: USB video class
    CXP = 5       #: CoaXPress
    CLHS = 6      #: Camera Link HS
    U3V = 7       #: USB3 Vision Standard
    Ethernet = 8  #: Generic Ethernet
    PCI = 9       #: PCI / PCIe
    Custom = 10   #: Non standard
    Mixed = 11    #: Mixed (transport layer only)

    def __str__(self):
        return self._name_


class VmbAccessMode(Uint32Enum):
    """Camera Access Mode."""
    None_ = 0      #: No access
    Full = 1       #: Read and write access
    Read = 2       #: Read-only access
    Unknown = 4    #: Access type unknown
    Exclusive = 8  #: Read and write access without permitting access for other consumers

    def __str__(self):
        return self._name_


class VmbFeatureData(Uint32Enum):
    """Feature Data Types."""
    Unknown = 0  #: Unknown feature type
    Int = 1      #: 64 bit integer feature
    Float = 2    #: 64 bit floating point feature
    Enum = 3     #: Enumeration feature
    String = 4   #: String feature
    Bool = 5     #: Boolean feature
    Command = 6  #: Command feature
    Raw = 7      #: Raw (direct register access) feature
    None_ = 8    #: Feature with no data

    def __str__(self):
        return self._name_


class VmbFeaturePersist(Uint32Enum):
    """
    Type of features that are to be saved (persisted) to the XML file when using
    VmbCameraSettingsSave
    """
    All = 0         #: Save all features to XML, including look-up tables
    Streamable = 1  #: Save only features marked as streamable, excluding look-up tables
    NoLUT = 2       #: Save all features except look-up tables (default)

    def __str__(self):
        return self._name_


class VmbModulePersistFlags(Uint32Flag):
    """Parameters determining the operation mode of VmbSettingsSave and VmbSettingsLoad."""
    None_ = 0x00           #: Persist/Load features for no module
    TransportLayer = 0x01  #: Persist/Load the transport layer features
    Interface = 0x02       #: Persist/Load the interface features
    RemoteDevice = 0x04    #: Persist/Load the remote device features
    LocalDevice = 0x08     #: Persist/Load the local device features
    Streams = 0x10         #: Persist/Load the features of stream modules
    All = 0xff             #: Persist/Load features for all modules

    def __str__(self):
        return self._name_


class VmbFeatureVisibility(Uint32Enum):
    """Feature Visibility."""
    Unknown = 0    #: Feature visibility is not known
    Beginner = 1   #: Feature is visible in feature list (beginner level)
    Expert = 2     #: Feature is visible in feature list (expert level)
    Guru = 3       #: Feature is visible in feature list (guru level)
    Invisible = 4  #: Feature is not visible in feature list

    def __str__(self):
        return self._name_


class VmbFeatureFlags(Uint32Enum):
    """Feature Flags."""
    None_ = 0         #: No additional information is provided
    Read = 1          #: Static info about read access. Current status depends on access mode, check with VmbFeatureAccessQuery()  # noqa: E501
    Write = 2         #: Static info about write access. Current status depends on access mode, check with VmbFeatureAccessQuery() # noqa: E501
    Undocumented = 4
    Volatile = 8      #: Value may change at any time
    ModifyWrite = 16  #: Value may change after a write

    def __str__(self):
        return self._name_


class VmbFrameStatus(Int32Enum):
    """Frame transfer status."""
    Complete = 0     #: Frame has been completed without errors
    Incomplete = -1  #: Frame could not be filled to the end
    TooSmall = -2    #: Frame buffer was too small
    Invalid = -3     #: Frame buffer was invalid

    def __str__(self):
        return self._name_


class VmbPayloadType(Int32Enum):
    """Frame payload type."""
    Unknown = 0         #: Unknown payload type
    Image = 1           #: Image data
    Raw = 2             #: Raw data
    File = 3            #: File data
    JPEG = 5            #: JPEG data as described in the GigEVision 2.0 specification
    JPEG2000 = 6        #: JPEG 2000 data as described in the GigEVision 2.0 specification
    H264 = 7            #: H.264 data as described in the GigEVision 2.0 specification
    ChunkOnly = 8       #: Chunk data exclusively
    DeviceSpecific = 9  #: Device specific data format
    GenDC = 11          #: GenDC data


class VmbFrameFlags(Uint32Enum):
    """Frame Flags."""
    None_ = 0              #: No additional information is provided
    Dimension = 1          #: Frame's dimension is provided
    Offset = 2             #: Frame's offset is provided (ROI)
    FrameID = 4            #: Frame's ID is provided
    Timestamp = 8          #: Frame's timestamp is provided
    ImageData = 16         #: Frame's imageData is provided
    PayloadType = 32       #: Frame's payloadType is provided
    ChunkDataPresent = 64  #: Frame's chunkDataPresent is set based on info provided by the transport layer # noqa: E501

    def __str__(self):
        return self._name_


class VmbVersionInfo(ctypes.Structure):
    """
    Version Information
        Fields:
            major:
                Type: VmbUint32
                Info: Major version number
            minor:
                Type: VmbUint32
                Info: Minor version number
            patch:
                Type: VmbUint32
                Info: Patch version number
    """
    _fields_ = [
        ("major", VmbUint32),
        ("minor", VmbUint32),
        ("patch", VmbUint32)
    ]

    def __str__(self):
        return '{}.{}.{}'.format(self.major, self.minor, self.patch)

    def __repr__(self):
        rep = 'VmbVersionInfo'
        rep += '(major=' + repr(self.major)
        rep += ',minor=' + repr(self.minor)
        rep += ',patch=' + repr(self.patch)
        rep += ')'
        return rep


class VmbTransportLayerInfo(ctypes.Structure):
    """
        Fields:
            transportLayerIdString:
                Type: c_char_p
                Info: Unique id of the transport layer
            transportLayerName:
                Type: c_char_p
                Info: Name of the transport layer
            transportLayerModelName
                Type: c_char_p
                Info: Model name of the transport layer
            transportLayerVendor:
                Type: c_char_p
                Info: Vendor of the transport layer
            transportLayerVersion:
                Type: c_char_p
                Info: Version of the transport layer
            transportLayerPath:
                Type: c_char_p
                Info: Full path of the transport layer
            transportLayerHandle:
                Type: VmbHandle
                Info: Handle of the transport layer for feature access
            transportLayerType:
                Type: VmbTransportLayer (VmbUint32)
                Info: The type of the transport layer
    """
    _fields_ = [
        ("transportLayerIdString", c_char_p),
        ("transportLayerName", c_char_p),
        ("transportLayerModelName", c_char_p),
        ("transportLayerVendor", c_char_p),
        ("transportLayerVersion", c_char_p),
        ("transportLayerPath", c_char_p),
        ("transportLayerHandle", VmbHandle),
        ("transportLayerType", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbTransportLayerInfo'
        rep += fmt_repr('(transportLayerIdString={}', self.transportLayerIdString)
        rep += fmt_repr(',transportLayerName={}', self.transportLayerName)
        rep += fmt_repr(',transportLayerModelName={}', self.transportLayerModelName)
        rep += fmt_repr(',transportLayerVendor={}', self.transportLayerVendor)
        rep += fmt_repr(',transportLayerVersion={}', self.transportLayerVersion)
        rep += fmt_repr(',transportLayerPath={}', self.transportLayerPath)
        rep += fmt_repr(',transportLayerHandle={}', self.transportLayerHandle)
        rep += fmt_enum_repr(',transportLayerType={}', VmbTransportLayer, self.transportLayerType)
        return rep


class VmbInterfaceInfo(ctypes.Structure):
    """
    Interface information. Holds read-only information about an interface.
        Fields:
            interfaceIdString:
                Type: c_char_p
                Info: Unique identifier for each interface
            interfaceName:
                Type: c_char_p
                Info: Interface name, given by transport layer
            interfaceHandle:
                Type: VmbHandle
                Info: Handle of the interface for feature access
            transportLayerHandle:
                Type: VmbHandle
                Info: Handle of the related transport layer for feature access
            interfaceType:
                Type: VmbTransportLayer (VmbUint32)
                Info: Interface type, see VmbTransportLayer
    """
    _fields_ = [
        ("interfaceIdString", c_char_p),
        ("interfaceName", c_char_p),
        ("interfaceHandle", VmbHandle),
        ("transportLayerHandle", VmbHandle),
        ("interfaceType", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbInterfaceInfo'
        rep += fmt_repr('(interfaceIdString={}', self.interfaceIdString)
        rep += fmt_repr(',interfaceName={}', self.interfaceName)
        rep += fmt_repr(',interfaceHandle={}', self.interfaceHandle)
        rep += fmt_repr(',transportLayerHandle={}', self.transportLayerHandle)
        rep += fmt_enum_repr(',interfaceType={}', VmbTransportLayer, self.interfaceType)
        rep += ')'
        return rep


class VmbCameraInfo(ctypes.Structure):
    """
    Camera information. Holds read-only information about a camera.
        Fields:
            cameraIdString:
                Type: c_char_p
                Info: Unique identifier for each camera
            cameraIdExtended:
                Type: c_char_p
                Info: globally unique identifier for the camera
            cameraName:
                Type: c_char_p
                Info: Name of the camera
            modelName:
                Type: c_char_p
                Info: Model name
            serialString:
                Type: c_char_p
                Info: Serial number
            transportLayerHandle:
                Type: VmbHandle
                Info: Handle of the related transport layer for feature access
            interfaceHandle:
                Type: VmbHandle
                Info: Handle of the related interface for feature access
            localDeviceHandle:
                Type: VmbHandle
                Info: Handle of the related GenTL local device. NULL if the camera is not opened
            streamHandles:
                Type: c_ptr(VmbHandle)
                Info: Handles of the streams provided by the camera. NULL if the camera is not
                      opened
            streamCount:
                Type: VmbUint32
                Info: Number of stream handles in the streamHandles array
            permittedAccess:
                Type: VmbAccessMode (VmbUint32)
                Info: Used access mode, see VmbAccessMode
    """
    _fields_ = [
        ("cameraIdString", c_char_p),
        ("cameraIdExtended", c_char_p),
        ("cameraName", c_char_p),
        ("modelName", c_char_p),
        ("serialString", c_char_p),
        ("transportLayerHandle", VmbHandle),
        ("interfaceHandle", VmbHandle),
        ("localDeviceHandle", VmbHandle),
        ("streamHandles", c_ptr(VmbHandle)),
        ("streamCount", VmbUint32),
        ("permittedAccess", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbCameraInfo'
        rep += fmt_repr('(cameraIdString={}', self.cameraIdString)
        rep += fmt_repr(',cameraName={}', self.cameraName)
        rep += fmt_repr(',modelName={}', self.modelName)
        rep += fmt_repr(',serialString={}', self.serialString)
        rep += fmt_repr(',transportLayerHandle={}', self.transportLayerHandle)
        rep += fmt_repr(',interfaceHandle={}', self.interfaceHandle)
        rep += fmt_repr(',localDeviceHandle={}', self.localDeviceHandle)
        rep += fmt_repr(',streamHandles={}', self.streamHandles)
        rep += fmt_repr(',streamCount={}', self.streamCount)
        rep += fmt_flags_repr(',permittedAccess={}', VmbAccessMode, self.permittedAccess)
        rep += ')'
        return rep


class VmbFeatureInfo(ctypes.Structure):
    """
    Feature information. Holds read-only information about a feature.
        Fields:
            name:
                Type: c_char_p
                Info: Name used in the API
            category:
                Type: c_char_p
                Info: Category this feature can be found in
            displayName:
                Type: c_char_p
                Info: Feature name to be used in GUIs
            tooltip:
                Type: c_char_p
                Info: Short description, e.g. for a tooltip
            description:
                Type: c_char_p
                Info: Longer description
            sfncNamespace:
                Type: c_char_p
                Info: Namespace this feature resides in
            unit:
                Type: c_char_p
                Info: Measuring unit as given in the XML file
            representation:
                Type: c_char_p
                Info: Representation of a numeric feature
            featureDataType:
                Type: VmbFeatureData (VmbUint32)
                Info: Data type of this feature
            featureFlags:
                Type: VmbFeatureFlags (VmbUint32)
                Info: Access flags for this feature
            pollingTime:
                Type: VmbUint32
                Info: Predefined polling time for volatile features
            visibility:
                Type: VmbFeatureVisibility (VmbUint32)
                Info: GUI visibility
            isStreamable:
                Type: VmbBool
                Info: Indicates if a feature can be stored to / loaded from a file
            hasSelectedFeatures:
                Type: VmbBool
                Info: Indicates if the feature selects other features
    """
    _fields_ = [
        ("name", c_char_p),
        ("category", c_char_p),
        ("displayName", c_char_p),
        ("tooltip", c_char_p),
        ("description", c_char_p),
        ("sfncNamespace", c_char_p),
        ("unit", c_char_p),
        ("representation", c_char_p),
        ("featureDataType", VmbUint32),
        ("featureFlags", VmbUint32),
        ("pollingTime", VmbUint32),
        ("visibility", VmbUint32),
        ("isStreamable", VmbBool),
        ("hasSelectedFeatures", VmbBool)
    ]

    def __repr__(self):
        rep = 'VmbFeatureInfo'
        rep += fmt_repr('(name={}', self.name)
        rep += fmt_repr(',category={}', self.category)
        rep += fmt_repr(',displayName={}', self.displayName)
        rep += fmt_repr(',tooltip={}', self.tooltip)
        rep += fmt_repr(',description={}', self.description)
        rep += fmt_repr(',sfncNamespace={}', self.sfncNamespace)
        rep += fmt_repr(',unit={}', self.unit)
        rep += fmt_repr(',representation={}', self.representation)
        rep += fmt_enum_repr(',featureDataType={}', VmbFeatureData, self.featureDataType)
        rep += fmt_flags_repr(',featureFlags={}', VmbFeatureFlags, self.featureFlags)
        rep += fmt_repr(',pollingTime={}', self.pollingTime)
        rep += fmt_enum_repr(',visibility={}', VmbFeatureVisibility, self.visibility)
        rep += fmt_repr(',isStreamable={}', self.isStreamable)
        rep += fmt_repr(',hasSelectedFeatures={}', self.hasSelectedFeatures)
        rep += ')'
        return rep


class VmbFeatureEnumEntry(ctypes.Structure):
    """
    Info about possible entries of an enumeration feature:
        Fields:
            name:
                Type: c_char_p
                Info: Name used in the API
            displayName:
                Type: c_char_p
                Info: Enumeration entry name to be used in GUIs
            tooltip:
                Type: c_char_p
                Info: Short description, e.g. for a tooltip
            description:
                Type: c_char_p
                Info: Longer description
            intValue:
                Type: VmbInt64
                Info: Integer value of this enumeration entry
            sfncNamespace:
                Type: c_char_p
                Info: Namespace this feature resides in
            visibility:
                Type: VmbFeatureVisibility (VmbUint32)
                Info: GUI visibility
    """
    _fields_ = [
        ("name", c_char_p),
        ("displayName", c_char_p),
        ("tooltip", c_char_p),
        ("description", c_char_p),
        ("intValue", VmbInt64),
        ("sfncNamespace", c_char_p),
        ("visibility", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbFeatureEnumEntry'
        rep += fmt_repr('(name={}', self.name)
        rep += fmt_repr(',displayName={}', self.displayName)
        rep += fmt_repr(',tooltip={}', self.tooltip)
        rep += fmt_repr(',description={}', self.description)
        rep += fmt_repr(',intValue={},', self.intValue)
        rep += fmt_repr(',sfncNamespace={}', self.sfncNamespace)
        rep += fmt_enum_repr(',visibility={}', VmbFeatureVisibility, self.visibility)
        rep += ')'
        return rep


class VmbFrame(ctypes.Structure):
    """
    Frame delivered by Camera
        Fields (in):
            buffer:
                Type: c_void_p
                Info: Comprises image and chunk data
            bufferSize:
                Type: VmbUint32_t
                Info: Size of the data buffer
            context:
                Type: c_void_p[4]
                Info: 4 void pointers that can be employed by the user (e.g. for storing handles)

        Fields (out):
            receiveStatus:
                Type: VmbFrameStatus (VmbInt32)
                Info: Resulting status of the receive operation
            frameID:
                Type: VmbUint64
                Info: Unique ID of this frame in this stream
            timestamp:
                Type: VmbUint64
                Info: Timestamp set by the camera
            imageData:
                Type: c_ptr(VmbUint8)
                Info: The start of the image data, if present, or null
            receiveFlags:
                Type: VmbFrameFlags (VmbUint32)
                Info: Flags indicating which additional frame information is available
            pixelFormat:
                Type: VmbPixelFormat (VmbUint32)
                Info: Pixel format of the image
            width:
                Type: VmbImageDimension_t (VmbUint32)
                Info: Width of an image
            height:
                Type: VmbImageDimension_t (VmbUint32)
                Info: Height of an image
            offsetX:
                Type: VmbImageDimension_t (VmbUint32)
                Info: Horizontal offset of an image
            offsetY:
                Type: VmbImageDimension_t (VmbUint32)
                Info: Vertical offset of an image
            payloadType:
                Type: VmbPayloadType (VmbUint32)
                Info: The type of payload
            chunkDataPresent:
                Type: VmbBool
                Info: True if the transport layer reported chunk data to be present in the buffer
    """
    _fields_ = [
        ("buffer", c_void_p),
        ("bufferSize", VmbUint32),
        ("context", c_void_p * 4),
        ("receiveStatus", VmbInt32),
        ("frameID", VmbUint64),
        ("timestamp", VmbUint64),
        ("imageData", c_ptr(VmbUint8)),
        ("receiveFlags", VmbUint32),
        ("pixelFormat", VmbUint32),
        ("width", VmbUint32),
        ("height", VmbUint32),
        ("offsetX", VmbUint32),
        ("offsetY", VmbUint32),
        ("payloadType", VmbUint32),
        ("chunkDataPresent", VmbBool)
    ]

    def __repr__(self):
        rep = 'VmbFrame'
        rep += fmt_repr('(buffer={}', hex(self.buffer))
        rep += fmt_repr(',bufferSize={}', self.bufferSize)
        rep += fmt_repr(',context={}', self.context)
        rep += fmt_enum_repr(',receiveStatus: {}', VmbFrameStatus, self.receiveStatus)
        rep += fmt_repr(',frameID={}', self.frameID)
        rep += fmt_repr(',timestamp={}', self.timestamp)
        if self.imageData:
            rep += fmt_repr(',imageData={}', hex(ctypes.addressof(self.imageData.contents)))
        else:
            # imageData pointer is a nullptr. Use `None` to represent this
            rep += fmt_repr(',imageData={}', None)
        rep += fmt_flags_repr(',receiveFlags={}', VmbFrameFlags, self.receiveFlags)
        rep += fmt_enum_repr(',pixelFormat={}', VmbPixelFormat, self.pixelFormat)
        rep += fmt_repr(',width={}', self.width)
        rep += fmt_repr(',height={}', self.height)
        rep += fmt_repr(',offsetX={}', self.offsetX)
        rep += fmt_repr(',offsetY={}', self.offsetY)
        rep += fmt_repr(',payloadType={}', self.payloadType)
        rep += fmt_repr('chunkDataPresent={}', self.chunkDataPresent)
        rep += ')'
        return rep

    def deepcopy_skip_ptr(self, memo):
        result = VmbFrame()
        memo[id(self)] = result

        result.buffer = None
        result.bufferSize = 0
        result.context = (None, None, None, None)

        setattr(result, 'receiveStatus', copy.deepcopy(self.receiveStatus, memo))
        setattr(result, 'frameID', copy.deepcopy(self.frameID, memo))
        setattr(result, 'timestamp', copy.deepcopy(self.timestamp, memo))
        result.imageData = None
        setattr(result, 'receiveFlags', copy.deepcopy(self.receiveFlags, memo))
        setattr(result, 'pixelFormat', copy.deepcopy(self.pixelFormat, memo))
        setattr(result, 'width', copy.deepcopy(self.width, memo))
        setattr(result, 'height', copy.deepcopy(self.height, memo))
        setattr(result, 'offsetX', copy.deepcopy(self.offsetX, memo))
        setattr(result, 'offsetY', copy.deepcopy(self.offsetY, memo))
        setattr(result, 'payloadType', copy.deepcopy(self.payloadType, memo))
        setattr(result, 'chunkDataPresent', copy.deepcopy(self.chunkDataPresent, memo))
        return result


class VmbFeaturePersistSettings(ctypes.Structure):
    """
    Parameters determining the operation mode of VmbCameraSettingsSave and VmbCameraSettingsLoad
        Fields:
            persistType:
                Type: VmbFeaturePersist (VmbUint32)
                Info: Type of features that are to be saved
            modulePersistFlags:
                Type: VmbModulePersistFlags (VmbUint32)
                Info: Flags specifying the modules to persist/load
            maxIterations:
                Type: VmbUint32
                Info: Number of iterations when loading settings
            loggingLevel:
                Type: VmbUint32
                Info: Determines level of detail for load/save settings logging
    """
    _fields_ = [
        ("persistType", VmbUint32),
        ("modulePersistFlags", VmbUint32),
        ("maxIterations", VmbUint32),
        ("loggingLevel", VmbUint32)
    ]

    def __repr__(self):
        rep = 'VmbFrame'
        rep += fmt_enum_repr('(persistType={}', VmbFeaturePersist, self.persistType)
        rep += fmt_enum_repr('(modulePersistFlags={}',
                             VmbModulePersistFlags,
                             self.persistmodulePersistFlagsType)
        rep += fmt_repr(',maxIterations={}', self.maxIterations)
        rep += fmt_repr(',loggingLevel={}', self.loggingLevel)
        rep += ')'
        return rep


def _build_callback_type(*args):
    global _lib_instance

    lib_type = type(_lib_instance)

    if lib_type == ctypes.CDLL:
        return ctypes.CFUNCTYPE(*args)

    elif lib_type == ctypes.WinDLL:
        return ctypes.WINFUNCTYPE(*args)

    else:
        raise VmbSystemError('Unknown Library Type. Abort.')


CHUNK_CALLBACK_TYPE = _build_callback_type(VmbUint32, VmbHandle, ctypes.c_void_p)
INVALIDATION_CALLBACK_TYPE = _build_callback_type(None, VmbHandle, ctypes.c_char_p, ctypes.c_void_p)
FRAME_CALLBACK_TYPE = _build_callback_type(None, VmbHandle, VmbHandle, ctypes.POINTER(VmbFrame))


# For detailed information on the signatures see "VmbC.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbVersionQuery': (VmbError, [c_ptr(VmbVersionInfo), VmbUint32]),
    'VmbStartup': (VmbError, [c_ptr(VmbFilePathChar)]),
    'VmbShutdown': (None, None),
    'VmbCamerasList': (VmbError, [c_ptr(VmbCameraInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),
    'VmbCameraInfoQuery': (VmbError, [c_str, c_ptr(VmbCameraInfo), VmbUint32]),
    'VmbCameraOpen': (VmbError, [c_str, VmbAccessMode, c_ptr(VmbHandle)]),
    'VmbCameraClose': (VmbError, [VmbHandle]),
    'VmbFeaturesList': (VmbError, [VmbHandle, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                # noqa: E501
    'VmbFeatureInfoQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32]),
    'VmbFeatureListSelected': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeatureInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),  # noqa: E501
    'VmbFeatureAccessQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbBool), c_ptr(VmbBool)]),
    'VmbFeatureIntGet': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64)]),
    'VmbFeatureIntSet': (VmbError, [VmbHandle, c_str, VmbInt64]),
    'VmbFeatureIntRangeQuery': (VmbError, [VmbHandle, c_str, c_ptr(VmbInt64), c_ptr(VmbInt64)]),
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
    'VmbFeatureEnumEntryGet': (VmbError, [VmbHandle, c_str, c_str, c_ptr(VmbFeatureEnumEntry), VmbUint32]),                   # noqa: E501
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
    'VmbFeatureInvalidationRegister': (VmbError, [VmbHandle, c_str, INVALIDATION_CALLBACK_TYPE, c_void_p]),                   # noqa: E501
    'VmbFeatureInvalidationUnregister': (VmbError, [VmbHandle, c_str, INVALIDATION_CALLBACK_TYPE]),
    'VmbPayloadSizeGet': (VmbError, [VmbHandle, c_ptr(VmbUint32)]),
    'VmbFrameAnnounce': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbFrameRevoke': (VmbError, [VmbHandle, c_ptr(VmbFrame)]),
    'VmbFrameRevokeAll': (VmbError, [VmbHandle]),
    'VmbCaptureStart': (VmbError, [VmbHandle]),
    'VmbCaptureEnd': (VmbError, [VmbHandle]),
    'VmbCaptureFrameQueue': (VmbError, [VmbHandle, c_ptr(VmbFrame), FRAME_CALLBACK_TYPE]),
    'VmbCaptureFrameWait': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbCaptureQueueFlush': (VmbError, [VmbHandle]),
    'VmbTransportLayersList': (VmbError, [c_ptr(VmbTransportLayerInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),             # noqa: E501
    'VmbInterfacesList': (VmbError, [c_ptr(VmbInterfaceInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                       # noqa: E501
    'VmbMemoryRead': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbMemoryWrite': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbSettingsSave': (VmbError, [VmbHandle, c_ptr(VmbFilePathChar), c_ptr(VmbFeaturePersistSettings), VmbUint32]),          # noqa: E501
    'VmbSettingsLoad': (VmbError, [VmbHandle, c_ptr(VmbFilePathChar), c_ptr(VmbFeaturePersistSettings), VmbUint32]),          # noqa: E501
    'VmbChunkDataAccess': (VmbError, [c_ptr(VmbFrame), CHUNK_CALLBACK_TYPE, c_void_p])
}


def _attach_signatures(lib_handle):
    global _SIGNATURES

    for function_name, signature in _SIGNATURES.items():
        fn = getattr(lib_handle, function_name)
        fn.restype, fn.argtypes = signature
        fn.errcheck = _eval_vmberror

    return lib_handle


def _check_version(lib_handle):
    global EXPECTED_VMB_C_VERSION
    global VMB_C_VERSION

    v = VmbVersionInfo()
    lib_handle.VmbVersionQuery(byref(v), sizeof(v))

    VMB_C_VERSION = str(v)

    loaded_version = (v.major, v.minor, v.patch)
    expected_version = tuple(map(int, EXPECTED_VMB_C_VERSION.split(".")))

    if (os.environ.get('SKIP_VMBPY_VMBC_COMPATIBILITY_CHECK', 'false').lower()
            in ('true', 'yes', '1')):
        # User specifically requested that versions are not checked
        import warnings
        warnings.warn('VmbPy and VmbC compatibility check skipped because '
                      'SKIP_VMBPY_VMBC_COMPATIBILITY_CHECK was set to "{}". '
                      'Expected version is: "{}". Loaded version is "{}"'
                      ''.format(os.environ.get('SKIP_VMBPY_VMBC_COMPATIBILITY_CHECK'),
                                expected_version,
                                loaded_version),
                      category=RuntimeWarning)
        return lib_handle
    # major and minor version must be equal, patch version may be equal or greater
    if not (loaded_version[0:2] == expected_version[0:2] and
            loaded_version[2] >= expected_version[2]):
        msg = 'Invalid VmbC Version: Expected: {}, Found:{}'
        raise VmbSystemError(msg.format(EXPECTED_VMB_C_VERSION, VMB_C_VERSION))

    return lib_handle


def _eval_vmberror(result: VmbError, func: Callable[..., Any], *args: Tuple[Any, ...]):
    if result not in (VmbError.Success, None):
        raise VmbCError(result)


_lib_instance = _check_version(_attach_signatures(_lib_instance))


@TraceEnable()
def call_vmb_c(func_name: str, *args):
    """This function encapsulates the entire VmbC access.

    For Details on valid function signatures see the 'VmbC.h'.

    Arguments:
        func_name:
            The function name from VmbC to be called.
        args:
            Varargs passed directly to the underlying C-Function.

    Raises:
        TypeError:
            If given are do not match the signature of the function.
        AttributeError:
            If func with name ``func_name`` does not exist.
        VmbCError:
            If the function call is valid but neither ``None`` or ``VmbError.Success`` was returned.

    The following functions of VmbC can be executed:
        - VmbVersionQuery
        - VmbStartup
        - VmbShutdown
        - VmbCamerasList
        - VmbCameraInfoQuery
        - VmbCameraOpen
        - VmbCameraClose
        - VmbFeaturesList
        - VmbFeatureInfoQuery
        - VmbFeatureListSelected
        - VmbFeatureAccessQuery
        - VmbFeatureIntGet
        - VmbFeatureIntSet
        - VmbFeatureIntRangeQuery
        - VmbFeatureIntIncrementQuery
        - VmbFeatureFloatGet
        - VmbFeatureFloatSet
        - VmbFeatureFloatRangeQuery
        - VmbFeatureFloatIncrementQuery
        - VmbFeatureEnumGet
        - VmbFeatureEnumSet
        - VmbFeatureEnumRangeQuery
        - VmbFeatureEnumIsAvailable
        - VmbFeatureEnumAsInt
        - VmbFeatureEnumAsString
        - VmbFeatureEnumEntryGet
        - VmbFeatureStringGet
        - VmbFeatureStringSet
        - VmbFeatureStringMaxlengthQuery
        - VmbFeatureBoolGet
        - VmbFeatureBoolSet
        - VmbFeatureCommandRun
        - VmbFeatureCommandIsDone
        - VmbFeatureRawGet
        - VmbFeatureRawSet
        - VmbFeatureRawLengthQuery
        - VmbFeatureInvalidationRegister
        - VmbFeatureInvalidationUnregister
        - VmbFrameAnnounce
        - VmbFrameRevoke
        - VmbFrameRevokeAll
        - VmbCaptureStart
        - VmbCaptureEnd
        - VmbCaptureFrameQueue
        - VmbCaptureFrameWait
        - VmbCaptureQueueFlush
        - VmbInterfacesList
        - VmbMemoryRead
        - VmbMemoryWrite
        - VmbSettingsSave
        - VmbSettingsLoad
        - VmbChunkDataAccess
    """
    global _lib_instance
    getattr(_lib_instance, func_name)(*args)
