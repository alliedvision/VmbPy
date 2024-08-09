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
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

from .c_binding import (AccessMode, VmbCameraInfo, VmbCError, VmbError, VmbHandle, byref,
                        call_vmb_c, decode_cstr, decode_flags, sizeof)
from .error import VmbCameraError
from .featurecontainer import PersistableFeatureContainer
from .frame import AllocationMode, FormatTuple, Frame, PixelFormat
from .localdevice import LocalDevice
from .shared import read_memory, write_memory
from .stream import FrameHandler, Stream, StreamsList, StreamsTuple
from .util import (EnterContextOnCall, LeaveContextOnCall, RaiseIfInsideContext,
                   RaiseIfOutsideContext, RuntimeTypeCheckEnable, TraceEnable, VmbIntEnum)

if TYPE_CHECKING:
    from .feature import EnumFeature
    from .interface import Interface
    from .transportlayer import TransportLayer

__all__ = [
    'AccessMode',
    'Camera',
    'CameraEvent',
    'CamerasTuple',
    'CamerasList',
    'CameraChangeHandler',
]


# Type Forward declarations
CameraChangeHandler = Callable[['Camera', 'CameraEvent'], None]
CamerasTuple = Tuple['Camera', ...]
CamerasList = List['Camera']


class CameraEvent(VmbIntEnum):
    """Enum specifying a Camera Event"""
    Missing = 0      #: A known camera disappeared from the bus
    Detected = 1     #: A new camera was discovered
    Reachable = 2    #: A known camera can be accessed
    Unreachable = 3  #: A known camera cannot be accessed anymore
    Unknown = 4      #: An unknown event occurred


