# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str
from typing import cast
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbHandle, VmbFeatureInfo, VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.error import VimbaFeatureError

__all__ = [
    'CommandFeature'
]


class CommandFeature(BaseFeature):
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def run(self):
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
