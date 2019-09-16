# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import enum

from vimba.c_binding import VmbAccessMode


__all__ = [
    'AccessMode'
]


class AccessMode(enum.IntEnum):
    None_ = VmbAccessMode.None_
    Full = VmbAccessMode.Full
    Read = VmbAccessMode.Read
    Config = VmbAccessMode.Config
    Lite = VmbAccessMode.Lite
