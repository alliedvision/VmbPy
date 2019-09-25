"""Enumeration Feature implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

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
    """An EnumEntry represents a single value of an EnumFeature. A EnumEntry
    is a one to one association between a str and an int.
    """
    def __init__(self, handle: VmbHandle, feat_name: str, info: VmbFeatureEnumEntry):
        """Do not call directly. Access EnumEntries via EnumFeatures instead."""
        self.__handle: VmbHandle = handle
        self.__feat_name: str = feat_name
        self.__info: VmbFeatureEnumEntry = info

    def __str__(self):
        return self.as_string()

    def __int__(self):
        return self.as_int()

    def as_bytes(self) -> bytes:
        """Get EnumEntry as bytes"""
        return self.__info.name

    def as_string(self) -> str:
        """Get EnumEntry as str"""
        return self.as_bytes().decode()

    def as_int(self) -> int:
        """Get EnumEntry as int"""
        return self.__info.intValue

    def as_tuple(self) -> Tuple[str, int]:
        """Get EnumEntry in str and int representation"""
        return (self.as_string(), self.as_int())

    def is_available(self) -> bool:
        """Query if the EnumEntry can be used currently as a value.

        Returns:
            True if the EnumEntry can be used as a value otherwise False.
        """

        c_val = VmbBool(False)

        call_vimba_c_func('VmbFeatureEnumIsAvailable', self.__handle, self.__feat_name,
                          self.__info.name, byref(c_val))

        return c_val.value


EnumEntryTuple = Tuple[EnumEntry, ...]


class EnumFeature(BaseFeature):
    """The EnumFeature is a feature, where only EnumEntry values are allowed.
    All possible values of an EnumFeature can be queried through the Feature itself.
    """

    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        super().__init__(handle, info)

        self.__entries: EnumEntryTuple = _discover_enum_entries(self._handle, self._info.name)

    def get_all_entries(self) -> EnumEntryTuple:
        """Get a set of all possible EnumEntries of this Feature."""
        return self.__entries

    def get_available_entries(self) -> EnumEntryTuple:
        """Get a set of all currently available EnumEntries of this Feature."""
        return tuple([e for e in self.get_all_entries() if e.is_available()])

    @RuntimeTypeCheckEnable()
    def get_entry(self, val_or_name: Union[int, str]) -> EnumEntry:
        """Get a specific EnumEntry.

        Arguments:
            val_or_name: Lookup EnumEntry either by its name or its associated value.

        Returns:
            EnumEntry associated with Argument 'val_or_name'.

        Raises:
            TypeError if int_or_name it not of type int or type str.
            VimbaFeatureError if no EnumEntry is associated with 'val_or_name'
        """
        for entry in self.__entries:
            if type(val_or_name)(entry) == val_or_name:
                return entry

        msg = 'EnumEntry lookup failed: No Entry associated with \'{}\'.'.format(val_or_name)
        raise VimbaFeatureError(msg)

    def get(self) -> EnumEntry:
        """Get current feature value of type EnumEntry

        Returns:
            Feature value of type 'EnumEntry'.

        Raises:
            VimbaFeatureError if access rights are not sufficient.
        """

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
        """Set current feature value of type EnumFeature.

        Arguments:
            val - The value to set. Can be int or str or EnumEntry.

        Raises:
            TypeError if argument 'val' is not int, str or EunmFeature.
            VimbaFeatureError if val is of type int or str and does not match to an EnumEntry.
            VimbaFeatureError if access rights are not sufficient.
            VimbaFeatureError if executed within a registered change_handler.
        """

        if type(val) == EnumEntry:
            val = self.get_entry(str(val))

        else:
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
