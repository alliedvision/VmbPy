"""Interface access.

This module allows access to all detected interfaces.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import enum
from typing import Tuple
from vimba.c_binding import call_vimba_c_func, byref, sizeof, decode_cstr
from vimba.c_binding import VmbInterface, VmbInterfaceInfo, VmbHandle, VmbUint32
from vimba.feature import discover_features, filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features, FeatureTypes, \
                          FeaturesTuple
from vimba.util import RuntimeTypeCheckEnable


__all__ = [
    'InterfaceType',
    'Interface',
    'InterfacesTuple',
    'discover_interfaces'
]


class InterfaceType(enum.IntEnum):
    """Enum specifying all interface types.

    Enum values:
        Unknown  - Interface is not known to this VimbaPython version.
        Firewire - 1394
        Ethernet - Gigabit Ethernet
        Usb      - USB 3.0
        CL       - Camera Link
        CSI2     - CSI-2
    """
    Unknown = VmbInterface.Unknown
    Firewire = VmbInterface.Firewire
    Ethernet = VmbInterface.Ethernet
    Usb = VmbInterface.Usb
    CL = VmbInterface.CL
    CSI2 = VmbInterface.CSI2


class Interface:
    """This class allows access a Interface detected by the Vimba System.
    Camera is meant be used in conjunction with the "with" - Statement. On entering a context
    all Interface features are detected and can be accessed within the context. Basic Interface
    properties like Name can be access outside of the context.
    """

    def __init__(self, info: VmbInterfaceInfo):
        """Do not call directly. Access Interfaces via vimba.System instead."""
        self.__handle: VmbHandle = VmbHandle(0)
        self.__info: VmbInterfaceInfo = info
        self.__feats: FeaturesTuple = ()
        self.__context_cnt: int = 0

    def __enter__(self):
        if not self.__context_cnt:
            self._open()

        self.__context_cnt += 1
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__context_cnt -= 1

        if not self.__context_cnt:
            self._close()

    def __str__(self):
        return 'Interface(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Interface'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    def get_id(self) -> str:
        """Get Interface Id, e.g. VimbaUSBInterface_0x0."""
        return decode_cstr(self.__info.interfaceIdString)

    def get_type(self) -> InterfaceType:
        """Get Interface Type, e.g. InterfaceType.Usb."""
        return InterfaceType(self.__info.interfaceType)

    def get_name(self) -> str:
        """Get Interface Name, e.g. Vimba USB Interface."""
        return decode_cstr(self.__info.interfaceName)

    def get_serial(self) -> str:
        """Get Interface Serial or '' if not set."""
        return decode_cstr(self.__info.serialString)

    def get_all_features(self) -> FeaturesTuple:
        """Get access to all discovered features of this Interface:

        Returns:
            A set of all currently detected features. Returns an empty set then called
            outside of 'with' - statement.
        """
        return self.__feats

    @RuntimeTypeCheckEnable()
    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features affected by a specific interface feature.

        Arguments:
            feat - Feature used find features that are affected by 'feat'.

        Returns:
            A set of features affected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this interface.
        """
        return filter_affected_features(self.__feats, feat)

    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features selected by a specific interface feature.

        Arguments:
            feat - Feature used find features that are selected by 'feat'.

        Returns:
            A set of features selected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this interface.
        """
        return filter_selected_features(self.__feats, feat)

    #@RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
        """Get all interface features of a specific feature type.

        Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
        EnumFeature, CommandFeature, RawFeature

        Arguments:
            feat_type - FeatureType used find features of that type.

        Returns:
            A set of features of type 'feat_type'. Can be an empty set if there is
            no interface feature with the given type available.

        Raises:
            TypeError if 'feat_type' is not of any feature Type.
        """
        return filter_features_by_type(self.__feats, feat_type)

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get a interface feature by its name.

        Arguments:
            feat_name - Name used to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError if 'feat_name' is not of type 'str'.
            VimbaFeatureError if no feature is associated with 'feat_name'.
        """
        return filter_features_by_name(self.__feats, feat_name)

    def _open(self):
        call_vimba_c_func('VmbInterfaceOpen', self.__info.interfaceIdString, byref(self.__handle))

        self.__feats = discover_features(self.__handle)

    def _close(self):
        for feat in self.__feats:
            feat.unregister_all_change_handlers()

        self.__feats = ()

        call_vimba_c_func('VmbInterfaceClose', self.__handle)

        self.__handle = VmbHandle(0)


InterfacesTuple = Tuple[Interface, ...]


def discover_interfaces() -> InterfacesTuple:
    """Do not call directly. Access Interfaces via vimba.System instead."""

    result = []
    inters_count = VmbUint32(0)

    call_vimba_c_func('VmbInterfacesList', None, 0, byref(inters_count), sizeof(VmbInterfaceInfo))

    if inters_count:
        inters_found = VmbUint32(0)
        inters_infos = (VmbInterfaceInfo * inters_count.value)()

        call_vimba_c_func('VmbInterfacesList', inters_infos, inters_count, byref(inters_found),
                          sizeof(VmbInterfaceInfo))

        for info in inters_infos[:inters_found.value]:
            result.append(Interface(info))

    return tuple(result)
