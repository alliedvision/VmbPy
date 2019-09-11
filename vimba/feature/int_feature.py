# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from typing import Tuple
from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbHandle, VmbInt64, VmbFeatureInfo
from vimba.feature.base_feature import BaseFeature


class IntFeature(BaseFeature):
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

    def get(self) -> int:
        c_val = VmbInt64()

        call_vimba_c_func('VmbFeatureIntGet', self._handle, self._info.name, byref(c_val))

        return c_val.value

    def get_range(self) -> Tuple[int, int]:
        c_min = VmbInt64()
        c_max = VmbInt64()

        call_vimba_c_func('VmbFeatureIntRangeQuery', self._handle, self._info.name, byref(c_min),
                          byref(c_max))

        return (c_min.value, c_max.value)

    def get_increment(self) -> int:
        c_val = VmbInt64()

        call_vimba_c_func('VmbFeatureIntIncrementQuery', self._handle, self._info.name,
                          byref(c_val))

        return c_val.value

    def set(self, val: int):
        call_vimba_c_func('VmbFeatureIntSet', self._handle, self._info.name, val)
