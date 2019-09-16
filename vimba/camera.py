# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from typing import Tuple
from vimba.c_binding import call_vimba_c_func, byref, sizeof, decode_cstr, decode_flags
from vimba.c_binding import VmbCameraInfo, VmbHandle, VmbUint32, G_VIMBA_HANDLE
from vimba.access_mode import AccessMode
from vimba.feature import discover_features, discover_feature, filter_features_by_name, \
                          filter_features_by_type, filter_affected_features, \
                          filter_selected_features, FeatureTypes, FeaturesTuple
from vimba.util import RuntimeTypeCheckEnable


__all__ = [
    'Camera',
    'CamerasTuple',
    'discover_cameras'
]


class Camera:
    def __init__(self, info: VmbCameraInfo, access_mode: AccessMode):
        self.__handle: VmbHandle = VmbHandle(0)
        self.__info: VmbCameraInfo = info
        self.__access_mode: AccessMode = access_mode
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
        return 'Camera(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Camera'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    @RuntimeTypeCheckEnable()
    def set_access_mode(self, access_mode: AccessMode):
        self.__access_mode = access_mode

    def get_access_mode(self) -> AccessMode:
        return self.__access_mode

    def get_id(self) -> str:
        return decode_cstr(self.__info.cameraIdString)

    def get_name(self) -> str:
        return decode_cstr(self.__info.cameraName)

    def get_model(self) -> str:
        return decode_cstr(self.__info.modelName)

    def get_serial(self) -> str:
        return decode_cstr(self.__info.serialString)

    def get_permitted_access_modes(self) -> Tuple[AccessMode, ...]:
        return decode_flags(AccessMode, self.__info.permittedAccess)

    def get_interface_id(self) -> str:
        return decode_cstr(self.__info.interfaceIdString)

    def get_all_features(self) -> FeaturesTuple:
        return self.__feats

    @RuntimeTypeCheckEnable()
    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        return filter_affected_features(self.__feats, feat)

    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        return filter_selected_features(self.__feats, feat)

    #@RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
        return filter_features_by_type(self.__feats, feat_type)

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        return filter_features_by_name(self.__feats, feat_name)

    def _open(self):
        call_vimba_c_func('VmbCameraOpen', self.__info.cameraIdString, self.__access_mode,
                          byref(self.__handle))

        self.__feats = discover_features(self.__handle)

    def _close(self):
        for feat in self.__feats:
            feat.unregister_all_change_handlers()

        self.__feats = ()

        call_vimba_c_func('VmbCameraClose', self.__handle)

        self.__handle = VmbHandle(0)


def _setup_network_discovery():
    if discover_feature(G_VIMBA_HANDLE, 'GeVTLIsPresent').get():
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllDuration').set(250)
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllOnce').run()


CamerasTuple = Tuple[Camera, ...]


def discover_cameras(access_mode: AccessMode, network_discovery: bool) -> CamerasTuple:
    if network_discovery:
        _setup_network_discovery()

    result = []
    cams_count = VmbUint32(0)

    call_vimba_c_func('VmbCamerasList', None, 0, byref(cams_count), 0)

    if cams_count:
        cams_found = VmbUint32(0)
        cams_infos = (VmbCameraInfo * cams_count.value)()

        call_vimba_c_func('VmbCamerasList', cams_infos, cams_count, byref(cams_found),
                          sizeof(VmbCameraInfo))

        for info in cams_infos[:cams_found.value]:
            result.append(Camera(info, access_mode))

    return tuple(result)
