"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
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

from typing import TYPE_CHECKING, Dict, Tuple

from .c_binding import TransportLayerType, VmbHandle, VmbTransportLayerInfo, decode_cstr
from .featurecontainer import PersistableFeatureContainer
from .util import EnterContextOnCall, LeaveContextOnCall, RaiseIfOutsideContext, TraceEnable

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


class TransportLayer(PersistableFeatureContainer):
    """This class allows access to a Transport Layer."""

    @TraceEnable()
    def __init__(self, info: VmbTransportLayerInfo):
        """Do not call directly. Access Transport Layers via ``vmbpy.VmbSystem`` instead."""
        super().__init__()
        self.__info: VmbTransportLayerInfo = info
        self._handle: VmbHandle = self.__info.transportLayerHandle
        self._open()

    def __str__(self):
        return 'TransportLayer(id={})'.format(self.get_id())

    def __repr__(self) -> str:
        rep = 'TransportLayer'
        rep += '(_handle=' + repr(self._handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    @TraceEnable()
    @EnterContextOnCall()
    def _open(self):
        self._attach_feature_accessors()

    @TraceEnable()
    @LeaveContextOnCall()
    def _close(self):
        self._remove_feature_accessors()

    def get_interfaces(self) -> InterfacesTuple:
        """Get all interfaces associated with the Transport Layer instance.

        Returns:
            A tuple of all interfaces associated with this Transport Layer.

        Raises:
            RuntimeError:
                If called outside of VmbSystem ``with`` context.
        """
        return self._get_interfaces()

    def _get_interfaces(self):
        # This method is implemented using functionality of `VmbSystem`. This is just a placeholder
        # that is overwritten from `VmbSystem`. This is done to avoid importing `VmbSystem` here
        # which would lead to a circular dependency.
        raise NotImplementedError

    def get_cameras(self) -> CamerasTuple:
        """Get access to cameras associated with the Transport Layer instance.

        Returns:
            A tuple of all cameras associated with this Transport Layer.

        Raises:
            RuntimeError:
                If called outside of VmbSystem ``with`` context.
        """
        return self._get_cameras()

    def _get_cameras(self):
        # This method relies on functionality of `VmbSystem` and is overwritten from there. This is
        # done to avoid importing `VmbSystem` here which would lead to a circular dependency.
        raise NotImplementedError

    def get_id(self) -> str:
        """Get Transport Layer Id such as 'VimbaGigETL'"""
        return decode_cstr(self.__info.transportLayerIdString)

    def get_name(self) -> str:
        """Get Transport Layer Display Name such as 'AVT GigE Transport Layer'"""
        return decode_cstr(self.__info.transportLayerName)

    def get_model_name(self) -> str:
        """Get Transport Layer Model Name such as 'GigETL'"""
        return decode_cstr(self.__info.transportLayerModelName)

    def get_vendor(self) -> str:
        """Get Transport Layer Vendor such as 'Allied Vision Technologies'"""
        return decode_cstr(self.__info.transportLayerVendor)

    def get_version(self) -> str:
        """Get Transport Layer Version"""
        return decode_cstr(self.__info.transportLayerVersion)

    def get_path(self) -> str:
        """Get path to Transport Layer file"""
        return decode_cstr(self.__info.transportLayerPath)

    def get_type(self) -> TransportLayerType:
        """Get Transport Layer Type such as ``TransportLayerType.GEV``"""
        return TransportLayerType(self.__info.transportLayerType)

    def _get_handle(self) -> VmbHandle:
        """Internal helper function to get handle of Transport Layer"""
        return self._handle

    _msg = 'Called \'{}()\' outside of VmbSystems \'with\' context.'
    get_all_features = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_all_features)                  # noqa: E501
    get_features_selected_by = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_selected_by)  # noqa: E501
    get_features_by_type = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_by_type)          # noqa: E501
    get_features_by_category = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_by_category)  # noqa: E501
    get_feature_by_name = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_feature_by_name)            # noqa: E501
    load_settings = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.load_settings)
    save_settings = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.save_settings)
