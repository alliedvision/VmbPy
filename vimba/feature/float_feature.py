"""Float feature implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import inspect

from typing import Tuple, Optional, cast
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbHandle, VmbDouble, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError


__all__ = [
    'FloatFeature'
]


class FloatFeature(BaseFeature):
    """The BoolFeature is a feature, that is represented by a floating number."""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def get(self) -> float:
        """Get current value (float)

        Returns:
            Current float value.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_val = VmbDouble(0.0)

        try:
            call_vimba_c_func('VmbFeatureFloatGet', self._handle, self._info.name, byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value

    def get_range(self) -> Tuple[float, float]:
        """Get range of accepted values

        Returns:
            A pair of range boundaries. First value is the minimum second value is the maximum.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_min = VmbDouble(0.0)
        c_max = VmbDouble(0.0)

        try:
            call_vimba_c_func('VmbFeatureFloatRangeQuery', self._handle, self._info.name,
                              byref(c_min), byref(c_max))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return (c_min.value, c_max.value)

    def get_increment(self) -> Optional[float]:
        """Get increment (steps between valid values, starting from minimal values).

        Returns:
            The increment or None if the feature has currently no increment.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """

        exc = None
        c_has_val = VmbBool(False)
        c_val = VmbDouble(False)

        try:
            call_vimba_c_func('VmbFeatureFloatIncrementQuery', self._handle, self._info.name,
                              byref(c_has_val), byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value if c_has_val else None

    @RuntimeTypeCheckEnable()
    def set(self, val: float):
        """Set current value of type float.

        Arguments:
            val - The float value to set.

        Raises:
            TypeError if argument 'val' is not of type 'float'.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if value is out of bounds.
            VimbaFeatureError if executed within a registered change_handler.
        """
        exc = None

        try:
            call_vimba_c_func('VmbFeatureFloatSet', self._handle, self._info.name, val)

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

    def _build_value_error(self, val: float) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        min_, max_ = self.get_range()

        # Value Errors for float mean always out-of-bounds
        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. {} is not within [{}, {}].'
        msg = msg.format(caller_name, self.get_name(), val, min_, max_)

        return VimbaFeatureError(msg)
