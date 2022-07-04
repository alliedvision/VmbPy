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
from __future__ import annotations

import enum
from typing import Tuple, TYPE_CHECKING, Dict

from .c_binding import VmbTransportLayer, VmbTransportLayerInfo, VmbHandle, decode_cstr
from .feature import discover_features, FeaturesTuple
from .shared import attach_feature_accessors
from .util import TraceEnable

if TYPE_CHECKING:
    from .camera import CamerasTuple
    from .interface import InterfacesTuple


__all__ = [
    'TransportLayer',
    'TransportLayerType',
    'TransportLayersTuple',
    'TransportLayersDict'
]

# Forward declarations
TransportLayersTuple = Tuple['TransportLayer', ...]
TransportLayersDict = Dict[VmbHandle, 'TransportLayer']


class TransportLayerType(enum.IntEnum):
    """Enum specifying all interface types.

    Enum values:
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
    Unknown = VmbTransportLayer.Unknown
    GEV = VmbTransportLayer.GEV
    CL = VmbTransportLayer.CL
    IIDC = VmbTransportLayer.IIDC
    UVC = VmbTransportLayer.UVC
    CXP = VmbTransportLayer.CXP
    CLHS = VmbTransportLayer.CLHS
    U3V = VmbTransportLayer.U3V
    Ethernet = VmbTransportLayer.Ethernet
    PCI = VmbTransportLayer.PCI
    Custom = VmbTransportLayer.Custom
    Mixed = VmbTransportLayer.Mixed


class TransportLayer:
    """This class allows access to a Transport Layer."""

    @TraceEnable()
    def __init__(self, info: VmbTransportLayerInfo):
        """Do not call directly. Access Transport Layers via vmbpy.VmbSystem instead."""
        self.__info: VmbTransportLayerInfo = info
        self.__handle: VmbHandle = self.__info.transportLayerHandle
        self.__feats: FeaturesTuple = discover_features(self.__handle)
        attach_feature_accessors(self, self.__feats)

    def __str__(self):
        return 'TransportLayer(id={})'.format(self.get_id())

    def __repr__(self) -> str:
        rep = 'TransportLayer'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    def get_interfaces(self) -> InterfacesTuple:
        """Get all interfaces associated with the Transport Layer instance

        This method relies on functionality of `VmbSystem` and is overwritten from there. This is
        done to avoid importing `VmbSystem` here which would lead to a circular dependency.
        """
        raise NotImplementedError

    def get_cameras(self) -> CamerasTuple:
        """Get all cameras associated with the Transport Layer instance

        This method relies on functionality of `VmbSystem` and is overwritten from there. This is
        done to avoid importing `VmbSystem` here which would lead to a circular dependency.
        """
        raise NotImplementedError

    def get_id(self) -> str:
        """Get Transport Layer Id such as VimbaGigETL"""
        return decode_cstr(self.__info.transportLayerIdString)

    def get_name(self) -> str:
        """Get Transport Layer Name such as Vimba GigE Transport Layer"""
        return decode_cstr(self.__info.transportLayerName)

    def get_model_name(self) -> str:
        """Get Transport Layer Model Name such as Vimba GigE TL"""
        return decode_cstr(self.__info.transportLayerModelName)

    def get_vendor(self) -> str:
        """Get Transport Layer Vendor such as Allied Vision Technologies"""
        return decode_cstr(self.__info.transportLayerVendor)

    def get_version(self) -> str:
        """Get Transport Layer Version"""
        return decode_cstr(self.__info.transportLayerVersion)

    def get_path(self) -> str:
        """Get path to Transport Layer file"""
        return decode_cstr(self.__info.transportLayerPath)

    def get_type(self) -> TransportLayerType:
        """Get Transport Layer Type such as TransportLayerType.GEV"""
        return TransportLayerType(self.__info.transportLayerType)

    def _get_handle(self) -> VmbHandle:
        """Internal helper function to get handle of Transport Layer"""
        return self.__handle
