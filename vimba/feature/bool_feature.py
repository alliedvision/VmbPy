# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool
from vimba.feature.base_feature import BaseFeature


class BoolFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)

    def get(self):
        c_val = VmbBool(False)
        call_vimba_c_func('VmbFeatureBoolGet', self._handle, self._info.name,
                          byref(c_val))
        return c_val.value

    def set(self, val: bool):
        call_vimba_c_func('VmbFeatureBoolSet', self._handle, self._info.name,
                          val)
