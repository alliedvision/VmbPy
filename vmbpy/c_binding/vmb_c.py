"""BSD 2-Clause License

Copyright (c) 2019, Allied Vision Technologies GmbH
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
from typing import Callable, Any, Tuple
from ctypes import c_void_p, c_char_p, byref, sizeof, POINTER as c_ptr, c_char_p as c_str
from ..util import TraceEnable
from ..error import VmbSystemError
from .vmb_common import Uint32Enum, Int32Enum, VmbUint8, VmbInt32, VmbUint32, VmbInt64, VmbUint64, \
    VmbHandle, VmbBool, VmbDouble, VmbError, VmbCError, VmbPixelFormat, \
    fmt_enum_repr, fmt_repr, fmt_flags_repr, load_vimbax_lib

__version__ = None

__all__ = [
    'VmbPixelFormat',
    'VmbTransportLayer',
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
    'G_VMB_C_HANDLE',
    'VMB_C_VERSION',
    'EXPECTED_VMB_C_VERSION',
    'call_vmb_c',
    'build_callback_type'
]


# Types
class VmbTransportLayer(Uint32Enum):
    """
    Camera Interface Types:
        Unknown  - Interface is not known to this version of the API
        GEV      - GigE Vision
        CL       - Camera Link
        IIDC     - IIDC 1394
        UVC      - USB video class
        CXP      - CoaXPress
        CLHS     - Camera Link HS
        U3V      - USB3 Vision Standard
        Ethernet - Generic Ethernet
        PCI      - PCI / PCIe
        Custom   - Non standard
        Mixed    - Mixed (transport layer only)
    """
    Unknown = 0
    GEV = 1
    CL = 2
    IIDC = 3
    UVC = 4
    CXP = 5
    CLHS = 6
    U3V = 7
    Ethernet = 8
    PCI = 9
    Custom = 10
    Mixed = 11

    def __str__(self):
        return self._name_


class VmbAccessMode(Uint32Enum):
    """
    Camera Access Mode:
        None_     - No access
        Full      - Read and write access
        Read      - Read-only access
        Config    - Configuration access (GeV)
        Exclusive - Read and write access without permitting access for other consumers
    """
    None_ = 0
    Full = 1
    Read = 2
    Config = 4
    Exclusive = ~Config

    def __str__(self):
        return self._name_


class VmbFeatureData(Uint32Enum):
    """
    Feature Data Types
        Unknown - Unknown feature type
        Int     - 64 bit integer feature
        Float   - 64 bit floating point feature
        Enum    - Enumeration feature
        String  - String feature
        Bool    - Boolean feature
        Command - Command feature
        Raw     - Raw (direct register access) feature
        None_   - Feature with no data
    """
    Unknown = 0
    Int = 1
    Float = 2
    Enum = 3
    String = 4
    Bool = 5
    Command = 6
    Raw = 7
    None_ = 8

    def __str__(self):
        return self._name_


class VmbFeaturePersist(Uint32Enum):
    """
    Type of features that are to be saved (persisted) to the XML file
    when using VmbCameraSettingsSave

        All        - Save all features to XML, including look-up tables
        Streamable - Save only features marked as streamable, excluding
                     look-up tables
        NoLUT      - Save all features except look-up tables (default)
    """
    All = 0
    Streamable = 1
    NoLUT = 2

    def __str__(self):
        return self._name_

class VmbModulePersistFlags(Uint32Enum):
    """
    Parameters determining the operation mode of VmbSettingsSave and VmbSettingsLoad

        None_          - Persist/Load features for no module
        TransportLayer - Persist/Load the transport layer features
        Interface      - Persist/Load the interface features
        RemoteDevice   - Persist/Load the remote device features
        LocalDevice    - Persist/Load the local device features
        Streams        - Persist/Load the features of stream modules
        All            - Persist/Load features for all modules
    """
    None_ = 0x00
    TransportLayer = 0x01
    Interface = 0x02
    RemoteDevice = 0x04
    LocalDevice = 0x08
    Streams = 0x10
    All = 0xff

    def __str__(self):
        return self._name_

class VmbFeatureVisibility(Uint32Enum):
    """
    Feature Visibility
        Unknown   - Feature visibility is not known
        Beginner  - Feature is visible in feature list (beginner level)
        Expert    - Feature is visible in feature list (expert level)
        Guru      - Feature is visible in feature list (guru level)
        Invisible - Feature is not visible in feature list
    """
    Unknown = 0
    Beginner = 1
    Expert = 2
    Guru = 3
    Invisible = 4

    def __str__(self):
        return self._name_


class VmbFeatureFlags(Uint32Enum):
    """
    Feature Flags
        None_       - No additional information is provided
        Read        - Static info about read access.
                      Current status depends on access mode, check with
                      VmbFeatureAccessQuery()
        Write       - Static info about write access.
                      Current status depends on access mode, check with
                      VmbFeatureAccessQuery()
        Volatile    - Value may change at any time
        ModifyWrite - Value may change after a write
    """
    None_ = 0
    Read = 1
    Write = 2
    Undocumented = 4
    Volatile = 8
    ModifyWrite = 16

    def __str__(self):
        return self._name_


class VmbFrameStatus(Int32Enum):
    """
    Frame transfer status
        Complete   - Frame has been completed without errors
        Incomplete - Frame could not be filled to the end
        TooSmall   - Frame buffer was too small
        Invalid    - Frame buffer was invalid
    """
    Complete = 0
    Incomplete = -1
    TooSmall = -2
    Invalid = -3

    def __str__(self):
        return self._name_


class VmbFrameFlags(Uint32Enum):
    """
    Frame Flags
        None_            - No additional information is provided
        Dimension        - Frame's dimension is provided
        Offset           - Frame's offset is provided (ROI)
        FrameID          - Frame's ID is provided
        Timestamp        - Frame's timestamp is provided
        ImageData        - Frame's imageData is provided
        PayloadType      - Frame's payloadType is provided
        ChunkDataPresent - Frame's chunkDataPresent is set based on info provided by the transport layer
    """
    None_ = 0
    Dimension = 1
    Offset = 2
    FrameID = 4
    Timestamp = 8
    ImageData = 16
    PayloadType = 32
    ChunkDataPresent = 64


    def __str__(self):
        return self._name_


class VmbVersionInfo(ctypes.Structure):
    """
    Version Information
        Fields:
            major - Type: VmbUint32, Info: Major version number
            minor - Type: VmbUint32, Info: Minor version number
            patch - Type: VmbUint32, Info: Patch version number
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


