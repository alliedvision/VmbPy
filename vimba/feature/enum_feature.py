# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

import ctypes

from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbBool, VmbUint32, VmbFeatureEnumEntry
from vimba.feature.base_feature import BaseFeature


class EnumEntry:
    def __init__(self, handle, feat_name, info):
        self._handle = handle
        self._feat_name = feat_name
        self._info = info

    def __str__(self):
        return self.as_string()

    def __int__(self):
        return self.as_int()

    def as_string(self):
        return self._info.name.decode()

    def as_int(self):
        return self._info.intValue

    def as_tuple(self):
        return (self.as_string(), self.as_int())

    def is_available(self):
        c_val = VmbBool()

        call_vimba_c_func('VmbFeatureEnumIsAvailable', self._handle,
                          self._feat_name, self._info.name, byref(c_val))

        return c_val.value


class EnumFeature(BaseFeature):
    def __init__(self, handle, info):
        super().__init__(handle, info)
        self._entires = _discover_enum_entries(self._handle, self._info.name)

    def get_all_entries(self):
        return self._entires

    def get_entry(self, int_or_name):
        for entry in self._entires:
            if type(int_or_name)(entry) == int_or_name:
                return entry

        # TODO: Add better error
        raise Exception('Lookup Failed')

    def get(self):
        c_val = ctypes.c_char_p(None)

        call_vimba_c_func('VmbFeatureEnumGet', self._handle, self._info.name,
                          byref(c_val))

        return self.get_entry(c_val.value.decode())

    def set(self, val: EnumEntry):
        call_vimba_c_func('VmbFeatureEnumSet', self._handle, self._info.name,
                          val._info.name)


def _discover_enum_entries(handle, feat_name):
    result = []
    enums_count = VmbUint32(0)

    call_vimba_c_func('VmbFeatureEnumRangeQuery', handle, feat_name, None, 0,
                      byref(enums_count))

    if enums_count.value:
        enums_found = VmbUint32(0)
        enums_names = (ctypes.c_char_p * enums_count.value)()

        call_vimba_c_func('VmbFeatureEnumRangeQuery', handle, feat_name,
                          enums_names, enums_count, byref(enums_found))

        for enum_name in enums_names[:enums_found.value]:
            enum_info = VmbFeatureEnumEntry()

            call_vimba_c_func('VmbFeatureEnumEntryGet', handle, feat_name,
                              enum_name, byref(enum_info),
                              sizeof(VmbFeatureEnumEntry))

            result.append(EnumEntry(handle, feat_name, enum_info))

    return tuple(result)
