"""Boolean Feature implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import inspect

from typing import cast
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbHandle, VmbFeatureInfo, VimbaCError, VmbError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError

__all__ = [
    'BoolFeature'
]


class BoolFeature(BaseFeature):
    """The BoolFeature is a feature, that is represented by a boolean value"""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def get(self) -> bool:
        """Get current feature value of type bool

        Returns:
            Feature value of type 'bool'.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None
        c_val = VmbBool(False)

        try:
            call_vimba_c_func('VmbFeatureBoolGet', self._handle, self._info.name, byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value

    @RuntimeTypeCheckEnable()
    def set(self, val: bool):
        """Set current feature value of type bool

        Arguments:
            val - The boolean value to set.

        Raises:
            TypeError if argument 'val' is not of type 'bool'.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if called with an invalid value.
            VimbaFeatureError if executed within a registered change_handler.
        """
        exc = None

        try:
            call_vimba_c_func('VmbFeatureBoolSet', self._handle, self._info.name, val)

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

    def _build_value_error(self, val: bool) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value({}).'

        return VimbaFeatureError(msg.format(caller_name, self.get_name(), val))
