# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import call_vimba_c_func, byref, create_string_buffer
from vimba.c_binding import VmbUint32
from vimba.feature.base_feature import BaseFeature


class StringFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)

    def get(self):
        c_buf_len = VmbUint32(0)

        call_vimba_c_func('VmbFeatureStringGet', self._handle,
                          self._info.name, None, 0, byref(c_buf_len))

        c_buf = create_string_buffer(c_buf_len.value)

        call_vimba_c_func('VmbFeatureStringGet', self._handle,
                          self._info.name, c_buf, c_buf_len, None)

        return c_buf.value.decode()

    def set(self, val: str):
        call_vimba_c_func('VmbFeatureStringSet', self._handle,
                          self._info.name, val.encode('uft-8'))

    def max_length(self):
        c_max_len = VmbUint32(0)

        call_vimba_c_func('VmbFeatureStringMaxlengthQuery', self._handle,
                          self._info.name, byref(c_max_len))

        return c_max_len.value
