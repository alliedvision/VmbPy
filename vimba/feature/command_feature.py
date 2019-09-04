# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool
from vimba.feature.base_feature import BaseFeature


class CommandFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)

    def run(self):
        call_vimba_c_func('VmbFeatureCommandRun', self._handle,
                          self._info.name)

    def is_done(self):
        c_val = VmbBool()

        call_vimba_c_func('VmbFeatureCommandIsDone', self._handle,
                          self._info.name, byref(c_val))

        return c_val.value
