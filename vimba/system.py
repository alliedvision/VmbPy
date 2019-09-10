# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, G_VIMBA_HANDLE
from vimba.access_mode import AccessMode
from vimba.feature import discover_features, filter_features_by_name, \
                          filter_features_by_type, filter_affected_features, \
                          filter_selected_features
from vimba.interface import discover_interfaces
from vimba.camera import discover_cameras
from vimba.logging import Log, LogConfig


class System:
    class _Impl:
        def __init__(self):
            self._feats = ()
            self._inters = ()
            self._cams = ()
            self._cams_access_mode = AccessMode.Full
            self._nw_discover = True
            self._context_cnt = 0

        def __enter__(self):
            if not self._context_cnt:
                self._startup()

            self._context_cnt += 1
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self._context_cnt -= 1

            if not self._context_cnt:
                self._shutdown()

        def set_camera_access_mode(self, mode: AccessMode):
            self._cams_access_mode = mode

        def get_camera_access_mode(self):
            return self._cams_access_mode

        def set_network_discovery(self, enable: bool):
            self._nw_discover = enable

        def get_network_discovery(self):
            return self._nw_discover

        def enable_log(self, config: LogConfig):
            Log.get_instance().enable(config)

        def disable_log(self):
            Log.get_instance().disable()

        def get_all_interfaces(self):
            return self._inters

        def get_all_cameras(self):
            return self._cams

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

        def _startup(self):
            call_vimba_c_func('VmbStartup')

            self._feats = discover_features(G_VIMBA_HANDLE)
            self._inters = discover_interfaces()
            self._cams = discover_cameras(self._cams_access_mode,
                                          self._nw_discover)

        def _shutdown(self):
            for feat in self._feats:
                feat.unregister_all_change_handlers()

            self._cams = ()
            self._inters = ()
            self._feats = ()

            call_vimba_c_func('VmbShutdown')

    _instance = _Impl()

    @staticmethod
    def get_instance():
        return System._instance
