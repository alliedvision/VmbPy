# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbCameraInfo, VmbAccessMode, VmbHandle, \
                            VmbUint32, G_VIMBA_HANDLE
from vimba.feature import discover_features, discover_feature, \
                          filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features


class Camera:
    def __init__(self, info: VmbCameraInfo):
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
        return 'Camera(id={}, handle={})'.format(self.get_id(), self._handle)

    def __repr__(self):
        rep = 'Camera'
        rep += '(_info=' + repr(self._info)
        rep += ',_handle=' + repr(self._handle)
        rep += ')'
        return rep

    def get_id(self):
        return self._info.cameraIdString.decode()

    def get_name(self):
        return self._info.cameraName.decode()

    def get_model(self):
        return self._info.modelName.decode()

    def get_serial(self):
        return self._info.serialString.decode()

    def get_interface_id(self):
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
        call_vimba_c_func('VmbCameraOpen', self._info.cameraIdString,
                          VmbAccessMode.Full, byref(self._handle))

        self._feats = discover_features(self._handle)

    def _close(self):
        self._feats = ()

        call_vimba_c_func('VmbCameraClose', self._handle)

        self._handle = VmbHandle(0)


def _setup_network_discovery():
    if discover_feature(G_VIMBA_HANDLE, 'GeVTLIsPresent').get():
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllDuration').set(250)
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllOnce').run()


def discover_cameras(network_discovery: bool):
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
            result.append(Camera(info))

    return tuple(result)
