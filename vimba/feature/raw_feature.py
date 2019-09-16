# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)

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
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def get(self) -> bytes:
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
