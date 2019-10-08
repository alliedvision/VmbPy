"""Frame implementation.

This module contains all functionality regarding Frame and Image data.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum
import ctypes
import copy

from typing import Optional, Tuple
from .c_binding import create_string_buffer, sizeof, decode_flags
from .c_binding import VmbFrameStatus, VmbFrameFlags, VmbFrame

__all__ = [
    'VimbaPixelFormat',
    'FrameStatus',
    'Frame',
    'FrameTuple'
]


# Forward declarations
FrameTuple = Tuple['Frame', ...]


class VimbaPixelFormat(enum.IntEnum):
    pass


class FrameStatus(enum.IntEnum):
    Complete = VmbFrameStatus.Complete
    Incomplete = VmbFrameStatus.Incomplete
    TooSmall = VmbFrameStatus.TooSmall
    Invalid = VmbFrameStatus.Invalid


class Frame:
    """Implement me"""

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

    def get_ancillary_data(self) -> bytes:
        """TODO: DOCUMENT ME """
        raise NotImplementedError('Impl Me')

    def get_status(self) -> FrameStatus:
        """Returns current frame status."""
        return FrameStatus(self._frame.receiveStatus)

    def get_pixel_format(self) -> VimbaPixelFormat:
        """TODO: DOCUMENT ME """
        raise NotImplementedError('Impl Me')

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
        """Convert internal pixel format to given format."""
        raise NotImplementedError('Impl Me')

    def store(self, filename: str, directory: Optional[str] = None):
        """TODO
        """
        raise NotImplementedError('Impl Me')

    def create_opencv_frame(self):
        """ Constructs Open CV Frame from Vimba Frame.
        TODO:
        """
        raise NotImplementedError('Impl Me')
