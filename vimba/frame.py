"""Frame implementation.

This module contains all functionality regarding Frame and Image data.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum
import ctypes
import copy

from typing import Optional, Tuple
from .c_binding import create_string_buffer, byref, sizeof, decode_flags
from .c_binding import call_vimba_c, VmbFrameStatus, VmbFrameFlags, VmbFrame, VmbHandle, \
                       VmbPixelFormat
from .feature import FeaturesTuple, FeatureTypes, discover_features, filter_features_by_name
from .util import TraceEnable, RuntimeTypeCheckEnable


__all__ = [
    'VimbaPixelFormat',
    'FrameStatus',
    'Frame',
    'FrameTuple'
]


# Forward declarations
FrameTuple = Tuple['Frame', ...]


class VimbaPixelFormat(enum.IntEnum):
    None_ = VmbPixelFormat.None_
    Mono8 = VmbPixelFormat.Mono8
    Mono10 = VmbPixelFormat.Mono10
    Mono10p = VmbPixelFormat.Mono10p
    Mono12 = VmbPixelFormat.Mono12
    Mono12Packed = VmbPixelFormat.Mono12Packed
    Mono12p = VmbPixelFormat.Mono12p
    Mono14 = VmbPixelFormat.Mono14
    Mono16 = VmbPixelFormat.Mono16
    BayerGR8 = VmbPixelFormat.BayerGR8
    BayerRG8 = VmbPixelFormat.BayerRG8
    BayerGB8 = VmbPixelFormat.BayerGB8
    BayerBG8 = VmbPixelFormat.BayerBG8
    BayerGR10 = VmbPixelFormat.BayerGR10
    BayerRG10 = VmbPixelFormat.BayerRG10
    BayerGB10 = VmbPixelFormat.BayerGB10
    BayerBG10 = VmbPixelFormat.BayerBG10
    BayerGR12 = VmbPixelFormat.BayerGR12
    BayerRG12 = VmbPixelFormat.BayerRG12
    BayerGB12 = VmbPixelFormat.BayerGB12
    BayerBG12 = VmbPixelFormat.BayerBG12
    BayerGR12Packed = VmbPixelFormat.BayerGR12Packed
    BayerRG12Packed = VmbPixelFormat.BayerRG12Packed
    BayerGB12Packed = VmbPixelFormat.BayerGB12Packed
    BayerBG12Packed = VmbPixelFormat.BayerBG12Packed
    BayerGR10p = VmbPixelFormat.BayerGR10p
    BayerRG10p = VmbPixelFormat.BayerRG10p
    BayerGB10p = VmbPixelFormat.BayerGB10p
    BayerBG10p = VmbPixelFormat.BayerBG10p
    BayerGR12p = VmbPixelFormat.BayerGR12p
    BayerRG12p = VmbPixelFormat.BayerRG12p
    BayerGB12p = VmbPixelFormat.BayerGB12p
    BayerBG12p = VmbPixelFormat.BayerBG12p
    BayerGR16 = VmbPixelFormat.BayerGR16
    BayerRG16 = VmbPixelFormat.BayerRG16
    BayerGB16 = VmbPixelFormat.BayerGB16
    BayerBG16 = VmbPixelFormat.BayerBG16
    Rgb8 = VmbPixelFormat.Rgb8
    Bgr8 = VmbPixelFormat.Bgr8
    Rgb10 = VmbPixelFormat.Rgb10
    Bgr10 = VmbPixelFormat.Bgr10
    Rgb12 = VmbPixelFormat.Rgb12
    Bgr12 = VmbPixelFormat.Bgr12
    Rgb14 = VmbPixelFormat.Rgb14
    Bgr14 = VmbPixelFormat.Bgr14
    Rgb16 = VmbPixelFormat.Rgb16
    Bgr16 = VmbPixelFormat.Bgr16
    Argb8 = VmbPixelFormat.Argb8
    Rgba8 = VmbPixelFormat.Rgba8
    Bgra8 = VmbPixelFormat.Bgra8
    Rgba10 = VmbPixelFormat.Rgba10
    Bgra10 = VmbPixelFormat.Bgra10
    Rgba12 = VmbPixelFormat.Rgba12
    Bgra12 = VmbPixelFormat.Bgra12
    Rgba14 = VmbPixelFormat.Rgba14
    Bgra14 = VmbPixelFormat.Bgra14
    Rgba16 = VmbPixelFormat.Rgba16
    Bgra16 = VmbPixelFormat.Bgra16
    Yuv411 = VmbPixelFormat.Yuv411
    Yuv422 = VmbPixelFormat.Yuv422
    Yuv444 = VmbPixelFormat.Yuv444
    YCbCr411_8_CbYYCrYY = VmbPixelFormat.YCbCr411_8_CbYYCrYY
    YCbCr422_8_CbYCrY = VmbPixelFormat.YCbCr422_8_CbYCrY
    YCbCr8_CbYCr = VmbPixelFormat.YCbCr8_CbYCr


class FrameStatus(enum.IntEnum):
    Complete = VmbFrameStatus.Complete
    Incomplete = VmbFrameStatus.Incomplete
    TooSmall = VmbFrameStatus.TooSmall
    Invalid = VmbFrameStatus.Invalid


# TODO: Ancillary Data are basically Features where most functions are not available.
#       Some kind of protection against undefined behavior might be in order here.
class AncillaryData:
    """TODO: Document me """
    @TraceEnable()
    def __init__(self, handle: VmbFrame):
        """Do not call directly. Get Object via Frame access method"""
        self.__handle: VmbFrame = handle
        self.__data_handle: VmbHandle = VmbHandle()
        self.__feats: FeaturesTuple = ()
        self.__context_cnt = 0

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

    def get_all_features(self) -> FeaturesTuple:
        return self.__feats

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        return filter_features_by_name(self.__feats, feat_name)

    @TraceEnable()
    def _open(self):
        call_vimba_c('VmbAncillaryDataOpen', byref(self.__handle), byref(self.__data_handle))

        self.__feats = discover_features(self.__data_handle)

    @TraceEnable()
    def _close(self):
        call_vimba_c('VmbAncillaryDataClose', self.__data_handle)

        self.__data_handle = VmbHandle()
        self.__feats = ()


class Frame:
    """This class allows access a Frames acquired by a Camera. The Frame is basically
    a buffer containing image data and some metadata.
    """
    def __init__(self, buffer_size: int):
        """Do not call directly. Create Frame via Camera methods instead."""
        self._buffer = create_string_buffer(buffer_size)
        self._frame: VmbFrame = VmbFrame()

        # Setup underlaying Frame
        self._frame.buffer = ctypes.cast(self._buffer, ctypes.c_void_p)
        self._frame.bufferSize = sizeof(self._buffer)

    def __str__(self):
        return 'Frame(id={}, buffer={})'.format(self._frame.frameID, hex(self._frame.buffer))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # VmbFrame contains Pointers and ctypes.Structure with Pointers can't be copied.
        # As a workaround VmbFrame contains a deepcopy-like Method performing deep copy of all
        # Attributes except PointerTypes. Those must be set manually after the copy operation.
        setattr(result, '_buffer', copy.deepcopy(self._buffer, memo))
        setattr(result, '_frame', self._frame.deepcopy_skip_ptr(memo))

        result._frame.buffer = ctypes.cast(result._buffer, ctypes.c_void_p)
        result._frame.bufferSize = sizeof(result._buffer)

        return result

    def get_buffer(self) -> ctypes.Array:
        """Get internal buffer object containing image data."""
        return self._buffer

    def get_buffer_size(self) -> int:
        """Get byte size of internal buffer."""
        return sizeof(self._buffer)

    def get_image_size(self) -> int:
        """Get byte size of image data stored in buffer."""
        return self._frame.imageSize

    def get_ancillary_data(self) -> Optional[AncillaryData]:
        """Get AncillaryData.

        Frames acquired with Cameras where Feature ChunkModeActive is enabled, can contain
        Ancillary Data within the image data.

        Returns:
            None if Frame contains no ancillary data.
            AncillaryData if Frame contains ancillary data.
        """
        if not self._frame.ancillarySize:
            return None

        return AncillaryData(self._frame)

    def get_status(self) -> FrameStatus:
        """Returns current frame status."""
        return FrameStatus(self._frame.receiveStatus)

    def get_pixel_format(self) -> VimbaPixelFormat:
        """Get format of the acquired image data """
        return VimbaPixelFormat(self._frame.pixelFormat)

    def get_height(self) -> Optional[int]:
        """Get image height in pixel.

        Returns:
            Image height in pixel if dimension data is provided by the camera.
            None if dimension data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Dimension not in flags:
            return None

        return self._frame.height

    def get_width(self) -> Optional[int]:
        """Get image width in pixel.

        Returns:
            Image width in pixel if dimension data is provided by the camera.
            None if dimension data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Dimension not in flags:
            return None

        return self._frame.width

    def get_offset_x(self) -> Optional[int]:
        """Get horizontal offset in pixel.

        Returns:
            Horizontal offset in pixel if offset data is provided by the camera.
            None if offset data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Offset not in flags:
            return None

        return self._frame.offsetX

    def get_offset_y(self) -> Optional[int]:
        """Get vertical offset in pixel.

        Returns:
            Vertical offset in pixel if offset data is provided by the camera.
            None if offset data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Offset not in flags:
            return None

        return self._frame.offsetY

    def get_id(self) -> Optional[int]:
        """Get Frame ID.

        Returns:
            Frame ID if the id is provided by the camera.
            None if frame id is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.FrameID not in flags:
            return None

        return self._frame.frameID

    def get_timestamp(self) -> Optional[int]:
        """Get Frame timestamp.

        Returns:
            Timestamp if provided by the camera.
            None if timestamp is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Timestamp not in flags:
            return None

        return self._frame.timestamp

    def convert_pixel_format(self, format: VimbaPixelFormat):
        """TODO: Implement me"""
        raise NotImplementedError('TODO: Implement me')

    def store(self, filename: str, directory: Optional[str] = None):
        """TODO: Implement me"""
        raise NotImplementedError('TODO: Implement me')

    def create_opencv_frame(self):
        """TODO: Implement me"""
        raise NotImplementedError('TODO: Implement me')