"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
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

import copy
from ctypes import POINTER
import threading
from typing import List, Tuple, Dict, Union, Optional, cast, Callable, TYPE_CHECKING

from .c_binding import call_vmb_c, byref, sizeof, \
                       VmbHandle, VmbCError, VmbFrame, VmbError, AccessMode, build_callback_type, \
                       VmbUint32
from .error import VmbSystemError, VmbCameraError, VmbTimeout, VmbFeatureError
from .featurecontainer import PersistableFeatureContainer
from .frame import Frame, AllocationMode
from .util import TraceEnable, Log, RuntimeTypeCheckEnable, enter_context_on_call, leave_context_on_call

if TYPE_CHECKING:
    from .camera import Camera
    from .frame import FrameTuple


__all__ = [
    'Stream',
    'StreamsList',
    'StreamsTuple',
    'StreamsDict'
]

StreamsList = List['Stream']
StreamsTuple = Tuple['Stream', ...]
StreamsDict = Dict[VmbHandle, 'Stream']
FrameHandler = Callable[['Camera', 'Stream', Frame], None]


class _Context:
    def __init__(self, cam, stream, frames, handler, callback):
        self.cam: Camera = cam
        self.stream: Stream = stream
        self.stream_handle: VmbHandle = stream._handle
        self.frames: FrameTuple = frames
        self.frames_lock = threading.Lock()
        self.frames_handler = handler
        self.frames_callback = callback


class _State:
    def __init__(self, context: _Context):
        self.context = context


class _StateInit(_State):
    @TraceEnable()
    def forward(self) -> Union[_State, VmbCameraError]:
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vmb_c('VmbFrameAnnounce', self.context.stream_handle, byref(frame_handle),
                           sizeof(frame_handle))
                if frame._allocation_mode == AllocationMode.AllocAndAnnounceFrame:
                    assert frame_handle.buffer is not None
                    frame._set_buffer(frame_handle.buffer)

            except VmbCError as e:
                return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateAnnounced(self.context)


class _StateAnnounced(_State):
    @TraceEnable()
    def forward(self) -> Union[_State, VmbCameraError]:
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vmb_c('VmbCaptureFrameQueue', self.context.stream_handle, byref(frame_handle),
                           self.context.frames_callback)

            except VmbCError as e:
                return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateQueued(self.context)

    @TraceEnable()
    def backward(self) -> Union[_State, VmbCameraError]:
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vmb_c('VmbFrameRevoke', self.context.stream_handle, byref(frame_handle))

            except VmbCError as e:
                return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateInit(self.context)


class _StateQueued(_State):
    @TraceEnable()
    def forward(self) -> Union[_State, VmbCameraError]:
        try:
            call_vmb_c('VmbCaptureStart', self.context.stream_handle)

        except VmbCError as e:
            return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateCaptureStarted(self.context)

    @TraceEnable()
    def backward(self) -> Union[_State, VmbCameraError]:
        try:
            call_vmb_c('VmbCaptureQueueFlush', self.context.stream_handle)

        except VmbCError as e:
            return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateAnnounced(self.context)


class _StateCaptureStarted(_State):
    @TraceEnable()
    def forward(self) -> Union[_State, VmbCameraError]:
        try:
            # Skip Command execution on AccessMode.Read (required for Multicast Streaming)
            if self.context.cam.get_access_mode() != AccessMode.Read:
                self.context.cam.get_feature_by_name('AcquisitionStart').run()

        except BaseException as e:
            return VmbCameraError(str(e))

        return _StateAcquiring(self.context)

    @TraceEnable()
    def backward(self) -> Union[_State, VmbCameraError]:
        try:
            call_vmb_c('VmbCaptureEnd', self.context.stream_handle)

        except VmbCError as e:
            return _build_camera_error(self.context.cam, self.context.stream, e)

        return _StateQueued(self.context)


class _StateAcquiring(_State):
    @TraceEnable()
    def backward(self) -> Union[_State, VmbCameraError]:
        try:
            # Skip Command execution on AccessMode.Read (required for Multicast Streaming)
            if self.context.cam.get_access_mode() != AccessMode.Read:
                self.context.cam.get_feature_by_name('AcquisitionStop').run()

        except BaseException as e:
            return VmbCameraError(str(e))

        return _StateCaptureStarted(self.context)

    @TraceEnable()
    def wait_for_frames(self, timeout_ms: int):
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vmb_c('VmbCaptureFrameWait', self.context.stream_handle, byref(frame_handle),
                           timeout_ms)

            except VmbCError as e:
                raise _build_camera_error(self.context.cam, self.context.stream, e) from e

    @TraceEnable()
    def queue_frame(self, frame):
        frame_handle = _frame_handle_accessor(frame)

        try:
            call_vmb_c('VmbCaptureFrameQueue', self.context.stream_handle, byref(frame_handle),
                       self.context.frames_callback)

        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e


