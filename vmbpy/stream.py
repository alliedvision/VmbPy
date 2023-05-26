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
import copy
import threading
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, cast

from .c_binding import (AccessMode, VmbCError, VmbError, VmbFrame, VmbHandle, VmbUint32, byref,
                        call_vmb_c, sizeof)
from .c_binding.vmb_c import FRAME_CALLBACK_TYPE
from .error import VmbCameraError, VmbFeatureError, VmbSystemError, VmbTimeout
from .featurecontainer import PersistableFeatureContainer
from .frame import AllocationMode, Frame
from .shared import filter_features_by_name
from .util import (EnterContextOnCall, LeaveContextOnCall, Log, RaiseIfOutsideContext,
                   RuntimeTypeCheckEnable, TraceEnable)

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


class _StateAnnounced(_State):
    @TraceEnable()
    def enter(self):
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)
            try:
                call_vmb_c('VmbFrameAnnounce', self.context.stream_handle, byref(frame_handle),
                           sizeof(frame_handle))
                if frame._allocation_mode == AllocationMode.AllocAndAnnounceFrame:
                    assert frame_handle.buffer is not None
                    frame._set_buffer(frame_handle.buffer)
            except VmbCError as e:
                raise _build_camera_error(self.context.cam, self.context.stream, e) from e

    @TraceEnable()
    def exit(self):
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)
            try:
                call_vmb_c('VmbFrameRevoke', self.context.stream_handle, byref(frame_handle))
            except VmbCError as e:
                raise _build_camera_error(self.context.cam, self.context.stream, e) from e


class _StateQueued(_State):
    @TraceEnable()
    def enter(self):
        for frame in self.context.frames:
            frame_handle = _frame_handle_accessor(frame)
            try:
                call_vmb_c('VmbCaptureFrameQueue', self.context.stream_handle, byref(frame_handle),
                           self.context.frames_callback)
            except VmbCError as e:
                raise _build_camera_error(self.context.cam, self.context.stream, e) from e

    @TraceEnable()
    def exit(self):
        try:
            call_vmb_c('VmbCaptureQueueFlush', self.context.stream_handle)
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e


class _StateCaptureStarted(_State):
    @TraceEnable()
    def enter(self):
        try:
            call_vmb_c('VmbCaptureStart', self.context.stream_handle)
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e

    @TraceEnable()
    def exit(self):
        try:
            call_vmb_c('VmbCaptureEnd', self.context.stream_handle)
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e


class _StateAcquiring(_State):
    @TraceEnable()
    def enter(self):
        try:
            if not self.context.cam._disconnected:
                # Skip Command execution on AccessMode.Read (required for Multicast Streaming)
                if self.context.cam.get_access_mode() != AccessMode.Read:
                    self.context.cam.get_feature_by_name('AcquisitionStart').run()
            else:
                raise VmbCameraError('Camera \'{}\' is not accessible to start the acquisition'
                                     ''.format(self.context.cam))
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e
        except BaseException as e:
            raise VmbCError(str(e))

    @TraceEnable()
    def exit(self):
        try:
            # Skip Command execution if camera went missing from VmbSystem (i.e. camera connection
            # got lost)
            if not self.context.cam._disconnected:
                # Skip Command execution on AccessMode.Read (required for Multicast Streaming)
                if self.context.cam.get_access_mode() != AccessMode.Read:
                    self.context.cam.get_feature_by_name('AcquisitionStop').run()
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e
        except BaseException as e:
            raise VmbCError(str(e))

    @TraceEnable()
    def wait_for_frame(self, timeout_ms: int, frame: Frame):
        frame_handle = _frame_handle_accessor(frame)
        try:
            call_vmb_c('VmbCaptureFrameWait', self.context.stream_handle, byref(frame_handle),
                       timeout_ms)
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e

    @TraceEnable()
    def queue_frame(self, frame: Frame):
        frame_handle = _frame_handle_accessor(frame)
        try:
            call_vmb_c('VmbCaptureFrameQueue', self.context.stream_handle, byref(frame_handle),
                       self.context.frames_callback)
        except VmbCError as e:
            raise _build_camera_error(self.context.cam, self.context.stream, e) from e


