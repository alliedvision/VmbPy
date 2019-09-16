"""RawFeature implementation

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from typing import cast
from vimba.c_binding import call_vimba_c_func, byref, create_string_buffer
from vimba.c_binding import VmbHandle, VmbUint32, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError

__all__ = [
    'RawFeature'
]


class RawFeature(BaseFeature):
    """The RawFeature is a feature, that is represented by sequence of bytes."""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def get(self) -> bytes:
        """Get current value as a sequence of bytes

        Returns:
            Current value.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """

        exc = None
        c_buf_avail = VmbUint32()
        c_buf_len = self.length()
        c_buf = create_string_buffer(c_buf_len)

        try:
            call_vimba_c_func('VmbFeatureRawGet', self._handle, self._info.name, c_buf, c_buf_len,
                              byref(c_buf_avail))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_buf.raw[:c_buf_avail.value]

    @RuntimeTypeCheckEnable()
    def set(self, buf: bytes):
        """Set current value as a sequence of bytes.

        Arguments:
            val - The value to set.

        Raises:
            TypeError if argument 'val' is not of type 'bytes'.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if executed within a registered change_handler.
        """
        exc = None

        try:
            call_vimba_c_func('VmbFeatureRawSet', self._handle, self._info.name, buf, len(buf))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

        if exc:
            raise exc

    def length(self) -> int:
        """Get length of byte sequence representing the value.

        Returns:
            Length of current value.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_val = VmbUint32()

        try:
            call_vimba_c_func('VmbFeatureRawLengthQuery', self._handle, self._info.name,
                              byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value
