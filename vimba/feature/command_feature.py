"""Command Feature implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from typing import cast
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbHandle, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.error import VimbaFeatureError

__all__ = [
    'CommandFeature'
]


class CommandFeature(BaseFeature):
    """The CommandFeature is a feature, that can perform some kind on operation."""

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

    def run(self):
        """Execute feature.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """
        exc = None

        try:
            call_vimba_c_func('VmbFeatureCommandRun', self._handle, self._info.name)

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

    def is_done(self) -> bool:
        """Test if a feature execution is done.

        Returns:
            True if feature was fully executed. False if the Feature is still being executed.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """

        exc = None
        c_val = VmbBool(False)

        try:
            call_vimba_c_func('VmbFeatureCommandIsDone', self._handle, self._info.name,
                              byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return c_val.value
