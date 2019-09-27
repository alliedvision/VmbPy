"""Frame implementation.

This module contains all functionality regarding Frame and Image data.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum

from typing import Type, Optional, Tuple
from .c_binding import VmbFrameStatus

__all__ = [
    'PixelFormat',
    'FrameStatus',
    'Frame',
    'FrameTuple'
]


class PixelFormat(enum.IntEnum):
    pass


class FrameStatus(enum.IntEnum):
    Complete = VmbFrameStatus.Complete
    Incomplete = VmbFrameStatus.Incomplete
    TooSmall = VmbFrameStatus.TooSmall
    Invalid = VmbFrameStatus.Invalid


class Frame:
    def __init__(self, buffer_size: int):
        pass

    def __deepcopy__(self) -> Type['Frame']:
        raise NotImplementedError('Impl Me')

    def get_buffer(self) -> bytes:
        raise NotImplementedError('Impl Me')

    def get_ancillary_data(self) -> bytes:
        raise NotImplementedError('Impl Me')

    def get_status(self) -> FrameStatus:
        raise NotImplementedError('Impl Me')

    def get_size(self) -> bytes:
        raise NotImplementedError('Impl Me')

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

    def get_frame_id(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def get_timestamp(self) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def convert_pixel_format(self, format: PixelFormat):
        raise NotImplementedError('Impl Me')

    def store(self, filename: str, directory: Optional[str] = None) -> Optional[int]:
        raise NotImplementedError('Impl Me')

    def create_opencv_frame(self):
        raise NotImplementedError('Impl Me')

FrameTuple = Tuple[Frame, ...]
