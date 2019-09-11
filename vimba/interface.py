# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import enum
from typing import Tuple
from vimba.c_binding import call_vimba_c_func, byref, sizeof, decode_cstr
from vimba.c_binding import VmbInterface, VmbInterfaceInfo, VmbHandle, VmbUint32
from vimba.access_mode import AccessMode
from vimba.feature import discover_features, filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features, FeatureTypes, \
                          FeaturesTuple


class InterfaceType(enum.IntEnum):
    Unknown = VmbInterface.Unknown
    Firewire = VmbInterface.Firewire
    Ethernet = VmbInterface.Ethernet
    Usb = VmbInterface.Usb
    CL = VmbInterface.CL
    CSI2 = VmbInterface.CSI2


class Interface:
    def __init__(self, info: VmbInterfaceInfo):
        self._handle: VmbHandle = VmbHandle(0)
        self._info: VmbInterfaceInfo = info
        self._feats: FeaturesTuple = ()
        self._context_cnt: int = 0

    def __enter__(self):
        if not self._context_cnt:
            self._open()

        self._context_cnt += 1
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._context_cnt -= 1

        if not self._context_cnt:
            self._close()

    def __str__(self):
        return 'Interface(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Interface'
        rep += '(_handle=' + repr(self._handle)
        rep += ',_info=' + repr(self._info)
        rep += ')'
        return rep

    def get_id(self) -> str:
        return decode_cstr(self._info.interfaceIdString)

    def get_type(self) -> InterfaceType:
        return InterfaceType(self._info.interfaceType)

    def get_name(self) -> str:
        return decode_cstr(self._info.interfaceName)

    def get_serial(self) -> str:
        return decode_cstr(self._info.serialString)

    def get_permitted_access_mode(self) -> AccessMode:
        return AccessMode(self._info.permittedAccess)

    def get_all_features(self) -> FeaturesTuple:
        return self._feats

    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        return filter_affected_features(self._feats, feat)

    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        return filter_selected_features(self._feats, feat)

    def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
        return filter_features_by_type(self._feats, feat_type)

    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        return filter_features_by_name(self._feats, feat_name)

    def _open(self):
        call_vimba_c_func('VmbInterfaceOpen', self._info.interfaceIdString, byref(self._handle))

        self._feats = discover_features(self._handle)

    def _close(self):
        for feat in self._feats:
            feat.unregister_all_change_handlers()

        self._feats = ()

        call_vimba_c_func('VmbInterfaceClose', self._handle)

        self._handle = VmbHandle(0)


InterfacesTuple = Tuple[Interface, ...]


def discover_interfaces() -> InterfacesTuple:
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
