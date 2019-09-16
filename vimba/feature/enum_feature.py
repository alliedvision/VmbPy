# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

import ctypes

from typing import Tuple, Union, cast
from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbBool, VmbHandle, VmbFeatureEnumEntry, VmbFeatureInfo, VmbUint32, \
                            VmbError, VimbaCError
from vimba.feature.base_feature import BaseFeature
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaFeatureError

__all__ = [
    'EnumEntry',
    'EnumFeature'
]


class EnumEntry:
    def __init__(self, handle: VmbHandle, feat_name: str, info: VmbFeatureEnumEntry):
        self.__handle: VmbHandle = handle
        self.__feat_name: str = feat_name
        self.__info: VmbFeatureEnumEntry = info

    def __str__(self):
        return self.as_string()

    def __int__(self):
        return self.as_int()

    def as_bytes(self) -> bytes:
        return self.__info.name

    def as_string(self) -> str:
        return self.as_bytes().decode()

    def as_int(self) -> int:
        return self.__info.intValue

    def as_tuple(self) -> Tuple[str, int]:
        return (self.as_string(), self.as_int())

    def is_available(self) -> bool:
        c_val = VmbBool(False)

        call_vimba_c_func('VmbFeatureEnumIsAvailable', self.__handle, self.__feat_name,
                          self.__info.name, byref(c_val))

        return c_val.value


EnumEntryTuple = Tuple[EnumEntry, ...]


class EnumFeature(BaseFeature):
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        super().__init__(handle, info)

        self._entires: EnumEntryTuple = _discover_enum_entries(self._handle, self._info.name)

    def get_all_entries(self) -> EnumEntryTuple:
        return self._entires

    @RuntimeTypeCheckEnable()
    def get_entry(self, int_or_name: Union[int, str]) -> EnumEntry:
        for entry in self._entires:
            if type(int_or_name)(entry) == int_or_name:
                return entry

        msg = 'EnumEntry lookup failed: No Entry associated with \'{}\'.'.format(int_or_name)
        raise VimbaFeatureError(msg)

    def get(self) -> EnumEntry:
        exc = None
        c_val = ctypes.c_char_p(None)

        try:
            call_vimba_c_func('VmbFeatureEnumGet', self._handle, self._info.name, byref(c_val))

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

        if exc:
            raise exc

        return self.get_entry(c_val.value.decode() if c_val.value else '')

    @RuntimeTypeCheckEnable()
    def set(self, val: Union[int, str, EnumEntry]):
        if type(val) != EnumEntry:
            val = self.get_entry(val)

        exc = None
        val = cast(EnumEntry, val)

        try:
            call_vimba_c_func('VmbFeatureEnumSet', self._handle, self._info.name, val.as_bytes())

        except VimbaCError as e:
            exc = cast(VimbaFeatureError, e)
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

        if exc:
            raise exc


def _discover_enum_entries(handle: VmbHandle, feat_name: str) -> EnumEntryTuple:
    result = []
    enums_count = VmbUint32(0)

    call_vimba_c_func('VmbFeatureEnumRangeQuery', handle, feat_name, None, 0,
                      byref(enums_count))

    if enums_count.value:
        enums_found = VmbUint32(0)
        enums_names = (ctypes.c_char_p * enums_count.value)()

        call_vimba_c_func('VmbFeatureEnumRangeQuery', handle, feat_name, enums_names, enums_count,
                          byref(enums_found))

        for enum_name in enums_names[:enums_found.value]:
            enum_info = VmbFeatureEnumEntry()

            call_vimba_c_func('VmbFeatureEnumEntryGet', handle, feat_name, enum_name,
                              byref(enum_info), sizeof(VmbFeatureEnumEntry))

            result.append(EnumEntry(handle, feat_name, enum_info))

    return tuple(result)
