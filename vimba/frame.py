"""Frame implementation.

This module contains all functionality regarding Frame and Image data.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum
import ctypes

from typing import Type, Optional, Tuple
from .c_binding import create_string_buffer, sizeof, decode_flags
from .c_binding import VmbFrameStatus, VmbFrameFlags, VmbFrame

__all__ = [
    'PixelFormat',
    'FrameStatus',
    'Frame',
    'FrameTuple'
]


FrameType = Type['Frame']


class PixelFormat(enum.IntEnum):
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
        self.__buffer = create_string_buffer(buffer_size)
        self.__frame: VmbFrame = VmbFrame()

        self.__frame.buffer = ctypes.cast(self.__buffer, ctypes.c_void_p)
        self.__frame.bufferSize = sizeof(self.__buffer)

    def __deepcopy__(self) -> FrameType:
        raise NotImplementedError('Impl Me')

    def get_buffer(self) -> ctypes.Array:
        return self.__buffer

    def get_buffer_size(self) -> int:
        return sizeof(self.__buffer)

    def get_image_size(self) -> int:
        return self.__frame.imageSize

    def get_ancillary_data(self) -> bytes:
        raise NotImplementedError('Impl Me')

    def get_status(self) -> FrameStatus:
        return FrameStatus(self.__frame.receiveStatus)

    def get_pixel_format(self) -> PixelFormat:
        raise NotImplementedError('Impl Me')

    def get_width(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def get_height(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def get_offset_x(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def get_offset_y(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def get_id(self) -> Optional[int]:
        flags = decode_flags(VmbFrameFlags, self.__frame.receiveFlags)
        return self.__frame.frameID if VmbFrameFlags.FrameID in flags else None

    def get_timestamp(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def convert_pixel_format(self, format: PixelFormat):
        raise NotImplementedError('Impl Me')

    def store(self, filename: str, directory: Optional[str] = None) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def create_opencv_frame(self):
        raise NotImplementedError('Impl Me')


FrameTuple = Tuple[Frame, ...]
