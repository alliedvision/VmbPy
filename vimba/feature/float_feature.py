# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from typing import Tuple
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbBool, VmbHandle, VmbDouble, VmbFeatureInfo
from vimba.feature.base_feature import BaseFeature


class FloatFeature(BaseFeature):
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def get(self) -> float:
        c_val = VmbDouble(0.0)

        call_vimba_c_func('VmbFeatureFloatGet', self._handle, self._info.name, byref(c_val))

        return c_val.value

    def get_range(self) -> Tuple[float, float]:
        c_min = VmbDouble(0.0)
        c_max = VmbDouble(0.0)

        call_vimba_c_func('VmbFeatureFloatRangeQuery', self._handle, self._info.name, byref(c_min),
                          byref(c_max))

        return (c_min.value, c_max.value)

    def get_increment(self) -> float:
        c_has_val = VmbBool(False)
        c_val = VmbDouble(False)

        call_vimba_c_func('VmbFeatureFloatIncrementQuery', self._handle, self._info.name,
                          byref(c_has_val), byref(c_val))

        if not c_has_val:
            # TODO: Throw clever exception...
            raise Exception('Feature has no increment')

        return c_val.value

    def set(self, val: float):
        call_vimba_c_func('VmbFeatureFloatSet', self._handle, self._info.name, val)