class Camera(PersistableFeatureContainer):
    """This class provides access to a Camera. It corresponds to the GenTL Remote Device.

    Camera is intended be used in conjunction with the ``with`` context. On entering the context,
    all Camera features are detected and can be accessed within the context. Static Camera
    properties like Name and Model can be accessed outside the context.
    """
    @TraceEnable()
    @LeaveContextOnCall()
    def __init__(self, info: VmbCameraInfo, interface: Interface):
        """Do not call directly. Access Cameras via ``vmbpy.VmbSystem`` instead."""
        super().__init__()
        self.__interface: Interface = interface
        self.__streams: StreamsList = []
        self.__local_device: LocalDevice = None  # type: ignore
        self._handle: VmbHandle = VmbHandle(0)
        self.__info: VmbCameraInfo = info
        self.__access_mode: AccessMode = AccessMode.Full
        self.__context_cnt: int = 0
        # Indicator variable that will be set to True when the camera goes missing from VmbSystem
        # (i.e. camera connection is lost)
        self._disconnected = False

    @TraceEnable()
    def __enter__(self):
        if not self.__context_cnt:
            self._open()

        self.__context_cnt += 1
        return self

    @TraceEnable()
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__context_cnt -= 1

        if not self.__context_cnt:
            self._close()

    def __str__(self):
        return 'Camera(id={})'.format(self.get_id())

    @RaiseIfInsideContext()
    @RuntimeTypeCheckEnable()
    def set_access_mode(self, access_mode: AccessMode):
        """Set camera access mode.

        Must be set before the camera connection is opened.

        Arguments:
            access_mode:
                AccessMode for accessing a Camera.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called inside ``with`` context.
        """
        self.__access_mode = access_mode

    def get_access_mode(self) -> AccessMode:
        """Get current camera access mode"""
        return self.__access_mode

    def get_id(self) -> str:
        """Get Camera Id. For example 'DEV_1AB22C00041B'"""
        return decode_cstr(self.__info.cameraIdString)

    def get_extended_id(self) -> str:
        """Get the extended (globally unique) ID of a Camera."""
        return decode_cstr(self.__info.cameraIdExtended)

    def get_name(self) -> str:
        """Get Camera Name. For example 'Allied Vision 1800 U-500m'"""
        return decode_cstr(self.__info.cameraName)

    def get_model(self) -> str:
        """Get Camera Model. For example '1800 U-500m'"""
        return decode_cstr(self.__info.modelName)

    def get_serial(self) -> str:
        """Get Camera serial number. For example '50-0503328442'"""
        return decode_cstr(self.__info.serialString)

    def get_permitted_access_modes(self) -> Tuple[AccessMode, ...]:
        """Get a set of all access modes the camera can be accessed with."""
        return decode_flags(AccessMode, self.__info.permittedAccess)

    def get_transport_layer(self) -> TransportLayer:
        """Get the ``TransportLayer`` instance for this Camera."""
        return self.get_interface().get_transport_layer()

    def get_interface(self) -> Interface:
        """Get the ``Interface`` instance for this Camera."""
        return self.__interface

    def get_interface_id(self) -> str:
        """Get ID of the Interface this camera is connected to. For example 'VimbaUSBInterface_0x0'
        """
        return self.get_interface().get_id()

    @RaiseIfOutsideContext()
    def get_streams(self) -> StreamsTuple:
        """Returns a Tuple containing all instances of ``Stream`` associated with this Camera."""
        return tuple(self.__streams)

    @RaiseIfOutsideContext()
    def get_local_device(self) -> LocalDevice:
        """Returns the instance of ``LocalDevice`` associated with this Camera."""
        return self.__local_device

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
                If called outside ``with`` context.
            ValueError:
                If ``addr`` is negative.
            ValueError:
                If ``max_bytes`` is negative.
            ValueError:
                If the memory access was invalid.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return read_memory(self._handle, addr, max_bytes)

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def write_memory(self, addr: int, data: bytes):  # coverage: skip
        """Write a byte sequence to a given memory address.

        Arguments:
            addr:
                Address to write the content of 'data' too.
            data:
                Byte sequence to write at address 'addr'.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If ``addr`` is negative.
        """
        # Note: Coverage is skipped. Function is untestable in a generic way.
        return write_memory(self._handle, addr, data)

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_frame_generator(self,
                            limit: Optional[int] = None,
                            timeout_ms: int = 2000,
                            allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """Construct frame generator, providing synchronous image acquisition.

        The frame generator acquires a new frame with each execution. Frames may only be used inside
        their respective loop iteration. If a frame must be used outside the loop iteration, a copy
        of the frame must be created (e.g. via ``copy.deepcopy(frame)``).

        Arguments:
            limit:
                The number of images the generator shall acquire (>0). If limit is None, the
                generator will produce an unlimited amount of images and must be stopped by the user
                supplied code.
            timeout_ms:
                Timeout in milliseconds of frame acquisition.
            allocation_mode:
                Allocation mode deciding if buffer allocation should be done by vmbpy or the
                Transport Layer

        Returns:
            Frame generator expression

        Raises:
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If a limit is supplied and ``<= 0``.
            ValueError:
                If a ``timeout_ms`` is negative.
            VmbTimeout:
                If Frame acquisition timed out.
            VmbCameraError:
                If Camera is streaming while executing the generator.
        """
        return self.__streams[0].get_frame_generator(limit=limit,
                                                     timeout_ms=timeout_ms,
                                                     allocation_mode=allocation_mode)

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    @contextlib.contextmanager
    def get_frame_with_context(self,
                               timeout_ms: int = 2000,
                               allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """Gets a single frame from camera to be used inside a context manager.

        Records a single frame from the camera and yields it to the caller for use inside a `with`
        context manager. The frame may only be used inside the context, but may be copied for use
        outside of it (e.g. via ``copy.deepcopy(frame)``). The yielded frame can be used to access
        chunk data.

        Arguments:
            timeout_ms:
                Timeout in milliseconds of frame acquisition.
            allocation_mode:
                Allocation mode deciding if buffer allocation should be done by vmbpy or the
                Transport Layer

        Yields:
            Frame from camera for use in ``with`` context manager

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If a ``timeout_ms`` is negative.
            VmbTimeout:
                If Frame acquisition timed out.
        """
        for frame in self.get_frame_generator(1,
                                              timeout_ms=timeout_ms,
                                              allocation_mode=allocation_mode):
            yield frame

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_frame(self,
                  timeout_ms: int = 2000,
                  allocation_mode: AllocationMode = AllocationMode.AnnounceFrame) -> Frame:
        """Get copy of a single frame from camera. Synchronous frame acquisition.

        Records a single frame from the camera, creates a copy of the frame and returns it to the
        caller. This frame may be used by users as long as they want but can not be used e.g. to
        access chunk data associated with it. See also ``get_frame_with_context`` to avoid the frame
        copy.

        Arguments:
            timeout_ms:
                Timeout in milliseconds of frame acquisition.
            allocation_mode:
                Allocation mode deciding if buffer allocation should be done by vmbpy or the
                Transport Layer

        Returns:
            Frame from camera

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If a timeout_ms is negative.
            VmbTimeout:
                If Frame acquisition timed out.
        """
        return self.__streams[0].get_frame(timeout_ms=timeout_ms,
                                           allocation_mode=allocation_mode)

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def start_streaming(self,
                        handler: FrameHandler,
                        buffer_count: int = 5,
                        allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """Enter streaming mode.

        Enter streaming mode is also known as asynchronous frame acquisition. While active, the
        camera acquires and buffers frames continuously. With each acquired frame, a given
        FrameHandler is called with a new Frame.

        Arguments:
            handler:
                Callable that is executed on each acquired frame.
            buffer_count:
                Number of frames supplied as internal buffer.
            allocation_mode:
                Allocation mode deciding if buffer allocation should be done by vmbpy or the
                Transport Layer

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If buffer is less or equal to zero.
            VmbCameraError:
                If the camera is already streaming.
            VmbCameraError:
                If anything went wrong on entering streaming mode.
        """
        self.__streams[0].start_streaming(handler=handler,
                                          buffer_count=buffer_count,
                                          allocation_mode=allocation_mode)

    @RaiseIfOutsideContext()
    @TraceEnable()
    def stop_streaming(self):
        """Leave streaming mode.

        Leave asynchronous frame acquisition. If streaming mode was not activated before, it just
        returns silently.

        Raises:
            RuntimeError:
                If called outside ``with`` context.
            VmbCameraError:
                If anything went wrong on leaving streaming mode.
        """
        self.__streams[0].stop_streaming()

    @TraceEnable()
    def is_streaming(self) -> bool:
        """Returns ``True`` if the camera is currently in streaming mode. If not, returns ``False``.
        """
        try:
            return self.__streams[0].is_streaming()
        except IndexError:
            # No streams are opened. So the camera connection is not open. Cam is not streaming
            return False

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def queue_frame(self, frame: Frame):
        """Reuse acquired frame in streaming mode.

        Add given frame back into the frame queue used in streaming mode. This should be the last
        operation on a registered ``FrameHandler``. If streaming mode is not active, it returns
        silently.

        Arguments:
            frame:
                The frame to reuse.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            ValueError:
                If the given frame is not from the internal buffer queue.
            RuntimeError:
                If called outside ``with`` context.
            VmbCameraError:
                If reusing the frame was unsuccessful.
        """
        self.__streams[0].queue_frame(frame=frame)

    @RaiseIfOutsideContext()
    @TraceEnable()
    def get_pixel_formats(self) -> FormatTuple:
        """Get supported pixel formats from Camera.

        Returns:
            All pixel formats the camera supports

        Raises:
            RuntimeError:
                If called outside ``with`` context.
        """
        result = []
        feat: EnumFeature = self.get_feature_by_name('PixelFormat')  # type: ignore

        # Build intersection between PixelFormat Enum Values and PixelFormat
        # Note: The Mapping is a bit complicated due to different writing styles within
        #       Feature EnumEntries and PixelFormats
        all_fmts = set([k.upper() for k in PixelFormat.__members__])
        all_enum_fmts = set([str(k).upper() for k in feat.get_available_entries()])
        fmts = all_fmts.intersection(all_enum_fmts)

        for k in PixelFormat.__members__:
            if k.upper() in fmts:
                result.append(PixelFormat[k])

        return tuple(result)

    @RaiseIfOutsideContext()
    @TraceEnable()
    def get_pixel_format(self):
        """Get current pixel format.

        Returns:
            Current pixel format set on the camera.

        Raises:
            RuntimeError:
                If called outside ``with`` context.
        """
        enum_value = str(self.get_feature_by_name('PixelFormat').get()).upper()

        for k in PixelFormat.__members__:
            if k.upper() == enum_value:
                return PixelFormat[k]

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def set_pixel_format(self, fmt: PixelFormat):
        """Set current pixel format.

        Arguments:
            fmt:
                Pixel format to set on the camera.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If the given pixel format is not supported by the cameras.
        """
        if fmt not in self.get_pixel_formats():
            raise ValueError('Camera does not support PixelFormat \'{}\''.format(str(fmt)))

        feat: EnumFeature = self.get_feature_by_name('PixelFormat')  # type: ignore
        fmt_str = str(fmt).upper()

        for entry in feat.get_available_entries():
            if str(entry).upper() == fmt_str:
                feat.set(entry)

    @TraceEnable()
    @EnterContextOnCall()
    def _open(self):
        try:
            call_vmb_c('VmbCameraOpen', self.__info.cameraIdString, self.__access_mode,
                       byref(self._handle))

        except VmbCError as e:
            err = e.get_error_code()

            # In theory InvalidAccess should be thrown on using a non permitted access mode.
            # In reality VmbError.NotImplemented_ is sometimes returned.
            if err in (VmbError.InvalidAccess, VmbError.NotImplemented_):
                msg = 'Accessed Camera \'{}\' with invalid Mode \'{}\'. Valid modes are: {}'
                msg = msg.format(self.get_id(), str(self.__access_mode),
                                 self.get_permitted_access_modes())
                exc = VmbCameraError(msg)
            elif err == VmbError.InUse:
                msg = 'Accessed Camera \'{}\' is already in use. Could not be opened with access ' \
                      'mode \'{}\'. Valid modes are: {}'
                msg = msg.format(self.get_id(), str(self.__access_mode),
                                 self.get_permitted_access_modes())
                exc = VmbCameraError(msg)
            elif err == VmbError.NotFound:
                msg = 'Camera with ID \'{}\' could not be found.'
                msg = msg.format(self.get_id())
                exc = VmbCameraError(msg)
            else:
                exc = VmbCameraError(repr(err))

            raise exc from e

        try:
            call_vmb_c('VmbCameraInfoQueryByHandle',
                       self._handle,
                       byref(self.__info),
                       sizeof(self.__info))
        except VmbCError as e:
            try:
                call_vmb_c('VmbCameraClose', self._handle)
            except Exception:
                pass
            err = e.get_error_code()
            if err == VmbError.BadHandle:
                msg = 'Invalid handle used to query camera info. Used handle: {}'
                msg = msg.format(self._handle)
                exc - VmbCameraError(msg)
            else:
                exc = VmbCameraError(repr(err))
            raise exc from e

        try:
            for i in range(self.__info.streamCount):
                # The stream at index 0 is automatically opened
                self.__streams.append(Stream(stream_handle=self.__info.streamHandles[i],
                                             is_open=(i == 0),
                                             parent_cam=self))
            self.__local_device = LocalDevice(self.__info.localDeviceHandle)
            self._attach_feature_accessors()
        except VmbCError as e:
            try:
                call_vmb_c('VmbCameraClose', self._handle)
            except Exception:
                pass
            err = e.get_error_code()
            exc = VmbCameraError(repr(err))
            raise exc from e

    @TraceEnable()
    @LeaveContextOnCall()
    def _close(self):
        try:
            for feat in self._feats:
                feat.unregister_all_change_handlers()

            self._remove_feature_accessors()

            self.__local_device._close()

            for stream in self.__streams:
                if stream.is_streaming():
                    stream.stop_streaming()
                stream.close()
        except Exception:
            pass
        finally:
            # VmbCameraClose must be called in any case
            call_vmb_c('VmbCameraClose', self._handle)
            self._handle = VmbHandle(0)
            self.__streams = []
            self.__local_device = None

    @TraceEnable()
    def _update_permitted_access_modes(self):
        info = VmbCameraInfo()
        try:
            call_vmb_c('VmbCameraInfoQuery',
                       self.get_id().encode('utf-8'),
                       byref(info),
                       sizeof(info))

        except VmbCError as e:
            raise VmbCameraError(str(e.get_error_code())) from e
        self.__info.permittedAccess = info.permittedAccess

    # Add decorators to inherited methods
    get_all_features = RaiseIfOutsideContext()(PersistableFeatureContainer.get_all_features)                   # noqa: E501
    get_features_selected_by = RaiseIfOutsideContext()(PersistableFeatureContainer.get_features_selected_by)   # noqa: E501
    get_features_by_type = RaiseIfOutsideContext()(PersistableFeatureContainer.get_features_by_type)           # noqa: E501
    get_features_by_category = RaiseIfOutsideContext()(PersistableFeatureContainer.get_features_by_category)   # noqa: E501
    get_feature_by_name = RaiseIfOutsideContext()(PersistableFeatureContainer.get_feature_by_name)             # noqa: E501
    load_settings = RaiseIfOutsideContext()(PersistableFeatureContainer.load_settings)
    save_settings = RaiseIfOutsideContext()(PersistableFeatureContainer.save_settings)
