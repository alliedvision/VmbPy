"""System access

This module provides access to Vimba. It provides the starting point
for Camera, Interface and system Feature detection and access.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
from threading import Lock
from typing import List
from .c_binding import call_vimba_c_func, G_VIMBA_C_HANDLE
from .feature import discover_features, filter_features_by_name, filter_features_by_type, \
                     filter_affected_features, filter_selected_features, FeatureTypes, \
                     FeaturesTuple, EnumFeature
from .interface import Interface, InterfaceChangeHandler, InterfacesTuple, InterfacesList, \
                       discover_interfaces, discover_interface
from .camera import AccessMode, Camera, CameraChangeHandler, CamerasTuple, CamerasList, \
                    discover_cameras, discover_camera
from .util import Log, LogConfig, TraceEnable, RuntimeTypeCheckEnable
from .error import VimbaCameraError, VimbaInterfaceError


__all__ = [
    'Vimba'
]


class Vimba:
    class __Impl:
        """This class allows access to the entire Vimba System.
        Vimba is meant be used in conjunction with the "with" - Statement, upon
        entering the context, all system features, connected cameras and interfaces are detected
        and can be used.
        """

        @TraceEnable()
        def __init__(self):
            """Do not call directly. Use Vimba.get_instance() instead."""
            self.__feats: FeaturesTuple = ()

            self.__inters: InterfacesList = ()
            self.__inters_lock: Lock = Lock()
            self.__inters_handlers: List[InterfaceChangeHandler] = []
            self.__inters_handlers_lock: Lock = Lock()

            self.__cams: CamerasList = ()
            self.__cams_lock: Lock = Lock()
            self.__cams_access_mode: AccessMode = AccessMode.Full
            self.__cams_capture_timeout: int = 2000
            self.__cams_handlers: List[CameraChangeHandler] = []
            self.__cams_handlers_lock: Lock = Lock()

            self.__nw_discover: bool = True
            self.__context_cnt: int = 0

        @TraceEnable()
        def __enter__(self):
            if not self.__context_cnt:
                self._startup()

            self.__context_cnt += 1
            return self

        @TraceEnable()
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
        def set_camera_capture_timeout(self, millis):
            """Set default camera frame capture timeout in milliseconds.

            Arguments:
                millis - The new default capture timeout to use.

            Raises:
                TypeError if 'millis' is no integer.
                ValueError if 'millis' is negative
            """
            if millis <= 0:
                raise ValueError('Given Timeout {} must be positive.'.format(millis))

            self.__cams_capture_timeout = millis

        def get_camera_capture_timeout(self) -> int:
            """Get default camera frame capture timeout in milliseconds"""
            return self.__cams_capture_timeout

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
            with self.__inters_lock:
                return tuple(self.__inters)

        @RuntimeTypeCheckEnable()
        def get_interface_by_id(self, id_: str) -> Interface:
            """Lookup Interface with given ID.

            Arguments:
                id_ - Interface Id to search for.

            Returns:
                Interface associated with given Id

            Raises:
                VimbaInterfaceError if interface with id_ can't be found.
            """
            with self.__inters_lock:
                inter = [inter for inter in self.__inters if id_ == inter.get_id()]

            if not inter:
                raise VimbaInterfaceError('Interface with ID \'{}\' not found.'.format(id_))

            return inter.pop()

        def get_all_cameras(self) -> CamerasTuple:
            """Get access to all discovered Cameras.

            Returns:
                A set of all currently detected Cameras. Returns an empty set then called
                outside of 'with'.
            """
            with self.__cams_lock:
                return tuple(self.__cams)

        @RuntimeTypeCheckEnable()
        def get_camera_by_id(self, id_: str) -> Camera:
            """Lookup Camera with given ID.

            Arguments:
                id_ - Camera Id to search for.

            Returns:
                Camera associated with given Id

            Raises:
                VimbaCameraError if camera with id_ can't be found.
            """
            with self.__cams_lock:
                cam = [cam for cam in self.__cams if id_ == cam.get_id()]

            if not cam:
                raise VimbaCameraError('Camera with ID \'{}\' not found.'.format(id_))

            return cam.pop()

        def get_all_features(self) -> FeaturesTuple:
            """Get access to all discovered system features:

            Returns:
                A set of all currently detected Features. Returns an empty set then called
                outside of 'with' - statement.
            """
            return self.__feats

        @TraceEnable()
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

        @TraceEnable()
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

        @RuntimeTypeCheckEnable()
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

        #@RuntimeTypeCheckEnable()
        def register_camera_change_handler(self, handler: CameraChangeHandler):
            """Add Callable what is executed on camera connect/disconnect

            Arguments:
                handler - The change handler that shall be added.

            Raises:
                TypeError if 'handler' is not of Type Callable[[Camera, bool], None]
            """
            with self.__cams_handlers_lock:
                if handler not in self.__cams_handlers:
                    self.__cams_handlers.append(handler)

        def unregister_all_camera_change_handlers(self):
            """Remove all currently registered camera change handlers"""
            with self.__cams_handlers_lock:
                if self.__cams_handlers:
                    self.__cams_handlers.clear()

        #@RuntimeTypeCheckEnable()
        def unregister_camera_change_handler(self, handler: CameraChangeHandler):
            """Remove previously registered camera change handler

            Arguments:
                handler - The change handler that shall be removed.

            Raises:
                TypeError if 'handler' is not of Type Callable[[Camera, bool], None]
            """
            with self.__cams_handlers_lock:
                if handler in self.__cams_handlers:
                    self.__cams_handlers.remove(handler)

        # @RuntimeTypeCheckEnable()
        def register_interface_change_handler(self, handler: InterfaceChangeHandler):
            """Add Callable what is executed on interface connect/disconnect

            Arguments:
                handler - The change handler that shall be added.

            Raises:
                TypeError if 'handler' is not of Type Callable[[Interface, bool], None]
            """
            with self.__inters_handlers_lock:
                if handler not in self.__inters_handlers:
                    self.__inters_handlers.append(handler)

        def unregister_all_interface_change_handlers(self):
            """Remove all currently registered interface change handlers"""
            with self.__inters_handlers_lock:
                if self.__inters_handlers:
                    self.__inters_handlers.clear()

        # @RuntimeTypeCheckEnable()
        def unregister_interface_change_handler(self, handler: InterfaceChangeHandler):
            """Remove previously registered interface change handler

            Arguments:
                handler - The change handler that shall be removed.

            Raises:
                TypeError if 'handler' is not of Type Callable[[Interface, bool], None]
            """
            with self.__inters_handlers_lock:
                if handler in self.__inters_handlers:
                    self.__inters_handlers.remove(handler)

        @TraceEnable()
        def _startup(self):
            call_vimba_c_func('VmbStartup')

            self.__feats = discover_features(G_VIMBA_C_HANDLE)
            self.__inters = discover_interfaces()
            self.__cams = discover_cameras(self.__cams_access_mode, self.__cams_capture_timeout,
                                           self.__nw_discover)

            feat = self.get_feature_by_name('DiscoveryInterfaceEvent')
            feat.register_change_handler(self.__cam_cb_wrapper)

            feat = self.get_feature_by_name('DiscoveryCameraEvent')
            feat.register_change_handler(self.__inter_cb_wrapper)

        @TraceEnable()
        def _shutdown(self):
            self.unregister_all_camera_change_handlers()
            self.unregister_all_interface_change_handlers()

            for feat in self.__feats:
                feat.unregister_all_change_handlers()

            self.__cams_handlers = []
            self.__cams = ()
            self.__inters_handlers = []
            self.__inters = ()
            self.__feats = ()

            call_vimba_c_func('VmbShutdown')

        def __cam_cb_wrapper(self, cam_event: EnumFeature):   # coverage: skip
            # Skip coverage because it can't be measured. This is called from C-Context

            # Early return for 'Unrechable', 'Reachable'. These value are triggered on
            # camera open/camera close. This handler is for detection of new cameras only.
            event = str(cam_event.get())

            if event in ('Unreachable', 'Reachable'):
                return

            cam_avail = True if event == 'Detected' else False
            cam_id = self.get_feature_by_name('DiscoveryCameraIdent').get()
            log = Log.get_instance()

            if cam_avail:
                cam = discover_camera(cam_id, self.__cams_access_mode, self.__cams_capture_timeout)

                with self.__cams_lock:
                    self.__cams.append(cam)

                msg = 'Added camera \"{}\" to active cameras'

            else:
                with self.__cams_lock:
                    cam = [c for c in self.__cams if cam_id == c.get_id()].pop()
                    self.__cams.remove(cam)

                msg = 'Removed camera \"{}\" from active cameras'

            log.info(msg.format(cam_id))

            with self.__cams_handlers_lock:
                for handler in self.__cams_handlers:
                    try:
                        handler(cam, cam_avail)

                    except BaseException as e:
                        msg = 'Caught Exception in handler: '
                        msg += 'Type: {}, '.format(type(e))
                        msg += 'Value: {}, '.format(e)
                        msg += 'raised by: {}'.format(handler)

                        Log.get_instance().error(msg)

        def __inter_cb_wrapper(self, inter_event: EnumFeature):   # coverage: skip
            # Skip coverage because it can't be measured. This is called from C-Context
            inter_avail = True if str(inter_event.get()) == 'Available' else False
            inter_id = self.get_feature_by_name('DiscoveryInterfaceIdent').get()
            log = Log.get_instance()

            if inter_avail:
                inter = discover_interface(inter_id)

                with self.__inters_lock:
                    self.__inters.append(inter)

                msg = 'Added interface \"{}\" to active interfaces'

            else:
                with self.__inters_lock:
                    inter = [i for i in self.__inters if inter_id == i.get_id()].pop()
                    self.__inters.remove(inter)

                msg = 'Removed interface \"{}\" from active interfaces'

            log.info(msg.format(inter_id))

            with self.__inters_handlers_lock:
                for handler in self.__inters_handlers:
                    try:
                        handler(inter, inter_avail)

                    except BaseException as e:
                        msg = 'Caught Exception in handler: '
                        msg += 'Type: {}, '.format(type(e))
                        msg += 'Value: {}, '.format(e)
                        msg += 'raised by: {}'.format(handler)

                        Log.get_instance().error(msg)

    __instance = __Impl()

    @staticmethod
    @TraceEnable()
    def get_instance() -> '__Impl':
        """Get VimbaSystem Singleton."""
        return Vimba.__instance
