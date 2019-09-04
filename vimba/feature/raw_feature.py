# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)

from vimba.c_binding import call_vimba_c_func, byref, create_string_buffer
from vimba.c_binding import VmbUint32
from vimba.feature.base_feature import BaseFeature


class RawFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)

    def get(self):
        c_buf_avail = VmbUint32()
        c_buf_len = self.length()
        c_buf = create_string_buffer(c_buf_len)

        call_vimba_c_func('VmbFeatureRawGet', self._handle, self._info.name,
                          c_buf, c_buf_len, byref(c_buf_avail))

        return c_buf.raw

    def set(self, buf: bytes):
        call_vimba_c_func('VmbFeatureRawSet', self._handle, self._info.name,
                          buf, len(buf))

    def length(self):
        c_val = VmbUint32()

        call_vimba_c_func('VmbFeatureRawLengthQuery', self._handle,
                          self._info.name, byref(c_val))

        return c_val.value
