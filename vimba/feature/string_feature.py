"""StringFeature implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

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
    """The StringFeature is a feature, that is represented by a string."""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def get(self) -> str:
        """Get current value (str)

        Returns:
            Current str value.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
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
        """Set current value of type str.

        Arguments:
            val - The str value to set.

        Raises:
            TypeError if argument 'val' is not of type 'str'.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if val exceeds the maximum string length.
            VimbaFeatureError if executed within a registered change_handler.
        """
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
        """Get maximum string length the Feature can store.

        In this context, string length does not mean the number of character, it means
        the number of bytes after encoding. A string encoded in UTF-8 could exceed,
        the max length.

        Returns:
            Return the number of ASCII characters, the Feature can store.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
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