class _CaptureFsm:
    STATE_ORDER = (_StateAnnounced, _StateQueued, _StateCaptureStarted, _StateAcquiring)

    def __init__(self, context: _Context):
        self.__context = context
        # self.__states holds each entered states in the order they were entered. The "current"
        # state is always the last one in the array
        self.__states: List[_State] = []

    def get_context(self) -> _Context:
        return self.__context

    def go_to_state(self, new_state: Optional[type[_State]]):
        """
        Make the state machine transition to new_state.

        If an error occurs during the transition, it is raised after the transition is completed.
        See section "Raises" of this docstring for a short explanation.

        Arguments:
            new_state:
                The state that the state machine should transition to or None. If a state is given,
                all necessary transitions are attempted. If None is given, all currently entered
                states will be exited.

        Raises:
            Any errors encountered during the state transition are cached. If only one error was
            encountered, that error is raised after the target state has been reached. If multiple
            errors are encountered during the transition, they are bundled in an array and raised at
            the end of the transition as part of a VmbCameraError.
        """
        if new_state is not None:
            target_index = _CaptureFsm.STATE_ORDER.index(new_state)
        else:
            target_index = -1
        exc = []
        while self.__current_index != target_index:
            try:
                if self.__current_index < target_index:
                    # Get the next state we should transition to, add it to the end of the
                    # self.__states array and enter that new state
                    self.__states.append(
                        _CaptureFsm.STATE_ORDER[self.__current_index + 1](self.__context))
                    self.__states[-1].enter()  # type: ignore
                else:
                    # Take the last state from the self.__states array and exit it
                    self.__states.pop().exit()  # type: ignore
            except VmbCError as e:
                # If an exception is encountered during any state enter or exit, we collect it until
                # all requested transitions were attempted
                exc.append(e)
        # if exceptions have been collected, assemble them back to an exception and raise that
        if exc:
            if len(exc) == 1:
                # Only one exception was encountered. Raise that one directly
                raise exc.pop()
            else:
                raise VmbCameraError('Encountered multiple VmbC Errors during state transition: '
                                     f'{exc}')

    @property
    def __current_index(self) -> int:
        # Returns the index of the "current" state of the state machine in _CaptureFsm.STATE_ORDER.
        # The "current" state is always the last one that was entered
        return len(self.__states) - 1

    def enter_capturing_mode(self):
        # Forward state machine until the end
        self.go_to_state(_CaptureFsm.STATE_ORDER[-1])

    def leave_capturing_mode(self):
        # Revert state machine until the initial state is reached
        self.go_to_state(None)

    def wait_for_frame(self, timeout_ms: int, frame: Frame):
        # Wait for Frames only in AcquiringMode
        if isinstance(self.__states[-1], _StateAcquiring):
            self.__states[-1].wait_for_frame(timeout_ms, frame)

    def queue_frame(self, frame: Frame):
        # Queue Frame only in AcquiringMode
        if isinstance(self.__states[-1], _StateAcquiring):
            self.__states[-1].queue_frame(frame)


