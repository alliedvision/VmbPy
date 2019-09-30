"""Camera access.

This module allows access to a detected camera.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum
from typing import Tuple, List, Callable, cast, Optional, Type
from .c_binding import call_vimba_c_func, byref, sizeof, decode_cstr, decode_flags
from .c_binding import VmbCameraInfo, VmbHandle, VmbUint32, G_VIMBA_HANDLE, VmbAccessMode, \
                       VimbaCError, VmbError, VmbFrame
from .feature import discover_features, discover_feature, filter_features_by_name, \
                     filter_features_by_type, filter_affected_features, \
                     filter_selected_features, FeatureTypes, FeaturesTuple
from .frame import Frame, FrameTuple
from .util import TraceEnable, RuntimeTypeCheckEnable
from .error import VimbaSystemError, VimbaCameraError, VimbaTimeout


__all__ = [
    'AccessMode',
    'Camera',
    'CameraChangeHandler',
    'CamerasTuple',
    'CamerasList',
    'discover_cameras',
    'discover_camera',
    'FrameHandler'
]


FrameHandler = Callable[[Type['Camera'], Frame], None]


class AccessMode(enum.IntEnum):
    """Enum specifying all available access modes for camera access.

    Enum values:
        None_  - No access
        Full   - Read and write access
        Read   - Read-only access
        Config - Configuration access (GeV)
        Lite   - Read and write access without feature access (only addresses)
    """
    None_ = VmbAccessMode.None_
    Full = VmbAccessMode.Full
    Read = VmbAccessMode.Read
    Config = VmbAccessMode.Config
    Lite = VmbAccessMode.Lite


class _CaptureHelper:
    @TraceEnable()
    def __init__(self, cam):
        self.__cam = cam
        self.__cam_handle = _cam_handle_accessor(self.__cam)

    def build_camera_error(self, orig_exc: VimbaCError):
        exc = cast(VimbaCameraError, orig_exc)
        err = orig_exc.get_error_code()

        if err == VmbError.ApiNotStarted:
            msg = 'System not ready. \'{}\' accessed outside of system context. Abort.'
            exc = cast(VimbaCameraError, VimbaSystemError(msg.format(self.__cam.get_id())))

        elif err == VmbError.DeviceNotOpen:
            msg = 'Camera \'{}\' accessed outside of context. Abort.'
            exc = VimbaCameraError(msg.format(self.__cam.get_id()))

        elif err == VmbError.BadHandle:
            msg = 'Invalid Camera. \'{}\' might be disconnected. Abort.'
            exc = VimbaCameraError(msg.format(self.__cam.get_id()))

        elif err == VmbError.InvalidAccess:
            msg = 'Invalid Access Mode on camera \'{}\'. Abort.'
            exc = VimbaCameraError(msg.format(self.__cam.get_id()))

        elif err == VmbError.Timeout:
            msg = 'Frame capturing on Camera \'{}\' timed out.'
            exc = cast(VimbaCameraError, VimbaTimeout(msg.format(self.__cam.get_id())))

        return exc

    @TraceEnable()
    def capture_start(self):
        exc = None

        try:
            call_vimba_c_func('VmbCaptureStart', self.__cam_handle)

        except VimbaCError as e:
            exc = self.build_camera_error(e)

        if exc:
            raise exc

    @TraceEnable()
    def capture_end(self):
        exc = None

        try:
            call_vimba_c_func('VmbCaptureEnd', self.__cam_handle)

        except VimbaCError as e:
            exc = self.build_camera_error(e)

        if exc:
            raise exc

    @TraceEnable()
    def capture_queue_frames(self, frames: FrameTuple, handler: Optional[FrameHandler]):
        exc = None

        for frame in frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vimba_c_func('VmbCaptureFrameQueue', self.__cam_handle,
                                  byref(frame_handle), handler)

            except VimbaCError as e:
                exc = self.build_camera_error(e)

            if exc:
                raise exc

    @TraceEnable()
    def capture_queue_flush(self):
        exc = None

        try:
            call_vimba_c_func('VmbCaptureQueueFlush', self.__cam_handle)

        except VimbaCError as e:
            exc = self.build_camera_error(e)

        if exc:
            raise exc

    @TraceEnable()
    def capture_frames_wait(self, frames: FrameTuple):
        exc = None

        for frame in frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vimba_c_func('VmbCaptureFrameWait', self.__cam_handle, byref(frame_handle),
                                  self.__cam.get_capture_timeout())

            except VimbaCError as e:
                exc = self.build_camera_error(e)

            if exc:
                raise exc

    @TraceEnable()
    def aquisition_start(self):
        self.__cam.get_feature_by_name('AcquisitionStart').run()

    @TraceEnable()
    def aquisition_stop(self):
        self.__cam.get_feature_by_name('AcquisitionStop').run()

    @TraceEnable()
    def announce_frames(self, frames: FrameTuple):
        exc = None

        for frame in frames:
            frame_handle = _frame_handle_accessor(frame)

            try:
                call_vimba_c_func('VmbFrameAnnounce', self.__cam_handle,
                                  byref(frame_handle), sizeof(frame_handle))

            except VimbaCError as e:
                exc = self.build_camera_error(e)

            if exc:
                raise exc

    @TraceEnable()
    def revoke_frames(self, frames: FrameTuple):
        exc = None

        for frame in frames:
            try:
                frame_handle = _frame_handle_accessor(frame)

                call_vimba_c_func('VmbFrameRevoke', self.__cam_handle,
                                  byref(frame_handle))

            except VimbaCError as e:
                exc = self.build_camera_error(e)

            if exc:
                raise exc

    @TraceEnable()
    def revoke_all_frames(self):
        exc = None

        try:
            call_vimba_c_func('VmbFrameRevokeAll', self.__cam_handle)

        except VimbaCError as e:
            exc = self.build_camera_error(e)

        if exc:
            raise exc


class _FrameIter:
    @TraceEnable()
    def __init__(self, limit: Optional[int], payload_size: int, capture_helper: _CaptureHelper):
        self.__limit: Optional[int] = limit
        self.__payload_size: int = payload_size
        self.__cap_help: _CaptureHelper = capture_helper

    @TraceEnable()
    def __iter__(self):
        return self

    @TraceEnable()
    def __next__(self):
        if self.__limit is not None:
            if self.__limit == 0:
                raise StopIteration

            else:
                self.__limit -= 1

        # Allocate Frame, capture it and return
        frame = Frame(self.__payload_size)
        frames = (frame, )

        self.__cap_help.announce_frames(frames)
        try:
            self.__cap_help.capture_start()
            try:
                self.__cap_help.capture_queue_frames(frames, None)
                try:
                    self.__cap_help.aquisition_start()
                    try:
                        self.__cap_help.capture_frames_wait(frames)
                    finally:
                        self.__cap_help.aquisition_stop()
                finally:
                    self.__cap_help.capture_end()
            finally:
                self.__cap_help.capture_queue_flush()
        finally:
            self.__cap_help.revoke_frames(frames)

        return frame


class Camera:
    """This class allows access a Camera detected by the Vimba System.
    Camera is meant be used in conjunction with the "with" - Statement. On entering a context
    all Camera features are detected and can be accessed within the context.
    Basic Camera properties like Name and Model can be access outside of the context.
    """
    @TraceEnable()
    def __init__(self, info: VmbCameraInfo, access_mode: AccessMode, capture_timeout: int):
        """Do not call directly. Access Cameras via vimba.System instead."""
        self.__handle: VmbHandle = VmbHandle(0)
        self.__info: VmbCameraInfo = info
        self.__access_mode: AccessMode = access_mode
        self.__capture_timeout = capture_timeout

        self.__feats: FeaturesTuple = ()
        self.__context_cnt: int = 0
        self.__frame_buffers: FrameTuple = ()
        self.__frame_handler: Optional[FrameHandler] = None

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

    def __repr__(self):
        rep = 'Camera'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    @RuntimeTypeCheckEnable()
    def set_access_mode(self, access_mode: AccessMode):
        """Set camera access mode.

        Arguments:
            mode - AccessMode used on accessing a Camera. This method
                must be used before entering the Context with the 'with' statement.

        Raises:
           TypeError if 'mode' is not of type AccessMode.
        """
        self.__access_mode = access_mode

    def get_access_mode(self) -> AccessMode:
        """Get current camera access mode"""
        return self.__access_mode

    @RuntimeTypeCheckEnable()
    def set_capture_timeout(self, millis):
        """Set camera frame capture timeout in milliseconds.

        Arguments:
            millis - The new default capture timeout to use.

        Raises:
            TypeError if 'millis' is no integer.
            ValueError if 'millis' is negative
        """
        if millis <= 0:
            raise ValueError('Given Timeout {} must be positive.'.format(millis))

        self.__capture_timeout = millis

    def get_capture_timeout(self) -> int:
        """Get camera frame capture timeout in milliseconds"""
        return self.__capture_timeout

    def get_id(self) -> str:
        """Get Camera Id, e.g. DEV_1AB22C00041B"""
        return decode_cstr(self.__info.cameraIdString)

    def get_name(self) -> str:
        """Get Camera Name, e.g. Allied Vision 1800 U-500m"""
        return decode_cstr(self.__info.cameraName)

    def get_model(self) -> str:
        """Get Camera Model, e.g. 1800 U-500m"""
        return decode_cstr(self.__info.modelName)

    def get_serial(self) -> str:
        """Get Camera Serial, e.g. 000T7"""
        return decode_cstr(self.__info.serialString)

    def get_permitted_access_modes(self) -> Tuple[AccessMode, ...]:
        """Get a set of all access modes, the camera can be accessed with."""
        return decode_flags(AccessMode, self.__info.permittedAccess)

    def get_interface_id(self) -> str:
        """Get ID of the Interface this camera is connected to, e.g. VimbaUSBInterface_0x0"""
        return decode_cstr(self.__info.interfaceIdString)

    def get_all_features(self) -> FeaturesTuple:
        """Get access to all discovered features of this camera:

        Returns:
            A set of all currently detected features. Returns an empty set then called
            outside of 'with' - statement.
        """
        return self.__feats

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features affected by a specific camera feature.

        Arguments:
            feat - Feature used find features that are affected by 'feat'.

        Returns:
            A set of features affected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this camera.
        """
        return filter_affected_features(self.__feats, feat)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features selected by a specific camera feature.

        Arguments:
            feat - Feature used find features that are selected by 'feat'.

        Returns:
            A set of features selected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this camera.
        """
        return filter_selected_features(self.__feats, feat)

    #@RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
        """Get all camera features of a specific feature type.

        Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
        EnumFeature, CommandFeature, RawFeature

        Arguments:
            feat_type - FeatureType used find features of that type.

        Returns:
            A set of features of type 'feat_type'. Can be an empty set if there is
            no camera feature with the given type available.

        Raises:
            TypeError if 'feat_type' is not of any feature Type.
        """
        return filter_features_by_type(self.__feats, feat_type)

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get a camera feature by its name.

        Arguments:
            feat_name - Name used to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError if 'feat_name' is not of type 'str'.
            VimbaFeatureError if no feature is associated with 'feat_name'.
        """
        return filter_features_by_name(self.__feats, feat_name)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_frame_iter(self, limit: Optional[int] = None) -> _FrameIter:
        """Construct frame iterator, providing synchronous camera access.

        The Frame iterator acquires a new frame with each iteration.

        Arguments:
            limit - The number of images the iterator should acquire. If limit is None
                    the iterator will produce an unlimited amount of images and must be
                    stopped by the user supplied code.

        Returns:
            frame_iter object

        Raises:
            ValueError if a limit is supplied and it is not positive.
            VimbaCameraError if the camera is outside of its implemented context.
        """
        if limit and (limit < 0):
            raise ValueError('Given Limit {} is not >= 0'.format(limit))

        if not self.__handle:
            msg = 'Camera \'{}\' not ready for frame acquisition. Open camera via \'with\' .'
            raise VimbaCameraError(msg)

        payload_size = self.get_feature_by_name('PayloadSize').get()
        capture_helper = _CaptureHelper(self)

        return _FrameIter(limit, payload_size, capture_helper)

    @TraceEnable()
    def get_frame(self) -> Frame:
        """Get single frame from camera. Synchronous access.

        Returns:
            Frame from camera

        Raises:
            VimbaCameraError if camera is outside of its context.
        """
        return self.get_frame_iter(1).__next__()

    @TraceEnable()
    #@RuntimeTypeCheckEnable()
    def start_streaming(self, handler: FrameHandler, buffer_count: int = 5):
        raise NotImplementedError('Impl Me')

    @TraceEnable()
    def stop_streaming(self):
        raise NotImplementedError('Impl Me')

    @TraceEnable()
    def requeue_frame(self):
        raise NotImplementedError('Impl Me')

    @TraceEnable()
    def _open(self):
        exc = None

        try:
            call_vimba_c_func('VmbCameraOpen', self.__info.cameraIdString, self.__access_mode,
                              byref(self.__handle))

        except VimbaCError as e:
            exc = cast(VimbaSystemError, e)
            err = e.get_error_code()

            # In theory InvalidAccess should be thrown on using a non permitted access mode.
            # In reality VmbError.NotImplemented_ is returned.
            if err == VmbError.InvalidAccess or err == VmbError.NotImplemented_:
                msg = 'Accessed Camera \'{}\' with invalid Mode \'{}\'. Valid modes are: {}'
                msg = msg.format(self.get_id(), str(self.__access_mode),
                                 self.get_permitted_access_modes())

                exc = VimbaSystemError(msg)

        if exc:
            raise exc

        self.__feats = discover_features(self.__handle)

    @TraceEnable()
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


CameraChangeHandler = Callable[[Camera, bool], None]
CamerasTuple = Tuple[Camera, ...]
CamerasList = List[Camera]


@TraceEnable()
def discover_cameras(access_mode: AccessMode, capture_timeout: int,
                     network_discovery: bool) -> CamerasList:
    """Do not call directly. Access Cameras via vimba.Vimba instead."""

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
            result.append(Camera(info, access_mode, capture_timeout))

    return result


@TraceEnable()
def discover_camera(id_: str, access_mode: AccessMode, capture_timeout: int) -> Camera:
    """Do not call directly. Access Cameras via vimba.Vimba instead."""

    info = VmbCameraInfo()

    call_vimba_c_func('VmbCameraInfoQuery', id_.encode('utf-8'), byref(info), sizeof(info))

    return Camera(info, access_mode, capture_timeout)


def _cam_handle_accessor(cam) -> VmbHandle:
    return cam._Camera__handle


def _frame_handle_accessor(frame) -> VmbFrame:
    return frame._Frame__frame