class _CaptureFsm:
    def __init__(self, context: _Context):
        self.__context = context
        self.__state = _StateInit(self.__context)

    def get_context(self) -> _Context:
        return self.__context

    def enter_capturing_mode(self):
        # Forward state machine until the end or an error occurs
        exc = None

        while not exc:
            try:
                state_or_exc = self.__state.forward()

            except AttributeError:
                break

            if isinstance(state_or_exc, _State):
                self.__state = state_or_exc

            else:
                exc = state_or_exc

        return exc

    def leave_capturing_mode(self):
        # Revert state machine until the initial state is reached or an error occurs
        exc = None

        while not exc:
            try:
                state_or_exc = self.__state.backward()

            except AttributeError:
                break

            if isinstance(state_or_exc, _State):
                self.__state = state_or_exc

            else:
                exc = state_or_exc

        return exc

    def wait_for_frames(self, timeout_ms: int):
        # Wait for Frames only in AcquiringMode
        if isinstance(self.__state, _StateAcquiring):
            self.__state.wait_for_frames(timeout_ms)

    def queue_frame(self, frame):
        # Queue Frame only in AcquiringMode
        if isinstance(self.__state, _StateAcquiring):
            self.__state.queue_frame(frame)


@TraceEnable()
def _frame_generator(cam: Camera,
                     stream: Stream,
                     limit: Optional[int],
                     timeout_ms: int,
                     allocation_mode: AllocationMode):
    if stream.is_streaming():
        raise VmbCameraError('Operation not supported while streaming.')

    # frame_data_size = stream.get_feature_by_name('PayloadSize').get()
    frame_data_size = VmbUint32(0)
    try:
        call_vmb_c('VmbPayloadSizeGet', stream._handle, byref(frame_data_size))

    except VmbCError as e:
        raise _build_camera_error(cam, stream, e) from e
    try:
        buffer_alignment = stream.get_feature_by_name('StreamBufferAlignment').get()
    except VmbFeatureError:
        buffer_alignment = 1
    frames = (Frame(frame_data_size.value, allocation_mode, buffer_alignment=buffer_alignment), )
    fsm = _CaptureFsm(_Context(cam, stream, frames, None, None))
    cnt = 0

    try:
        while True if limit is None else cnt < limit:
            # Enter Capturing mode
            exc = fsm.enter_capturing_mode()
            if exc:
                raise exc

            fsm.wait_for_frames(timeout_ms)

            # Return copy of internally used frame to keep them independent.
            frame_copy = copy.deepcopy(frames[0])
            fsm.leave_capturing_mode()
            frame_copy._frame.frameID = cnt
            cnt += 1

            yield frame_copy

    finally:
        # Leave Capturing mode
        exc = fsm.leave_capturing_mode()
        if exc:
            raise exc


