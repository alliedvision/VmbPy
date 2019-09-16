# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import inspect
from typing import cast
from vimba.c_binding import call_vimba_c_func, byref, create_string_buffer
from vimba.c_binding import VmbHandle, VmbUint32, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError

__all__ = [
    'StringFeature'
]


class StringFeature(BaseFeature):
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def get(self) -> str:
        exc = None
        c_buf_len = VmbUint32(0)

        # Query buffer length
        try:
            call_vimba_c_func('VmbFeatureStringGet', self._handle, self._info.name, None, 0,
                              byref(c_buf_len))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        c_buf = create_string_buffer(c_buf_len.value)

        # Copy string from C-Layer
        try:
            call_vimba_c_func('VmbFeatureStringGet', self._handle, self._info.name, c_buf,
                              c_buf_len, None)

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_buf.value.decode()

    @RuntimeTypeCheckEnable()
    def set(self, val: str):
        exc = None

        try:
            call_vimba_c_func('VmbFeatureStringSet', self._handle, self._info.name,
                              val.encode('utf8'))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self.__build_value_error(val)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

        if exc:
            raise exc

    def get_max_length(self) -> int:
        exc = None
        c_max_len = VmbUint32(0)

        try:
            call_vimba_c_func('VmbFeatureStringMaxlengthQuery', self._handle, self._info.name,
                              byref(c_max_len))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_max_len.value

    def __build_value_error(self, val: str) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        val_as_bytes = val.encode('utf8')
        max_len = self.get_max_length()

        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. \'{}\' > max length \'{}\'.'

        return VimbaFeatureError(msg.format(caller_name, self.get_name(), val_as_bytes, max_len))