@TraceEnable()
def _frame_generator(cam: Camera,
                     stream: Stream,
                     limit: Optional[int],
                     timeout_ms: int,
                     allocation_mode: AllocationMode):
    if stream.is_streaming():
        raise VmbCameraError('Operation not supported while streaming.')

    buffer_alignment_feature = filter_features_by_name(stream.get_all_features(),
                                                       'StreamBufferAlignment')
    if buffer_alignment_feature:
        buffer_alignment = buffer_alignment_feature.get()
    else:
        buffer_alignment = 1

    frame_data_size = VmbUint32(0)
    try:
        call_vmb_c('VmbPayloadSizeGet', stream._handle, byref(frame_data_size))
    except VmbCError as e:
        raise _build_camera_error(cam, stream, e) from e

    # Some streams require a minimum number of announced frame buffers to work. VmbPy will announce
    # multiple frames but only used the frame at index 0 for actual data transmission for
    # synchronous acquisition
    buffer_count = 1
    buffer_minimum_feature = filter_features_by_name(stream.get_all_features(),
                                                     'StreamAnnounceBufferMinimum')
    if buffer_minimum_feature:
        buffer_minimum = buffer_minimum_feature.get()
        if not buffer_count >= buffer_minimum:
            msg = '`StreamAnnounceBufferMinimum` indicates at least {} buffers are needed. ' \
                  'Overriding previous number of frames (was {})'
            Log.get_instance().info(msg.format(buffer_minimum, buffer_count))
            buffer_count = buffer_minimum

    frames = tuple([Frame(frame_data_size.value,
                          allocation_mode,
                          buffer_alignment=buffer_alignment) for _ in range(buffer_count)])
    frame = frames[0]
    # FRAME_CALLBACK_TYPE() is equivalent to passing None (i.e. nullptr), but allows ctypes to still
    # perform type checking
    fsm = _CaptureFsm(_Context(cam, stream, frames, None, FRAME_CALLBACK_TYPE()))
    cnt = 0

    try:
        while True if limit is None else cnt < limit:
            fsm.enter_capturing_mode()
            exc = None
            fsm.wait_for_frame(timeout_ms, frame)
            # If an error is encountered while we stop the camera, store it for later. The frame is
            # still yielded to the user and only once they are done with it is the exception raised.
            try:
                fsm.go_to_state(_StateAnnounced)
            except (VmbCError, VmbCameraError) as e:
                exc = e

            # Because acquisition is started fresh for each frame the frameID needs to be set
            # manually
            frame._frame.frameID = cnt
            cnt += 1

            yield frame
            if exc:
                # If we caught an exception in the previous state transition, raise it now that the
                # user is done with the frame
                raise exc

    finally:
        # Leave Capturing mode
        fsm.leave_capturing_mode()


