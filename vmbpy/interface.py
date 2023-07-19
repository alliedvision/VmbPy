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

from typing import TYPE_CHECKING, Callable, Dict, Tuple

from .c_binding import VmbHandle, VmbInterfaceInfo, decode_cstr
from .featurecontainer import PersistableFeatureContainer
from .shared import read_memory, write_memory
from .transportlayer import TransportLayerType
from .util import (EnterContextOnCall, LeaveContextOnCall, RaiseIfOutsideContext,
                   RuntimeTypeCheckEnable, TraceEnable, VmbIntEnum)

if TYPE_CHECKING:
    from .camera import CamerasTuple
    from .transportlayer import TransportLayer

__all__ = [
    'Interface',
    'InterfaceEvent',
    'InterfaceChangeHandler',
    'InterfacesTuple',
    'InterfacesDict'
]


# Forward declarations
InterfaceChangeHandler = Callable[['Interface', 'InterfaceEvent'], None]
InterfacesTuple = Tuple['Interface', ...]
InterfacesDict = Dict[VmbHandle, 'Interface']


class InterfaceEvent(VmbIntEnum):
    """Enum specifying an Interface Event"""
    Missing = 0      #: A known interface disappeared from the bus
    Detected = 1     #: A new interface was discovered
    Reachable = 2    #: A known interface can be accessed
    Unreachable = 3  #: A known interface cannot be accessed anymore


class Interface(PersistableFeatureContainer):
    """This class allows access to an interface such as USB detected by VmbC."""

    @TraceEnable()
    def __init__(self, info: VmbInterfaceInfo, transport_layer: TransportLayer):
        """Do not call directly. Access Interfaces via ``vmbpy.VmbSystem`` instead."""
        super().__init__()
        self.__transport_layer = transport_layer
        self.__info: VmbInterfaceInfo = info
        self._handle: VmbHandle = self.__info.interfaceHandle
        self._open()

    @TraceEnable()
    @EnterContextOnCall()
    def _open(self):
        self._attach_feature_accessors()

    @TraceEnable()
    @LeaveContextOnCall()
    def _close(self):
        self._remove_feature_accessors()

    def __str__(self):
        return 'Interface(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Interface'
        rep += '(_handle=' + repr(self._handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    def get_id(self) -> str:
        """Get Interface Id such as 'VimbaUSBInterface_0x0'."""
        return decode_cstr(self.__info.interfaceIdString)

    def get_type(self) -> TransportLayerType:
        """Get Interface Type such as ``TransportLayerType.GEV``.

        Note:
            This uses the ``TransportLayerType`` enum to report the connection type of the Interface
            as there is no dedicated interface type enum. The ``TransportLayerType`` covers all
            interface types.
        """
        return TransportLayerType(self.__info.interfaceType)

    def get_name(self) -> str:
        """Get Interface Name such as 'VimbaX USB Interface'."""
        return decode_cstr(self.__info.interfaceName)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def read_memory(self, addr: int, max_bytes: int) -> bytes:  # coverage: skip
        """Read a byte sequence from a given memory address.

        Arguments:
            addr:
                Starting address to read from.
            max_bytes:
                Maximum number of bytes to read from addr.

        Returns:
            Read memory contents as bytes.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            ValueError:
                If ``addr`` is negative.
            ValueError:
                If ``max_bytes`` is negative.
            ValueError:
                If the memory access was invalid.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return read_memory(self._handle, addr, max_bytes)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def write_memory(self, addr: int, data: bytes):  # coverage: skip
        """Write a byte sequence to a given memory address.

        Arguments:
            addr:
                Address to write the content of 'data' to.
            data:
                Byte sequence to write at address 'addr'.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            ValueError:
                If ``addr`` is negative.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return write_memory(self._handle, addr, data)

    def get_transport_layer(self) -> TransportLayer:
        """Get the Transport Layer associated with this instance of Interface"""
        return self.__transport_layer

    def get_cameras(self) -> CamerasTuple:
        """Get access to cameras associated with the Interface instance

        Returns:
            A tuple of all cameras associated with this Interface

        Raises:
            RuntimeError:
                If called outside of VmbSystem ``with`` context.
        """
        return self._get_cameras()

    def _get_cameras(self):
        # This method relies on functionality of `VmbSystem` and is overwritten from there. This is
        # done to avoid importing `VmbSystem` here which would lead to a circular dependency.
        raise NotImplementedError

    def _get_handle(self) -> VmbHandle:
        """Internal helper function to get handle of interface"""
        return self._handle

    _msg = 'Called \'{}()\' outside of VmbSystems \'with\' context.'
    get_all_features = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_all_features)                  # noqa: E501
    get_features_selected_by = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_selected_by)  # noqa: E501
    get_features_by_type = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_by_type)          # noqa: E501
    get_features_by_category = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_features_by_category)  # noqa: E501
    get_feature_by_name = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.get_feature_by_name)            # noqa: E501
    load_settings = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.load_settings)
    save_settings = RaiseIfOutsideContext(msg=_msg)(PersistableFeatureContainer.save_settings)
