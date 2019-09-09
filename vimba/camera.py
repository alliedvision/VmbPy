# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, byref, sizeof, decode_cstr, \
                            decode_flags
from vimba.c_binding import VmbCameraInfo, VmbHandle, VmbUint32, G_VIMBA_HANDLE
from vimba.access_mode import AccessMode
from vimba.feature import discover_features, discover_feature, \
                          filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features


class Camera:
    def __init__(self, info: VmbCameraInfo, access_mode: AccessMode):
        self._handle = VmbHandle(0)
        self._info = info
        self._access_mode = access_mode
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
        return 'Camera(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Camera'
        rep += '(_handle=' + repr(self._handle)
        rep += ',_info=' + repr(self._info)
        rep += ')'
        return rep

    def set_access_mode(self, access_mode: AccessMode):
        self._access_mode = access_mode

    def get_access_mode(self):
        return self._access_mode

    def get_id(self):
        return decode_cstr(self._info.cameraIdString)

    def get_name(self):
        return decode_cstr(self._info.cameraName)

    def get_model(self):
        return decode_cstr(self._info.modelName)

    def get_serial(self):
        return decode_cstr(self._info.serialString)

    def get_permitted_access_modes(self):
        return decode_flags(AccessMode, self._info.permittedAccess)

    def get_interface_id(self):
        return decode_cstr(self._info.interfaceIdString)

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
        call_vimba_c_func('VmbCameraOpen', self._info.cameraIdString,
                          self._access_mode, byref(self._handle))

        self._feats = discover_features(self._handle)

    def _close(self):
        for feat in self._feats:
            feat.remove_all_change_handlers()

        self._feats = ()

        call_vimba_c_func('VmbCameraClose', self._handle)

        self._handle = VmbHandle(0)


def _setup_network_discovery():
    if discover_feature(G_VIMBA_HANDLE, 'GeVTLIsPresent').get():
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllDuration').set(250)
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllOnce').run()


def discover_cameras(access_mode: AccessMode, network_discovery: bool):
    if network_discovery:
        _setup_network_discovery()

    result = []
    cams_count = VmbUint32(0)

    call_vimba_c_func('VmbCamerasList', None, 0, byref(cams_count), 0)

    if cams_count:
        cams_found = VmbUint32(0)
        cams_infos = (VmbCameraInfo * cams_count.value)()

        call_vimba_c_func('VmbCamerasList', cams_infos, cams_count,
                          byref(cams_found), sizeof(VmbCameraInfo))

        for info in cams_infos[:cams_found.value]:
            result.append(Camera(info, access_mode))

    return tuple(result)