class Stream(PersistableFeatureContainer):
    """This class provides access to a Stream of a Camera"""
    __msg = 'Called \'{}()\' outside of Cameras \'with\' context.'

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
    @EnterContextOnCall()
    def open(self):
        if not self.__is_open:
            self._attach_feature_accessors()
            self.__is_open = True

        # Determine current PacketSize (GigE - only) is somewhere between 1500 bytes
        feat = filter_features_by_name(self._feats, 'GVSPPacketSize')
        if feat:
            try:
                min_ = 1400
                max_ = 1600
                size = feat.get()

                if (min_ < size) and (size < max_):
                    msg = ('Camera {}: GVSPPacketSize not optimized for streaming GigE Vision. '
                           'Enable jumbo packets for improved performance.')
                    Log.get_instance().info(msg.format(self._parent_cam.get_id()))

            except VmbFeatureError:
                pass

    @TraceEnable()
    @LeaveContextOnCall()
    def close(self):
        if self.__is_open:
            self._remove_feature_accessors()
            self.__is_open = False

    @TraceEnable()
    @RaiseIfOutsideContext(msg=__msg)
    @RuntimeTypeCheckEnable()
    def get_frame_generator(self,
                            limit: Optional[int] = None,
                            timeout_ms: int = 2000,
                            allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """See :func:`vmbpy.Camera.get_frame_generator`"""
        if limit is not None and (limit <= 0):
            raise ValueError('Given Limit {} is not > 0'.format(limit))

        if timeout_ms <= 0:
            raise ValueError('Given Timeout {} is not > 0'.format(timeout_ms))

        return _frame_generator(self._parent_cam, self, limit, timeout_ms, allocation_mode)

    @RaiseIfOutsideContext()
    @TraceEnable()
    @RuntimeTypeCheckEnable()
    @contextlib.contextmanager
    def get_frame_with_context(self,
                               timeout_ms: int = 2000,
                               allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """See :func:`vmbpy.Camera.get_frame_with_context`"""
        for frame in self.get_frame_generator(1,
                                              timeout_ms=timeout_ms,
                                              allocation_mode=allocation_mode):
            yield frame

    @TraceEnable()
    @RaiseIfOutsideContext(msg=__msg)
    @RuntimeTypeCheckEnable()
    def get_frame(self,
                  timeout_ms: int = 2000,
                  allocation_mode: AllocationMode = AllocationMode.AnnounceFrame) -> Frame:
        """See :func:`vmbpy.Camera.get_frame`"""
        for frame in self.get_frame_generator(1,
                                              timeout_ms=timeout_ms,
                                              allocation_mode=allocation_mode):
            frame_copy = copy.deepcopy(frame)
        return frame_copy

    @TraceEnable()
    @RaiseIfOutsideContext(msg=__msg)
    @RuntimeTypeCheckEnable()
    def start_streaming(self,
                        handler: FrameHandler,
                        buffer_count: int = 5,
                        allocation_mode: AllocationMode = AllocationMode.AnnounceFrame):
        """See :func:`vmbpy.Camera.start_streaming`"""
        if buffer_count <= 0:
            raise ValueError('Given buffer_count {} must be positive'.format(buffer_count))

        if self.is_streaming():
            raise VmbCameraError('Stream \'{}\' of camera \'{}\'already streaming.'
                                 ''.format(self, self._parent_cam.get_id()))

        # Setup capturing fsm
        buffer_alignment_feature = filter_features_by_name(self.get_all_features(),
                                                           'StreamBufferAlignment')
        if buffer_alignment_feature:
            buffer_alignment = buffer_alignment_feature.get()
        else:
            buffer_alignment = 1

        payload_size = VmbUint32(0)
        try:
            call_vmb_c('VmbPayloadSizeGet', self._handle, byref(payload_size))

        except VmbCError as e:
            raise _build_camera_error(self._parent_cam, self, e) from e

        buffer_minimum_feature = filter_features_by_name(self.get_all_features(),
                                                         'StreamAnnounceBufferMinimum')
        if buffer_minimum_feature:
            buffer_minimum = buffer_minimum_feature.get()
            if not buffer_count >= buffer_minimum:
                msg = '`StreamAnnounceBufferMinimum` indicates at least {} buffers are needed. ' \
                      'Overriding user supplied value (was {})'
                Log.get_instance().info(msg.format(buffer_minimum, buffer_count))
                buffer_count = buffer_minimum

        frames = tuple([Frame(payload_size.value,
                              allocation_mode,
                              buffer_alignment=buffer_alignment) for _ in range(buffer_count)])
        callback = FRAME_CALLBACK_TYPE(self.__frame_cb_wrapper)

        self.__capture_fsm = _CaptureFsm(_Context(self._parent_cam,
                                                  self,
                                                  frames,
                                                  handler,
                                                  callback))

        # Try to enter streaming mode. If this fails perform cleanup and raise error
        try:
            self.__capture_fsm.enter_capturing_mode()
        except BaseException:
            self.__capture_fsm.leave_capturing_mode()
            raise

    @TraceEnable()
    @RaiseIfOutsideContext(msg=__msg)
    def stop_streaming(self):
        """See :func:`vmbpy.Camera.stop_streaming`"""
        if not self.is_streaming():
            return

        # Leave Capturing mode. If any error occurs, report it and cleanup
        try:
            self.__capture_fsm.leave_capturing_mode()

        finally:
            self.__capture_fsm = None

    @TraceEnable()
    def is_streaming(self) -> bool:
        """Returns ``True`` if the camera is currently in streaming mode. If not, returns ``False``.
        """
        return self.__capture_fsm is not None and not self._parent_cam._disconnected

    @TraceEnable()
    @RaiseIfOutsideContext(msg=__msg)
    @RuntimeTypeCheckEnable()
    def queue_frame(self, frame: Frame):
        """See :func:`vmbpy.Camera.queue_frame`"""
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

    get_all_features = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_all_features)                  # noqa: E501
    get_features_selected_by = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_selected_by)  # noqa: E501
    get_features_by_type = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_by_type)          # noqa: E501
    get_features_by_category = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_by_category)  # noqa: E501
    get_feature_by_name = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_feature_by_name)            # noqa: E501
    load_settings = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.load_settings)
    save_settings = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.save_settings)


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
