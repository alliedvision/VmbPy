"""IntFeature implementation

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import inspect

from typing import Tuple, cast
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbHandle, VmbInt64, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError

__all__ = [
    'IntFeature'
]


class IntFeature(BaseFeature):
    """The IntFeature is a feature, that is represented by a integer."""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def get(self) -> int:
        """Get current value (int)

        Returns:
            Current int value.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_val = VmbInt64()

        try:
            call_vimba_c_func('VmbFeatureIntGet', self._handle, self._info.name, byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value

    def get_range(self) -> Tuple[int, int]:
        """Get range of accepted values

        Returns:
            A pair of range boundaries. First value is the minimum second value is the maximum.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_min = VmbInt64()
        c_max = VmbInt64()

        try:
            call_vimba_c_func('VmbFeatureIntRangeQuery', self._handle, self._info.name,
                              byref(c_min), byref(c_max))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return (c_min.value, c_max.value)

    def get_increment(self) -> int:
        """Get increment (steps between valid values, starting from minimal values).

        Returns:
            The increment of this feature.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_val = VmbInt64()

        try:
            call_vimba_c_func('VmbFeatureIntIncrementQuery', self._handle, self._info.name,
                              byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value

    @RuntimeTypeCheckEnable()
    def set(self, val: int):
        """Set current value of type int.

        Arguments:
            val - The int value to set.

        Raises:
            TypeError if argument 'val' is not of type 'int'.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if value is out of bounds or misaligned with regards the increment.
            VimbaFeatureError if executed within a registered change_handler.
        """
        exc = None

        try:
            call_vimba_c_func('VmbFeatureIntSet', self._handle, self._info.name, val)

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self._build_value_error(val)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

        if exc:
            raise exc

    def _build_value_error(self, val) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        min_, max_ = self.get_range()

        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. '

        # Value out of bounds
        if (val < min_) or (max_ < val):
            msg += '{} is not within [{}, {}].'.format(val, min_, max_)

        # Misaligned value
        else:
            inc = self.get_increment()
            msg += '{} is not a multiple of {}, starting at {}'.format(val, inc, min_)

        return VimbaFeatureError(msg.format(caller_name, self.get_name()))
