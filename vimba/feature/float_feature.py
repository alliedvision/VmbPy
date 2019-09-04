# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbDouble
from vimba.feature.base_feature import BaseFeature


class FloatFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)

    def get(self):
        c_val = VmbDouble()

        call_vimba_c_func('VmbFeatureFloatGet', self._handle, self._info.name,
                          byref(c_val))

        return c_val.value

    def get_range(self):
        c_min = VmbDouble()
        c_max = VmbDouble()

        call_vimba_c_func('VmbFeatureFloatRangeQuery', self._handle,
                          self._info.name, byref(c_min), byref(c_max))

        return (c_min.value, c_max.value)

    def get_increment(self):
        c_has_val = VmbBool()
        c_val = VmbDouble()

        call_vimba_c_func('VmbFeatureFloatIncrementQuery', self._handle,
                          self._info.name, byref(c_has_val), byref(c_val))

        if not c_has_val:
            # TODO: Throw clever exception...
            raise Exception('Feature has no increment')

        return c_val.value

    def set(self, val: float):
        call_vimba_c_func('VmbFeatureFloatSet', self._handle, self._info.name,
                          val)
