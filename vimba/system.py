# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, G_VIMBA_HANDLE
from vimba.access_mode import AccessMode
from vimba.feature import discover_features, filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features, FeatureTypes, \
                          FeaturesTuple
from vimba.interface import InterfacesTuple, discover_interfaces
from vimba.camera import CamerasTuple, discover_cameras
from vimba.util import Log, LogConfig, RuntimeTypeCheckEnable


__all__ = [
    'System'
]


class System:
    class __Impl:
        def __init__(self):
            self.__feats: FeaturesTuple = ()
            self.__inters: InterfacesTuple = ()
            self.__cams: CamerasTuple = ()
            self.__cams_access_mode: AccessMode = AccessMode.Full
            self.__nw_discover: bool = True
            self.__context_cnt: int = 0

        def __enter__(self):
            if not self.__context_cnt:
                self._startup()

            self.__context_cnt += 1
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.__context_cnt -= 1

            if not self.__context_cnt:
                self._shutdown()

        @RuntimeTypeCheckEnable()
        def set_camera_access_mode(self, mode: AccessMode):
            """Set default camera access mode"""
            self.__cams_access_mode = mode

        def get_camera_access_mode(self) -> AccessMode:
            """Get default camera access mode"""
            return self.__cams_access_mode

        @RuntimeTypeCheckEnable()
        def set_network_discovery(self, enable: bool):
            """Enable/Disable network camera discovery on context entry"""
            self.__nw_discover = enable

        def get_network_discovery(self) -> bool:
            """TODO"""
            return self.__nw_discover

        @RuntimeTypeCheckEnable()
        def enable_log(self, config: LogConfig):
            Log.get_instance().enable(config)

        def disable_log(self):
            Log.get_instance().disable()

        def get_all_interfaces(self) -> InterfacesTuple:
            return self.__inters

        def get_all_cameras(self) -> CamerasTuple:
            return self.__cams

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

        def _startup(self):
            call_vimba_c_func('VmbStartup')

            self.__feats = discover_features(G_VIMBA_HANDLE)
            self.__inters = discover_interfaces()
            self.__cams = discover_cameras(self.__cams_access_mode, self.__nw_discover)

        def _shutdown(self):
            for feat in self.__feats:
                feat.unregister_all_change_handlers()

            self.__cams = ()
            self.__inters = ()
            self.__feats = ()

            call_vimba_c_func('VmbShutdown')

    __instance = __Impl()

    @staticmethod
    def get_instance() -> '__Impl':
        return System.__instance
