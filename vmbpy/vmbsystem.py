"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import threading
from ctypes import byref, sizeof
from typing import List, Optional

from . import __version__ as VMBPY_VERSION
from .c_binding import (G_VMB_C_HANDLE, VMB_C_VERSION, VMB_IMAGE_TRANSFORM_VERSION, VmbCError,
                        VmbError, VmbHandle, VmbUint32, _as_vmb_file_path, call_vmb_c)
from .camera import (Camera, CameraChangeHandler, CameraEvent, CamerasList, CamerasTuple,
                     VmbCameraInfo)
from .error import VmbCameraError, VmbInterfaceError, VmbSystemError, VmbTransportLayerError
from .featurecontainer import FeatureContainer
from .interface import (Interface, InterfaceChangeHandler, InterfaceEvent, InterfacesDict,
                        InterfacesTuple, VmbInterfaceInfo)
from .shared import read_memory, write_memory
from .transportlayer import (TransportLayer, TransportLayersDict, TransportLayersTuple,
                             VmbTransportLayerInfo)
from .util import (EnterContextOnCall, LeaveContextOnCall, Log, LogConfig, RaiseIfInsideContext,
                   RaiseIfOutsideContext, RuntimeTypeCheckEnable, TraceEnable)

__all__ = [
    'VmbSystem',
]


