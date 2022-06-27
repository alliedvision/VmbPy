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

import enum
from typing import Tuple, List, Callable, Dict
from .c_binding import call_vmb_c, byref, sizeof, decode_cstr
from .c_binding import VmbInterfaceInfo, VmbHandle, VmbUint32
from . import vmbsystem
from .feature import discover_features, FeatureTypes, FeaturesTuple, FeatureTypeTypes
from .shared import filter_features_by_name, filter_features_by_type, filter_affected_features, \
                    filter_selected_features, filter_features_by_category, \
                    attach_feature_accessors, read_memory, \
                    write_memory, read_registers, write_registers
from .util import TraceEnable, RuntimeTypeCheckEnable
from .error import VmbFeatureError
from .transportlayer import TransportLayer, TransportLayerType

__all__ = [
    'Interface',
    'InterfaceEvent',
    'InterfaceChangeHandler',
    'InterfacesTuple',
    'InterfacesList',
    'discover_interfaces',
    'discover_interface'
]


# Forward declarations
InterfaceChangeHandler = Callable[['Interface', 'InterfaceEvent'], None]
InterfacesTuple = Tuple['Interface', ...]
InterfacesList = List['Interface']


class InterfaceEvent(enum.IntEnum):
    """Enum specifying an Interface Event

    Enum values:
        Missing     - A known interface disappeared from the bus
        Detected    - A new interface was discovered
        Reachable   - A known interface can be accessed
        Unreachable - A known interface cannot be accessed anymore
    """
    Missing = 0
    Detected = 1
    Reachable = 2
    Unreachable = 3


class Interface:
    """This class allows access to an interface such as USB detected by Vimba."""

    @TraceEnable()
    def __init__(self, info: VmbInterfaceInfo):
        """Do not call directly. Access Interfaces via vmbpy.VmbSystem instead."""
        self.__info: VmbInterfaceInfo = info
        self.__handle: VmbHandle = self.__info.interfaceHandle
        self.__feats = discover_features(self.__handle)
        attach_feature_accessors(self, self.__feats)

    def __str__(self):
        return 'Interface(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Interface'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    def get_id(self) -> str:
        """Get Interface Id such as VimbaUSBInterface_0x0."""
        return decode_cstr(self.__info.interfaceIdString)

    def get_type(self) -> TransportLayerType:
        """Get Interface Type such as InterfaceType.Usb."""
        return TransportLayerType(self.__info.interfaceType)

    def get_name(self) -> str:
        """Get Interface Name such as Vimba USB Interface."""
        return decode_cstr(self.__info.interfaceName)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def read_memory(self, addr: int, max_bytes: int) -> bytes:  # coverage: skip
        """Read a byte sequence from a given memory address.

        Arguments:
            addr: Starting address to read from.
            max_bytes: Maximum number of bytes to read from addr.

        Returns:
            Read memory contents as bytes.

        Raises:
            TypeError if parameters do not match their type hint.
            ValueError if addr is negative.
            ValueError if max_bytes is negative.
            ValueError if the memory access was invalid.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return read_memory(self.__handle, addr, max_bytes)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def write_memory(self, addr: int, data: bytes):  # coverage: skip
        """Write a byte sequence to a given memory address.

        Arguments:
            addr: Address to write the content of 'data' to.
            data: Byte sequence to write at address 'addr'.

        Raises:
            TypeError if parameters do not match their type hint.
            ValueError if addr is negative.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return write_memory(self.__handle, addr, data)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def read_registers(self, addrs: Tuple[int, ...]) -> Dict[int, int]:  # coverage: skip
        """Read contents of multiple registers.

        Arguments:
            addrs: Sequence of addresses that should be read iteratively.

        Returns:
            Dictionary containing a mapping from given address to the read register values.

        Raises:
            TypeError if parameters do not match their type hint.
            ValueError if any address in addrs is negative.
            ValueError if the register access was invalid.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return read_registers(self.__handle, addrs)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def write_registers(self, addrs_values: Dict[int, int]):  # coverage: skip
        """Write data to multiple registers.

        Arguments:
            addrs_values: Mapping between register addresses and the data to write.

        Raises:
            TypeError if parameters do not match their type hint.
            ValueError if any address in addrs_values is negative.
            ValueError if the register access was invalid.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return write_registers(self.__handle, addrs_values)

    def get_all_features(self) -> FeaturesTuple:
        """Get access to all discovered features of this Interface.

        Returns:
            A set of all currently detected features.
        """
        return self.__feats

    def get_transport_layer(self) -> TransportLayer:
        """Get the Transport Layer associated with this instance of Interface
        """
        with vmbsystem.VmbSystem.get_instance() as vmb:
            tls = vmb.get_all_transport_layers()
            return [tl for tl in tls if tl._get_handle() == self.__info.transportLayerHandle].pop()

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features affected by a specific interface feature.

        Arguments:
            feat - Feature to find features that are affected by 'feat'.

        Returns:
            A set of features affected by changes on 'feat'.

        Raises:
            TypeError if parameters do not match their type hint.
            VmbFeatureError if 'feat' is not a feature of this interface.
        """
        return filter_affected_features(self.__feats, feat)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features selected by a specific interface feature.

        Arguments:
            feat - Feature to find features that are selected by 'feat'.

        Returns:
            A set of features selected by changes on 'feat'.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VmbFeatureError if 'feat' is not a feature of this interface.
        """
        return filter_selected_features(self.__feats, feat)

    @RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypeTypes) -> FeaturesTuple:
        """Get all interface features of a specific feature type.

        Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
        EnumFeature, CommandFeature, RawFeature

        Arguments:
            feat_type - FeatureType used find features of that type.

        Returns:
            A set of features of type 'feat_type'.

        Raises:
            TypeError if parameters do not match their type hint.
        """
        return filter_features_by_type(self.__feats, feat_type)

    @RuntimeTypeCheckEnable()
    def get_features_by_category(self, category: str) -> FeaturesTuple:
        """Get all interface features of a specific category.

        Arguments:
            category - category for filtering.

        Returns:
            A set of features of category 'category'.

        Raises:
            TypeError if parameters do not match their type hint.
        """
        return filter_features_by_category(self.__feats, category)

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get an interface feature by its name.

        Arguments:
            feat_name - Name to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError if parameters do not match their type hint.
            VmbFeatureError if no feature is associated with 'feat_name'.
        """
        feat = filter_features_by_name(self.__feats, feat_name)

        if not feat:
            raise VmbFeatureError('Feature \'{}\' not found.'.format(feat_name))

        return feat


@TraceEnable()
def discover_interfaces() -> InterfacesList:
    """Do not call directly. Access Interfaces via vmbpy.VmbSystem instead."""

    result = []
    inters_count = VmbUint32(0)

    call_vmb_c('VmbInterfacesList', None, 0, byref(inters_count), sizeof(VmbInterfaceInfo))

    if inters_count:
        inters_found = VmbUint32(0)
        inters_infos = (VmbInterfaceInfo * inters_count.value)()

        call_vmb_c('VmbInterfacesList', inters_infos, inters_count, byref(inters_found),
                     sizeof(VmbInterfaceInfo))

        for info in inters_infos[:inters_found.value]:
            result.append(Interface(info))

    return result


@TraceEnable()
def discover_interface(id_: str) -> Interface:
    """Do not call directly. Access Interfaces via vmbpy.VmbSystem instead."""

    # Since there is no function to query a single interface, discover all interfaces and
    # extract the Interface with the matching ID.
    inters = discover_interfaces()
    return [i for i in inters if id_ == i.get_id()].pop()