class Stream(PersistableFeatureContainer):
    """This class provides access to a Stream of a Camera
    """
    @TraceEnable()
    def __init__(self, stream_handle: VmbHandle, is_open: bool, parent_cam: Camera) -> None:
        super().__init__()
        self._parent_cam: Camera = parent_cam
        self._handle: VmbHandle = stream_handle
        self.__capture_fsm: Optional[_CaptureFsm] = None
        self.__is_open: bool = False
        if is_open:
            self.open()

    @TraceEnable()
    @enter_context_on_call
    def open(self):
        if not self.__is_open:
            self._attach_feature_accessors()
            self.__is_open = True

    @TraceEnable()
    @leave_context_on_call
    def close(self):
        if self.__is_open:
            self._remove_feature_accessors()
            self.__is_open = False

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_frame_generator(self,
                            limit: Optional[int] = None,
                            timeout_ms: int = 2000,
                            allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        if limit and (limit < 0):
            raise ValueError('Given Limit {} is not >= 0'.format(limit))

        if timeout_ms <= 0:
            raise ValueError('Given Timeout {} is not > 0'.format(timeout_ms))

        return _frame_generator(self._parent_cam, self, limit, timeout_ms, allocation_mode)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_frame(self,
                  timeout_ms: int = 2000,
                  allocation_mode: AllocationMode = AllocationMode.AnnounceFrame) -> Frame:
        """Get single frame from camera. Synchronous frame acquisition.

        Arguments:
            timeout_ms - Timeout in milliseconds of frame acquisition.
            allocation_mode - Allocation mode deciding if buffer allocation should be done by
                              vmbpy or the Transport Layer

        Returns:
            Frame from camera

        Raises:
            TypeError if parameters do not match their type hint.
            RuntimeError if called outside "with" - statement scope.
            ValueError if a timeout_ms is negative.
            VmbTimeout if Frame acquisition timed out.
        """
        return next(self.get_frame_generator(1, timeout_ms, allocation_mode))

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def start_streaming(self,
                        handler: FrameHandler,
                        buffer_count: int = 5,
                        allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        if buffer_count <= 0:
            raise ValueError('Given buffer_count {} must be positive'.format(buffer_count))

        if self.is_streaming():
            raise VmbCameraError('Stream \'{}\' of camera \'{}\'already streaming.'
                                 ''.format(self, self._parent_cam.get_id()))

        # Setup capturing fsm
        # payload_size = self.get_feature_by_name('PayloadSize').get()
        payload_size = VmbUint32(0)
        try:
            call_vmb_c('VmbPayloadSizeGet', self._handle, byref(payload_size))

        except VmbCError as e:
            raise _build_camera_error(self._parent_cam, self, e) from e
        try:
            buffer_alignment = self.get_feature_by_name('StreamBufferAlignment').get()
        except VmbFeatureError:
            buffer_alignment = 1
        frames = tuple([Frame(payload_size.value,
                              allocation_mode,
                              buffer_alignment=buffer_alignment) for _ in range(buffer_count)])
        callback = build_callback_type(None,
                                       VmbHandle,
                                       VmbHandle,
                                       POINTER(VmbFrame))(self.__frame_cb_wrapper)

        self.__capture_fsm = _CaptureFsm(_Context(self._parent_cam,
                                                  self,
                                                  frames,
                                                  handler,
                                                  callback))

        # Try to enter streaming mode. If this fails perform cleanup and raise error
        exc = self.__capture_fsm.enter_capturing_mode()
        if exc:
            self.__capture_fsm.leave_capturing_mode()
            self.__capture_fsm = None
            raise exc

    @TraceEnable()
    def stop_streaming(self):
        if not self.is_streaming():
            return

        # Leave Capturing mode. If any error occurs, report it and cleanup
        try:
            exc = self.__capture_fsm.leave_capturing_mode()
            if exc:
                raise exc

        finally:
            self.__capture_fsm = None

    @TraceEnable()
    def is_streaming(self) -> bool:
        """Returns True if the camera is currently in streaming mode. If not, returns False."""
        return self.__capture_fsm is not None

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def queue_frame(self, frame: Frame):
        if self.__capture_fsm is None:
            return

        if frame not in self.__capture_fsm.get_context().frames:
            raise ValueError('Given Frame is not from Queue')

        self.__capture_fsm.queue_frame(frame)

    def __frame_cb_wrapper(self,
                           cam_handle: VmbHandle,
                           stream_handle: VmbHandle,
                           raw_frame_ptr: VmbFrame):   # coverage: skip
        # Skip coverage because it can't be measured. This is called from C-Context.
        # ignore callback if camera has been disconnected
        if self.__capture_fsm is None:
            return

        context = self.__capture_fsm.get_context()

        with context.frames_lock:
            raw_frame = raw_frame_ptr.contents
            frame = None

            for f in context.frames:
                # Access Frame internals to compare if both point to the same buffer
                if raw_frame.buffer == _frame_handle_accessor(f).buffer:
                    frame = f
                    break

            # Execute registered handler
            assert frame is not None

            try:
                context.frames_handler(self._parent_cam, self, frame)

            except Exception as e:
                msg = 'Caught Exception in handler: '
                msg += 'Type: {}, '.format(type(e))
                msg += 'Value: {}, '.format(e)
                msg += 'raised by: {}'.format(context.frames_handler)
                Log.get_instance().error(msg)
                raise e


def _frame_handle_accessor(frame: Frame) -> VmbFrame:
    return frame._frame


def _build_camera_error(cam: Camera, stream: Stream, orig_exc: VmbCError) -> VmbCameraError:
    err = orig_exc.get_error_code()

    if err == VmbError.ApiNotStarted:
        msg = 'System not ready. \'{}\' (stream \'{}\') accessed outside of system context. Abort.'
        exc = cast(VmbCameraError, VmbSystemError(msg.format(cam.get_id(), stream)))

    elif err == VmbError.DeviceNotOpen:
        msg = 'Camera \'{}\' (stream \'{}\') accessed outside of context. Abort.'
        exc = VmbCameraError(msg.format(cam.get_id(), stream))

    elif err == VmbError.BadHandle:
        msg = 'Invalid Camera. \'{}\' (stream \'{}\') might be disconnected. Abort.'
        exc = VmbCameraError(msg.format(cam.get_id(), stream))

    elif err == VmbError.InvalidAccess:
        msg = 'Invalid Access Mode on camera \'{}\' (stream \'{}\'). Abort.'
        exc = VmbCameraError(msg.format(cam.get_id(), stream))

    elif err == VmbError.Timeout:
        msg = 'Frame capturing on Camera \'{}\' (stream \'{}\') timed out.'
        exc = cast(VmbCameraError, VmbTimeout(msg.format(cam.get_id(), stream)))

    else:
        exc = VmbCameraError(repr(err))

    return exc