class VmbInterfaceInfo(ctypes.Structure):
    """
    Interface information. Holds read-only information about an interface.
        Fields:
            interfaceIdString    - Type: c_char_p
                                   Info: Unique identifier for each interface
            interfaceName        - Type: c_char_p
                                   Info: Interface name, given by transport layer
            interfaceHandle      - Type: VmbHandle
                                   Info: Handle of the interface for feature access
            transportLayerHandle - Type: VmbHandle
                                   Info: Handle of the related transport layer for feature access
            interfaceType        - Type: VmbTransportLayer (VmbUint32)
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
            cameraIdString       - Type: c_char_p
                                   Info: Unique identifier for each camera
            cameraIdExtended     - Type: c_char_p
                                   Info: globally unique identifier for the camera
            cameraName           - Type: c_char_p
                                   Info: Name of the camera
            modelName            - Type: c_char_p
                                   Info: Model name
            serialString         - Type: c_char_p
                                   Info: Serial number
            transportLayerHandle - Type: VmbHandle
                                   Info: Handle of the related transport layer for feature access
            interfaceHandle      - Type: VmbHandle
                                   Info: Handle of the related interface for feature access
            localDeviceHandle    - Type: VmbHandle
                                   Info: Handle of the related GenTL local device. NULL if the
                                   camera is not opened
            streamHandles        - Type: c_ptr(VmbHandle)
                                   Info: Handles of the streams provided by the camera.  NULL if the
                                   camera is not opened
            streamCount          - Type: VmbUint32
                                   Info: Number of stream handles in the streamHandles array
            permittedAccess      - Type: VmbAccessMode (VmbUint32)
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
            name                - Type: c_char_p
                                  Info: Name used in the API
            category            - Type: c_char_p
                                  Info: Category this feature can be found in
            displayName         - Type: c_char_p
                                  Info: Feature name to be used in GUIs
            tooltip             - Type: c_char_p
                                  Info: Short description, e.g. for a tooltip
            description         - Type: c_char_p
                                  Info: Longer description
            sfncNamespace       - Type: c_char_p
                                  Info: Namespace this feature resides in
            unit                - Type: c_char_p
                                  Info: Measuring unit as given in the XML file
            representation      - Type: c_char_p
                                  Info: Representation of a numeric feature
            featureDataType     - Type: VmbFeatureData (VmbUint32)
                                  Info: Data type of this feature
            featureFlags        - Type: VmbFeatureFlags (VmbUint32)
                                  Info: Access flags for this feature
            pollingTime         - Type: VmbUint32
                                  Info: Predefined polling time for volatile features
            visibility          - Type: VmbFeatureVisibility (VmbUint32)
                                  Info: GUI visibility
            isStreamable        - Type: VmbBool
                                  Info: Indicates if a feature can be stored to / loaded from a file
            hasSelectedFeatures - Type: VmbBool
                                  Info: Indicates if the feature selects other
                                        features
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
            name          - Type: c_char_p
                            Info: Name used in the API
            displayName   - Type: c_char_p
                            Info: Enumeration entry name to be used in GUIs
            tooltip       - Type: c_char_p
                            Info: Short description, e.g. for a tooltip
            description   - Type: c_char_p
                            Info: Longer description
            intValue      - Type: VmbInt64
                            Info: Integer value of this enumeration entry
            sfncNamespace - Type: c_char_p
                            Info: Namespace this feature resides in
            visibility    - Type: VmbFeatureVisibility (VmbUint32)
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
            buffer     - Type: c_void_p
                         Info: Comprises image and ancillary data
            bufferSize - Type: VmbUint32_t
                         Info: Size of the data buffer
            context    - Type: c_void_p[4]
                         Info: 4 void pointers that can be employed by the user
                               (e.g. for storing handles)

        Fields (out):
            receiveStatus    - Type: VmbFrameStatus (VmbInt32)
                               Info: Resulting status of the receive operation
            frameID          - Type: VmbUint64
                               Info: Unique ID of this frame in this stream
            timestamp        - Type: VmbUint64
                               Info: Timestamp set by the camera
            imageData        - Type: VmbUint8
                               Info: The start of the image data, if present, or null
            receiveFlags     - Type: VmbFrameFlags (VmbUint32)
                               Info: Flags indicating which additional frame information is
                                     available
            pixelFormat      - Type: VmbPixelFormat (VmbUint32)
                               Info: Pixel format of the image
            width            - Type: VmbImageDimension_t (VmbUint32)
                               Info: Width of an image
            height           - Type: VmbImageDimension_t (VmbUint32)
                               Info: Height of an image
            offsetX          - Type: VmbImageDimension_t (VmbUint32)
                               Info: Horizontal offset of an image
            offsetY          - Type: VmbImageDimension_t (VmbUint32)
                               Info: Vertical offset of an image
            payloadType      - Type: VmbPayloadType (VmbUint32)
                               Info: The type of payload
            chunkDataPresent - Type: VmbBool
                               Info: True if the transport layer reported chunk data to be present in the buffer
    """
    _fields_ = [
        ("buffer", c_void_p),
        ("bufferSize", VmbUint32),
        ("context", c_void_p * 4),
        ("receiveStatus", VmbInt32),
        ("frameID", VmbUint64),
        ("timestamp", VmbUint64),
        ("imageData", VmbUint8),
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
        rep += fmt_repr('(buffer={}', self.buffer)
        rep += fmt_repr(',bufferSize={}', self.bufferSize)
        rep += fmt_repr(',context={}', self.context)
        rep += fmt_enum_repr('receiveStatus: {}', VmbFrameStatus, self.receiveStatus)
        rep += fmt_repr(',frameID={}', self.frameID)
        rep += fmt_repr(',timestamp={}', self.timestamp)
        rep += fmt_repr(',imageData={}', self.imageData)
        rep += fmt_flags_repr(',receiveFlags={}', VmbFrameFlags, self.receiveFlags)
        rep += fmt_enum_repr(',pixelFormat={}', VmbPixelFormat, self.pixelFormat)
        rep += fmt_repr(',width={}', self.width)
        rep += fmt_repr(',height={}', self.height)
        rep += fmt_repr(',offsetX={}', self.offsetX)
        rep += fmt_repr(',offsetY={}', self.offsetY)
        rep += fmt_repr('payloadType={}', self.payloadType)
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
        setattr(result, 'imageData', copy.deepcopy(self.imageData, memo))
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
    Parameters determining the operation mode of VmbCameraSettingsSave
    and VmbCameraSettingsLoad
        Fields:
            persistType        - Type: VmbFeaturePersist (VmbUint32)
                                 Info: Type of features that are to be saved
            modulePersistFlags - Type: VmbModulePersistFlags (VmbUint32)
                                 Info: Flags specifying the modules to persist/load
            maxIterations      - Type: VmbUint32
                                 Info: Number of iterations when loading settings
            loggingLevel       - Type: VmbUint32
                                 Info: Determines level of detail for load/save
                                       settings logging
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
        rep += fmt_enum_repr('(modulePersistFlags={}', VmbModulePersistFlags, self.persistmodulePersistFlagsType)
        rep += fmt_repr(',maxIterations={}', self.maxIterations)
        rep += fmt_repr(',loggingLevel={}', self.loggingLevel)
        rep += ')'
        return rep


# TODO: Test that this also works on a 32bit Python version/System
G_VMB_C_HANDLE = VmbHandle((1 << (sizeof(VmbHandle)*8-4)) | 1)

VMB_C_VERSION = None
EXPECTED_VMB_C_VERSION = '0.1.0'

# For detailed information on the signatures see "VmbC.h"
# To improve readability, suppress 'E501 line too long (> 100 characters)'
# check of flake8
_SIGNATURES = {
    'VmbVersionQuery': (VmbError, [c_ptr(VmbVersionInfo), VmbUint32]),
    'VmbStartup': (VmbError, [c_str]),  # TODO: make sure c_str is correct (VmbFilePathChar_t in VmbC)
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
    'VmbFeatureInvalidationRegister': (VmbError, [VmbHandle, c_str, c_void_p, c_void_p]),
    'VmbFeatureInvalidationUnregister': (VmbError, [VmbHandle, c_str, c_void_p]),
    'VmbFrameAnnounce': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbFrameRevoke': (VmbError, [VmbHandle, c_ptr(VmbFrame)]),
    'VmbFrameRevokeAll': (VmbError, [VmbHandle]),
    'VmbCaptureStart': (VmbError, [VmbHandle]),
    'VmbCaptureEnd': (VmbError, [VmbHandle]),
    'VmbCaptureFrameQueue': (VmbError, [VmbHandle, c_ptr(VmbFrame), c_void_p]),
    'VmbCaptureFrameWait': (VmbError, [VmbHandle, c_ptr(VmbFrame), VmbUint32]),
    'VmbCaptureQueueFlush': (VmbError, [VmbHandle]),
    'VmbTransportLayersList': (VmbError, [c_ptr(VmbTransportLayerInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),             # noqa: E501
    'VmbInterfacesList': (VmbError, [c_ptr(VmbInterfaceInfo), VmbUint32, c_ptr(VmbUint32), VmbUint32]),                       # noqa: E501
    'VmbMemoryRead': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbMemoryWrite': (VmbError, [VmbHandle, VmbUint64, VmbUint32, c_str, c_ptr(VmbUint32)]),
    'VmbSettingsSave': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32]),
    'VmbSettingsLoad': (VmbError, [VmbHandle, c_str, c_ptr(VmbFeaturePersistSettings), VmbUint32]),
    # TODO: add 'VmbChunkDataAccess': (VmbError, [c_ptr(VmbFrame), c_void_p <- This callback is not void. Returns VmbError_t, c_void_p])
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
    # major and minor version must be equal, patch version may be equal or greater
    if not(loaded_version[0:2] == expected_version[0:2] and
           loaded_version[2] >= expected_version[2]):
        msg = 'Invalid VmbC Version: Expected: {}, Found:{}'
        raise VmbSystemError(msg.format(EXPECTED_VMB_C_VERSION, VMB_C_VERSION))

    return lib_handle


def _eval_vmberror(result: VmbError, func: Callable[..., Any], *args: Tuple[Any, ...]):
    if result not in (VmbError.Success, None):
        raise VmbCError(result)


_lib_instance = _check_version(_attach_signatures(load_vimbax_lib('VmbC')))


@TraceEnable()
def call_vmb_c(func_name: str, *args):
    """This function encapsulates the entire VmbC access.

    For Details on valid function signatures see the 'VmbC.h'.

    Arguments:
        func_name: The function name from VmbC to be called.
        args: Varargs passed directly to the underlying C-Function.

    Raises:
        TypeError if given are do not match the signature of the function.
        AttributeError if func with name 'func_name' does not exist.
        VmbCError if the function call is valid but neither None or VmbError.Success was returned.

    The following functions of VmbC can be executed:
        VmbVersionQuery
        VmbStartup
        VmbShutdown
        VmbCamerasList
        VmbCameraInfoQuery
        VmbCameraOpen
        VmbCameraClose
        VmbFeaturesList
        VmbFeatureInfoQuery
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
        VmbMemoryRead
        VmbMemoryWrite
        VmbSettingsSave
        VmbSettingsLoad
        VmbChunkDataAccess
    """
    global _lib_instance
    getattr(_lib_instance, func_name)(*args)


def build_callback_type(*args):
    global _lib_instance

    lib_type = type(_lib_instance)

    if lib_type == ctypes.CDLL:
        return ctypes.CFUNCTYPE(*args)

    elif lib_type == ctypes.WinDLL:
        return ctypes.WINFUNCTYPE(*args)

    else:
        raise VmbSystemError('Unknown Library Type. Abort.')