class VmbSystem:
    class __Impl(FeatureContainer):
        """This class allows access to the entire Vimba X System.
        VmbSystem is meant be used in conjunction with the ``with`` context. Upon entering the
        context, all system features, connected cameras and interfaces are detected and can be used.
        """

        @TraceEnable()
        @LeaveContextOnCall()
        def __init__(self):
            """Do not call directly. Use ``VmbSystem.get_instance()`` instead."""
            super().__init__()

            # self._handle is required so the inheritance from FeatureContainer works as expected to
            # automatically detect and attach/remove feature accessors
            self._handle: VmbHandle = G_VMB_C_HANDLE
            self.__path_configuration: Optional[str] = None

            self.__transport_layers: TransportLayersDict = {}
            self.__inters: InterfacesDict = {}
            self.__inters_lock: threading.Lock = threading.Lock()
            self.__inters_handlers: List[InterfaceChangeHandler] = []
            self.__inters_handlers_lock: threading.Lock = threading.Lock()

            self.__cams: CamerasList = ()
            self.__cams_lock: threading.Lock = threading.Lock()
            self.__cams_handlers: List[CameraChangeHandler] = []
            self.__cams_handlers_lock: threading.Lock = threading.Lock()

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

        def get_version(self) -> str:
            """ Returns version string of vmbpy and underlying dependencies."""
            msg = 'vmbpy: {} (using VmbC: {}, VmbImageTransform: {})'
            return msg.format(VMBPY_VERSION, VMB_C_VERSION, VMB_IMAGE_TRANSFORM_VERSION)

        @RuntimeTypeCheckEnable()
        def enable_log(self, config: LogConfig):
            """Enable vmbpy's logging mechanism.

            Arguments:
                config:
                    Configuration for the logging mechanism.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
            """
            Log.get_instance().enable(config)

        def disable_log(self):
            """Disable vmbpy's logging mechanism."""
            Log.get_instance().disable()

        @RaiseIfInsideContext()
        @TraceEnable()
        def set_path_configuration(self, *args: str):
            """Set the path_configuration parameter that can be passed to VmbStartup.

            Using this is optional. If no path configuration is set, the
            ``GENICAM_GENTL{32|64}_PATH`` environment variables are considered.

            Arguments:
                args:
                    Paths of directories that should be included in the path configuration. Each
                    path should be a separate argument. The paths contain directories to search for
                    .cti files, paths to .cti files and optionally the path to a configuration xml
                    file.

            Returns:
                An instance of self. This allows setting the path configuration while entering the
                ``VmbSystem`` ``with`` context at the same time.

            Example:
                Using the returned instance to directly open the ``with`` context of
                ``VmbSystem``::

                    with vmbpy.VmbSytem.get_instance().set_path_configuration('/foo', '/bar'):
                        # do something
            """
            self.__path_configuration = os.pathsep.join(args)
            return self

        @RaiseIfOutsideContext()
        @TraceEnable()
        @RuntimeTypeCheckEnable()
        def read_memory(self, addr: int, max_bytes: int) -> bytes:  # coverage: skip
            """Read a byte sequence from a given memory address.

            Arguments:
                addr:
                    Starting address to read from.
                max_bytes:
                    Maximum number of bytes to read from addr.

            Returns:
                Read memory contents as bytes.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
                ValueError:
                    If ``addr`` is negative.
                ValueError:
                    If ``max_bytes`` is negative.
                ValueError:
                    If the memory access was invalid.
            """
            # Note: Coverage is skipped. Function is untestable in a generic way.
            return read_memory(G_VMB_C_HANDLE, addr, max_bytes)

        @RaiseIfOutsideContext()
        @TraceEnable()
        @RuntimeTypeCheckEnable()
        def write_memory(self, addr: int, data: bytes):  # coverage: skip
            """ Write a byte sequence to a given memory address.

            Arguments:
                addr:
                    Address to write the content of ``data`` to.
                data:
                    Byte sequence to write at address ``addr``.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
                ValueError:
                    If ``addr`` is negative.
            """
            # Note: Coverage is skipped. Function is untestable in a generic way.
            return write_memory(G_VMB_C_HANDLE, addr, data)

        @RaiseIfOutsideContext()
        def get_all_transport_layers(self) -> TransportLayersTuple:
            """Get access to all loaded Transport Layers.

            Returns:
                A set of all currently loaded Transport Layers.

            Raises:
                RuntimeError:
                    If called outside of ``with`` context.
            """
            return tuple(self.__transport_layers.values())

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_transport_layer_by_id(self, id_: str) -> TransportLayer:
            """Lookup Transport Layer with given Id.

            Arguments:
                id_:
                    Transport Layer Id to search for.

            Returns:
                Transport Layer associated with given Id.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
                VmbTransportLayerError:
                    If Transport Layer with ``id_`` can't be found.
            """
            tls = [tl for tl in self.__transport_layers.values() if id_ == tl.get_id()]

            if not tls:
                raise VmbTransportLayerError('Transport Layer with ID \'{}\' not found.'
                                             ''.format(id_))

            return tls.pop()

        @RaiseIfOutsideContext()
        def get_all_interfaces(self) -> InterfacesTuple:
            """Get access to all discovered Interfaces.

            Returns:
                A set of all currently detected Interfaces.

            Raises:
                RuntimeError:
                    If called outside of ``with`` context.
            """
            with self.__inters_lock:
                return tuple(self.__inters.values())

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_interface_by_id(self, id_: str) -> Interface:
            """Lookup Interface with given Id.

            Arguments:
                id_:
                    Interface Id to search for.

            Returns:
                Interface associated with given Id.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
                VmbInterfaceError:
                    If interface with ``id_`` can't be found.
            """
            with self.__inters_lock:
                inter = [inter for inter in self.__inters.values() if id_ == inter.get_id()]

            if not inter:
                raise VmbInterfaceError('Interface with ID \'{}\' not found.'.format(id_))

            return inter.pop()

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_interfaces_by_tl(self, tl_: TransportLayer) -> InterfacesTuple:
            """Get access to interfaces associated with the given Transport Layer.

            Arguments:
                tl_:
                    Transport Layer whose interfaces should be returned.

            Returns:
                A tuple of all interfaces associated with the given Transport Layer.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
            """
            with self.__inters_lock:
                inters = tuple(i for i in self.__inters.values() if tl_ == i.get_transport_layer())

            return inters

        @RaiseIfOutsideContext()
        def get_all_cameras(self) -> CamerasTuple:
            """Get access to all discovered Cameras.

            Returns:
                A set of all currently detected Cameras.

            Raises:
                RuntimeError:
                    If called outside of ``with`` context.
            """
            with self.__cams_lock:
                return tuple(self.__cams)

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_camera_by_id(self, id_: str) -> Camera:
            """Lookup Camera with given Id.

            Arguments:
                id_:
                    Camera Id to search for. For GigE Cameras, the IP and MAC Address can be used
                    for Camera lookup.

            Returns:
                Camera associated with given Id.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
                VmbCameraError:
                    If camera with ``id_`` can't be found.
            """
            with self.__cams_lock:
                # Search for given Camera Id in all currently detected cameras.
                for cam in self.__cams:
                    if id_ == cam.get_id():
                        return cam

                # If a search by ID fails, the given id_ is almost certain an IP or MAC Address.
                # Try to query this Camera.
                try:
                    new_cam = self.__discover_camera(id_)

                    # new_cam is newly constructed from the given IP or MAC, search in existing
                    # cameras for a Camera with same ID and return that if a match was found.
                    for detected_cam in self.__cams:
                        if new_cam.get_id() == detected_cam.get_id():
                            return detected_cam
                    # If no match in the internal cam list was found, the camera was not discoverd
                    # by `VmbCamerasList` and not announced via an event. This can happen if the
                    # GigE-TL device discovery is not active, but the passed IP address resolved to
                    # a valid device. By detecting it like this, VmbC will now also generate events
                    # for the device and it will be added to `self.__cams` via a `Detected` event.
                    return new_cam

                except VmbCameraError:
                    pass

            raise VmbCameraError('No Camera with Id \'{}\' available.'.format(id_))

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_cameras_by_tl(self, tl_: TransportLayer) -> CamerasTuple:
            """Get access to cameras associated with the given Transport Layer.

            Arguments:
                tl_:
                    Transport Layer whose cameras should be returned.

            Returns:
                A tuple of all cameras associated with the given Transport Layer.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError
                    If called outside of ``with`` context.
            """
            with self.__cams_lock:
                cams = tuple(c for c in self.__cams if tl_ == c.get_transport_layer())

            return cams

        @RaiseIfOutsideContext()
        @RuntimeTypeCheckEnable()
        def get_cameras_by_interface(self, inter_: Interface):
            """Get access to cameras associated with the given interface.

            Arguments:
                inter_:
                    Interface whose cameras should be returned.

            Returns:
                A tuple of all cameras associated with the given interface.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
                RuntimeError:
                    If called outside of ``with`` context.
            """
            with self.__cams_lock:
                cams = tuple(c for c in self.__cams if inter_ == c.get_interface())

            return cams

        @RuntimeTypeCheckEnable()
        def register_camera_change_handler(self, handler: CameraChangeHandler):
            """Add Callable that is executed on camera connect/disconnect.

            Arguments:
                handler:
                    The change handler that shall be added.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
            """
            with self.__cams_handlers_lock:
                if handler not in self.__cams_handlers:
                    self.__cams_handlers.append(handler)

        def unregister_all_camera_change_handlers(self):
            """Remove all currently registered camera change handlers"""
            with self.__cams_handlers_lock:
                if self.__cams_handlers:
                    self.__cams_handlers.clear()

        @RuntimeTypeCheckEnable()
        def unregister_camera_change_handler(self, handler: CameraChangeHandler):
            """Remove previously registered camera change handler.

            Arguments:
                handler:
                    The change handler that shall be removed.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
            """
            with self.__cams_handlers_lock:
                if handler in self.__cams_handlers:
                    self.__cams_handlers.remove(handler)

        @RuntimeTypeCheckEnable()
        def register_interface_change_handler(self, handler: InterfaceChangeHandler):
            """Add Callable that is executed on interface connect/disconnect.

            Arguments:
                handler:
                    The change handler that shall be added.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
            """
            with self.__inters_handlers_lock:
                if handler not in self.__inters_handlers:
                    self.__inters_handlers.append(handler)

        def unregister_all_interface_change_handlers(self):
            """Remove all currently registered interface change handlers."""
            with self.__inters_handlers_lock:
                if self.__inters_handlers:
                    self.__inters_handlers.clear()

        @RuntimeTypeCheckEnable()
        def unregister_interface_change_handler(self, handler: InterfaceChangeHandler):
            """Remove previously registered interface change handler.

            Arguments:
                handler:
                    The change handler that shall be removed.

            Raises:
                TypeError:
                    If parameters do not match their type hint.
            """
            with self.__inters_handlers_lock:
                if handler in self.__inters_handlers:
                    self.__inters_handlers.remove(handler)

        @TraceEnable()
        @EnterContextOnCall()
        def _startup(self):
            Log.get_instance().info('Starting {}'.format(self.get_version()))

            try:
                call_vmb_c('VmbStartup', _as_vmb_file_path(self.__path_configuration))
            except VmbCError as e:
                err = e.get_error_code()
                if err in (VmbError.NoTL, VmbError.TLNotFound):
                    Exc = VmbTransportLayerError
                    msg = 'Encountered an error loading Transport Layers during VmbStartup'
                else:
                    Exc = VmbSystemError
                    msg = 'Encountered an error during VmbStartup'
                if self.__path_configuration:
                    msg += f'. "path_configuration" was set to "{self.__path_configuration}"'
                raise Exc(msg) from e

            self._attach_feature_accessors()

            feat = self.get_feature_by_name('EventInterfaceDiscovery')
            feat.register_change_handler(self.__inter_cb_wrapper)

            feat = self.get_feature_by_name('EventCameraDiscovery')
            feat.register_change_handler(self.__cam_cb_wrapper)

            self.__transport_layers = self.__discover_transport_layers()
            self.__inters = self.__discover_interfaces()
            self.__cams = self.__discover_cameras()

        @TraceEnable()
        @LeaveContextOnCall()
        def _shutdown(self):
            self.unregister_all_camera_change_handlers()
            self.unregister_all_interface_change_handlers()

            for feat in self._feats:
                feat.unregister_all_change_handlers()

            self._remove_feature_accessors()
            self.__cams_handlers = []
            self.__cams = ()
            self.__inters_handlers = []
            for inter in self.__inters.values():
                inter._close()
            self.__inters.clear()
            for tl in self.__transport_layers.values():
                tl._close()
            self.__transport_layers.clear()

            call_vmb_c('VmbShutdown')

        def __cam_cb_wrapper(self, _):   # coverage: skip
            # Skip coverage because it can't be measured. This is called from C-Context
            event = CameraEvent(int(self.get_feature_by_name('EventCameraDiscoveryType').get()))
            cam = None
            cam_id = self.get_feature_by_name('EventCameraDiscoveryCameraID').get()
            log = Log.get_instance()

            try:
                # New camera found: Add it to camera list
                if event == CameraEvent.Detected:
                    cam = self.__discover_camera(cam_id)

                    with self.__cams_lock:
                        self.__cams.append(cam)

                    log.info('Added camera \"{}\" to active cameras'.format(cam_id))

                # Existing camera lost. Remove it from active cameras
                elif event == CameraEvent.Missing:
                    with self.__cams_lock:
                        cam_list = [c for c in self.__cams if cam_id in (c.get_id(), c.get_extended_id())]  # noqa: E501
                        if cam_list:
                            cam = cam_list.pop()
                            cam._disconnected = True
                            self.__cams.remove(cam)

                            log.info('Removed camera \"{}\" from active cameras'.format(cam_id))

                # Camera access mode changed. Need to update cached permitted access modes
                elif event == CameraEvent.Reachable or event == CameraEvent.Unreachable:
                    with self.__cams_lock:
                        cam_list = [c for c in self.__cams if cam_id in (c.get_id(), c.get_extended_id())]  # noqa: E501
                        if cam_list:
                            cam = cam_list.pop()
                            cam._update_permitted_access_modes()
                        else:
                            log.warn('Unexpected access mode change for undiscovered camera \"{}\"'
                                     ''.format(cam_id))
                            cam = self.__discover_camera(cam_id)
                            self.__cams.append(cam)

                    log.info('Updated permitted access modes for camera \"{}\"'.format(cam_id))

                # unknown camera event
                else:
                    cam = self.get_camera_by_id(cam_id)

                with self.__cams_handlers_lock:
                    for handler in self.__cams_handlers:
                        try:
                            handler(cam, event)

                        except Exception as e:
                            msg = 'Caught Exception in handler: '
                            msg += 'Type: {}, '.format(type(e))
                            msg += 'Value: {}, '.format(e)
                            msg += 'raised by: {}'.format(handler)
                            Log.get_instance().error(msg)

            except Exception as e:
                msg = 'Caught Exception in __cam_cb_wrapper: '
                msg += 'Type: {}, '.format(type(e))
                msg += 'Value: {}, '.format(e)
                Log.get_instance().error(msg)

        def __inter_cb_wrapper(self, _):   # coverage: skip
            # Skip coverage because it can't be measured. This is called from C-Context
            event = InterfaceEvent(int(self.get_feature_by_name('EventInterfaceDiscoveryType').get()))  # noqa: E501
            inter = None
            inter_id = self.get_feature_by_name('EventInterfaceDiscoveryInterfaceID').get()
            log = Log.get_instance()

            # New interface found: Add it to interface list
            if event == InterfaceEvent.Detected:
                inter = self.__discover_interface(inter_id)

                with self.__inters_lock:
                    self.__inters[inter._get_handle()] = inter

                log.info('Added interface \"{}\" to active interfaces'.format(inter_id))

            # Existing interface lost. Remove it from active interfaces
            elif event == InterfaceEvent.Missing:
                with self.__inters_lock:
                    inter_list = [i for i in self.__inters.values() if inter_id == i.get_id()]
                    if inter_list:
                        inter = inter_list.pop()
                        del self.__inters[inter._get_handle()]

                        log.info('Removed interface \"{}\" from active interfaces'.format(inter_id))

            else:
                inter = self.get_interface_by_id(inter_id)

            with self.__inters_handlers_lock:
                for handler in self.__inters_handlers:
                    try:
                        handler(inter, event)

                    except Exception as e:
                        msg = 'Caught Exception in handler: '
                        msg += 'Type: {}, '.format(type(e))
                        msg += 'Value: {}, '.format(e)
                        msg += 'raised by: {}'.format(handler)
                        Log.get_instance().error(msg)
                        raise e

        @TraceEnable()
        def __discover_transport_layers(self) -> TransportLayersDict:
            """Do not call directly. Access Transport Layers via vmbpy.VmbSystem instead."""
            result = {}
            transport_layers_count = VmbUint32(0)

            call_vmb_c('VmbTransportLayersList',
                       None,
                       0,
                       byref(transport_layers_count),
                       sizeof(VmbTransportLayerInfo))

            if transport_layers_count:
                transport_layers_found = VmbUint32(0)
                transport_layer_infos = (VmbTransportLayerInfo * transport_layers_count.value)()

                call_vmb_c('VmbTransportLayersList',
                           transport_layer_infos,
                           transport_layers_count,
                           byref(transport_layers_found),
                           sizeof(VmbTransportLayerInfo))
                for info in transport_layer_infos[:transport_layers_found.value]:
                    try:
                        result[info.transportLayerHandle] = TransportLayer(info)
                    except Exception as e:
                        msg = 'Failed to create TransportLayer for {} ({}): {}'
                        msg = msg.format(info.transportLayerName, info.transportLayerPath, e)
                        Log.get_instance().error(msg)

            return result

        @TraceEnable()
        def __discover_interfaces(self) -> InterfacesDict:
            """Do not call directly. Access Interfaces via vmbpy.VmbSystem instead."""

            result = {}
            inters_count = VmbUint32(0)

            call_vmb_c('VmbInterfacesList', None, 0, byref(inters_count), sizeof(VmbInterfaceInfo))

            if inters_count:
                inters_found = VmbUint32(0)
                inters_infos = (VmbInterfaceInfo * inters_count.value)()

                call_vmb_c('VmbInterfacesList', inters_infos, inters_count, byref(inters_found),
                           sizeof(VmbInterfaceInfo))

                for info in inters_infos[:inters_found.value]:
                    try:
                        result[info.interfaceHandle] = Interface(
                            info, self.__transport_layers[info.transportLayerHandle])
                    except Exception as e:
                        msg = 'Failed to create Interface for {}: {}'
                        msg = msg.format(info.interfaceName, e)
                        Log.get_instance().error(msg)

            return result

        @TraceEnable()
        def __discover_interface(self, id_: str) -> Interface:
            """Do not call directly. Access Interfaces via vmbpy.VmbSystem instead."""

            # Since there is no function to query a single interface, discover all interfaces and
            # extract the Interface with the matching ID.
            inters = self.__discover_interfaces().values()
            return [i for i in inters if id_ == i.get_id()].pop()

        @TraceEnable()
        def __discover_cameras(self) -> CamerasList:
            """Do not call directly. Access Cameras via vmbpy.VmbSystem instead."""

            result = []
            cams_count = VmbUint32(0)

            call_vmb_c('VmbCamerasList', None, 0, byref(cams_count), 0)

            if cams_count:
                cams_found = VmbUint32(0)
                cams_infos = (VmbCameraInfo * cams_count.value)()

                call_vmb_c('VmbCamerasList', cams_infos, cams_count, byref(cams_found),
                           sizeof(VmbCameraInfo))

                for info in cams_infos[:cams_found.value]:
                    try:
                        result.append(Camera(info, self.__inters[info.interfaceHandle]))
                    except Exception as e:
                        msg = 'Failed to create Camera for {}: {}'
                        msg = msg.format(info.cameraName, e)
                        Log.get_instance().error(msg)

            return result

        @TraceEnable()
        def __discover_camera(self, id_: str) -> Camera:
            """Do not call directly. Access Cameras via vmbpy.VmbSystem instead."""

            info = VmbCameraInfo()

            # Try to lookup Camera with given ID. If this function
            try:
                call_vmb_c('VmbCameraInfoQuery', id_.encode('utf-8'), byref(info), sizeof(info))

            except VmbCError as e:
                raise VmbCameraError('Failed to query camera info: \"{}\"'
                                     ''.format(str(e.get_error_code()))) from e

            return Camera(info, self.__inters[info.interfaceHandle])

        # Add decorators to inherited methods
        get_all_features = RaiseIfOutsideContext()(FeatureContainer.get_all_features)                  # noqa: E501
        get_features_selected_by = RaiseIfOutsideContext()(FeatureContainer.get_features_selected_by)  # noqa: E501
        get_features_by_type = RaiseIfOutsideContext()(FeatureContainer.get_features_by_type)          # noqa: E501
        get_features_by_category = RaiseIfOutsideContext()(FeatureContainer.get_features_by_category)  # noqa: E501
        get_feature_by_name = RaiseIfOutsideContext()(FeatureContainer.get_feature_by_name)            # noqa: E501

    __instance = __Impl()

    @staticmethod
    @TraceEnable()
    def get_instance() -> '__Impl':
        """Get VmbSystem Singleton."""
        return VmbSystem.__instance

    # Monkey patch class methods that are just remapped VmbSystem functionality. This avoids
    # importing `VmbSystem` from those python files, preventing circular dependencies
    TransportLayer._get_interfaces = lambda self: VmbSystem.__instance.get_interfaces_by_tl(self)  # type: ignore # noqa: E501
    TransportLayer._get_cameras = lambda self: VmbSystem.__instance.get_cameras_by_tl(self)        # type: ignore # noqa: E501
    Interface._get_cameras = lambda self: VmbSystem.__instance.get_cameras_by_interface(self)      # type: ignore # noqa: E501
