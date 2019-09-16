# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

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
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def get(self) -> float:
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
