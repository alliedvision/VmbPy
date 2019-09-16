"""System access

This module provides access to Vimba. It provides the starting point
for Camera, Interface and system Feature detection and access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from vimba.c_binding import call_vimba_c_func, G_VIMBA_HANDLE
from vimba.feature import discover_features, filter_features_by_name, filter_features_by_type, \
                          filter_affected_features, filter_selected_features, FeatureTypes, \
                          FeaturesTuple
from vimba.interface import InterfacesTuple, discover_interfaces
from vimba.camera import AccessMode, CamerasTuple, discover_cameras
from vimba.util import Log, LogConfig, RuntimeTypeCheckEnable


__all__ = [
    'System'
]


class System:
    class __Impl:
        """This class allows access to the entire Vimba System.
        System is meant be used in conjunction with the "with" - Statement, upon
        entering the context, all system features, connected cameras and interfaces are detected
        and can be used.
        """

        def __init__(self):
            """Do not call directly. Use System.get_instance() instead."""
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
            """Set default camera access mode.

            Arguments:
                mode - AccessMode to use to open a Camera. This method
                       must be used before entering the Context with the 'with' statement.

            Raises:
                TypeError if 'mode' is not of type AccessMode.
            """
            self.__cams_access_mode = mode

        def get_camera_access_mode(self) -> AccessMode:
            """Get default camera access mode

            Returns:
                Currently configured camera access mode
            """
            return self.__cams_access_mode

        @RuntimeTypeCheckEnable()
        def set_network_discovery(self, enable: bool):
            """Enable/Disable network camera discovery.

            Arguments:
                enable - If 'True' VimbaPython tries to detect cameras connected via Ethernet
                         on entering the 'with' statement. If set to 'False', no network
                         discover occurs.

            Raises:
                TypeError if 'enable' is not of type bool.
            """
            self.__nw_discover = enable

        @RuntimeTypeCheckEnable()
        def enable_log(self, config: LogConfig):
            """Enable VimbaPython's logging mechanism.

            Arguments:
                config - Configuration for the logging mechanism.

            Raises:
                TypeError if 'config' is not of type LogConfig.
            """
            Log.get_instance().enable(config)

        def disable_log(self):
            """Disable VimbaPython's logging mechanism."""
            Log.get_instance().disable()

        def get_all_interfaces(self) -> InterfacesTuple:
            """Get access to all discovered Interfaces:

            Returns:
                A set of all currently detected Interfaces. Returns an empty set then called
                outside of 'with'.
            """
            return self.__inters

        def get_all_cameras(self) -> CamerasTuple:
            """Get access to all discovered Cameras:

            Returns:
                A set of all currently detected Cameras. Returns an empty set then called
                outside of 'with'.
            """
            return self.__cams

        def get_all_features(self) -> FeaturesTuple:
            """Get access to all discovered system features:

            Returns:
                A set of all currently detected Features. Returns an empty set then called
                outside of 'with' - statement.
            """
            return self.__feats

        @RuntimeTypeCheckEnable()
        def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
            """Get all system features affected by a specific system feature.

            Arguments:
                feat - Feature used find features that are affected by feat.

            Returns:
                A set of features affected by changes on 'feat'. Can be an empty set if 'feat'
                does not affect any features.

            Raises:
                TypeError if 'feat' is not of any feature type.
                VimbaFeatureError if 'feat' is not a system feature.
            """
            return filter_affected_features(self.__feats, feat)

        @RuntimeTypeCheckEnable()
        def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
            """Get all system features selected by a specific system feature.

            Arguments:
                feat - Feature used find features that are selected by feat.

            Returns:
                A set of features selected by 'feat'. Can be an empty set if 'feat'
                does not select any features.

            Raises:
                TypeError if feat is not of any feature type.
                VimbaFeatureError if 'feat' is not a system feature.
            """
            return filter_selected_features(self.__feats, feat)

        #@RuntimeTypeCheckEnable()
        def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
            """Get all system features of a specific feature type.

            Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
            EnumFeature, CommandFeature, RawFeature

            Arguments:
                feat_type - FeatureType used find features of that type.

            Returns:
                A set of features of type 'feat_type'. Can be an empty set if there is
                no system feature with the given type available.

            Raises:
                TypeError if 'feat_type' is not of any feature Type.
            """
            return filter_features_by_type(self.__feats, feat_type)

        @RuntimeTypeCheckEnable()
        def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
            """Get a system feature by its name.

            Arguments:
                feat_name - Name used to find a feature.

            Returns:
                Feature with the associated name.

            Raises:
                TypeError if 'feat_name' is not of type 'str'.
                VimbaFeatureError if no feature is associated with 'feat_name'.
            """
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
        """Get VimbaSystem Singleton."""
        return System.__instance
