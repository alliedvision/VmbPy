# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbInterfaceInfo, VmbHandle, VmbUint32
from vimba.feature import discover_features, filter_features_by_name, \
                          filter_features_by_type, filter_affected_features, \
                          filter_selected_features


class Interface:
    def __init__(self, info: VmbInterfaceInfo):
        self._info = info
        self._handle = VmbHandle(0)
        self._feats = ()
        self._context_cnt = 0

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
        return 'Interface(id={}, handle={})'.format(self.get_id(),
                                                    self._handle)

    def __repr__(self):
        rep = 'Interface'
        rep += '(_info=' + repr(self._info)
        rep += ',_handle=' + repr(self._handle)
        rep += ')'
        return rep

    def get_id(self):
        return self._info.interfaceIdString.decode()

    def get_all_features(self):
        return self._feats

    def get_features_affected_by(self, feat):
        return filter_affected_features(self._feats, feat)

    def get_features_selected_by(self, feat):
        return filter_selected_features(self._feats, feat)

    def get_features_by_type(self, feat_type):
        return filter_features_by_type(self._feats, feat_type)

    def get_feature_by_name(self, feat_name: str):
        return filter_features_by_name(self._feats, feat_name)

    def _open(self):
        call_vimba_c_func('VmbInterfaceOpen', self._info.interfaceIdString,
                          byref(self._handle))

        self._feats = discover_features(self._handle)

    def _close(self):
        self._feats = ()

        call_vimba_c_func('VmbInterfaceClose', self._handle)

        self._handle = VmbHandle(0)


def discover_interfaces():
    result = []
    inters_count = VmbUint32(0)

    call_vimba_c_func('VmbInterfacesList', None, 0, byref(inters_count),
                      sizeof(VmbInterfaceInfo))

    if inters_count:
        inters_found = VmbUint32(0)
        inters_infos = (VmbInterfaceInfo * inters_count.value)()

        call_vimba_c_func('VmbInterfacesList', inters_infos,
                          inters_count, byref(inters_found),
                          sizeof(VmbInterfaceInfo))

        for info in inters_infos[:inters_found.value]:
            result.append(Interface(info))

    return tuple(result)
