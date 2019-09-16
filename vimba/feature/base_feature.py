# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add getters to all members given interface struct. Handle Encoding
# TODO: Add repr and str
import inspect

from enum import IntEnum
from typing import Tuple, List, Callable, Type
from threading import Lock
from vimba.c_binding import call_vimba_c_func, byref, decode_cstr, decode_flags
from vimba.c_binding import VmbFeatureInfo, VmbFeatureFlags, VmbHandle, VmbFeatureVisibility, \
                            VmbBool, VmbInvalidationCallback
from vimba.util import Log
from vimba.error import VimbaFeatureError

__all__ = [
    'ChangeHandler',
    'FeatureFlags',
    'FeatureVisibility',
    'BaseFeature'
]


ChangeHandler = Callable[[Type['BaseFeature']], None]


class FeatureFlags(IntEnum):
    None_ = VmbFeatureFlags.None_
    Read = VmbFeatureFlags.Read
    Write = VmbFeatureFlags.Write
    Undocumented = VmbFeatureFlags.Undocumented
    Volatile = VmbFeatureFlags.Volatile
    ModifyWrite = VmbFeatureFlags.ModifyWrite


class FeatureVisibility(IntEnum):
    Unknown = VmbFeatureVisibility.Unknown
    Beginner = VmbFeatureVisibility.Beginner
    Expert = VmbFeatureVisibility.Expert
    Guru = VmbFeatureVisibility.Guru
    Invisible = VmbFeatureVisibility.Invisible


class BaseFeature:
    def __init__(self,  handle: VmbHandle, info: VmbFeatureInfo):
        self._handle: VmbHandle = handle
        self._info: VmbFeatureInfo = info

        self.__change_handlers: List[ChangeHandler] = []
        self.__change_handlers_lock = Lock()
        self.__callback = VmbInvalidationCallback(self.__callback_impl)

    def __str__(self):
        return 'Feature(name={}, type={})'.format(self.get_name(), self.get_type())

    def __repr__(self):
        rep = 'Feature'
        rep += '(_handle=' + repr(self._handle)
        rep += ',_info=' + repr(self._info)
        rep += ')'
        return rep

    def get_name(self) -> str:
        return decode_cstr(self._info.name)

    def get_type(self) -> Type['BaseFeature']:
        return type(self)

    def get_flags(self) -> Tuple[FeatureFlags, ...]:
        return decode_flags(FeatureFlags, self._info.featureFlags)

    def get_category(self) -> str:
        return decode_cstr(self._info.category)

    def get_display_name(self) -> str:
        return decode_cstr(self._info.displayName)

    def get_polling_time(self) -> int:
        return self._info.pollingTime

    def get_unit(self) -> str:
        return decode_cstr(self._info.unit)

    def get_representation(self) -> str:
        return decode_cstr(self._info.representation)

    def get_visibility(self) -> FeatureVisibility:
        return FeatureVisibility(self._info.visibility)

    def get_tooltip(self) -> str:
        return decode_cstr(self._info.tooltip)

    def get_description(self) -> str:
        return decode_cstr(self._info.description)

    def get_sfnc_namespace(self) -> str:
        return decode_cstr(self._info.sfncNamespace)

    def is_streamable(self) -> bool:
        return self._info.isStreamable

    def has_affected_features(self) -> bool:
        return self._info.hasAffectedFeatures

    def has_selected_features(self) -> bool:
        return self._info.hasSelectedFeatures

    def get_access_mode(self) -> Tuple[bool, bool]:
        c_read = VmbBool(False)
        c_write = VmbBool(False)

        call_vimba_c_func('VmbFeatureAccessQuery', self._handle, self._info.name, byref(c_read),
                          byref(c_write))

        return (c_read.value, c_write.value)

    def is_readable(self) -> bool:
        r, _ = self.get_access_mode()
        return r

    def is_writeable(self) -> bool:
        _, w = self.get_access_mode()
        return w

    def register_change_handler(self, change_handler: ChangeHandler):
        with self.__change_handlers_lock:
            if change_handler in self.__change_handlers:
                return

            self.__change_handlers.append(change_handler)

            if len(self.__change_handlers) == 1:
                self.__register_callback()

    def unregister_all_change_handlers(self):
        with self.__change_handlers_lock:
            if self.__change_handlers:
                self.__unregister_callback()
                self.__change_handlers.clear()

    def unregister_change_handler(self, change_handler: ChangeHandler):
        with self.__change_handlers_lock:
            if change_handler not in self.__change_handlers:
                return

            if len(self.__change_handlers) == 1:
                self.__unregister_callback()

            self.__change_handlers.remove(change_handler)

    def __register_callback(self):
        call_vimba_c_func('VmbFeatureInvalidationRegister', self._handle, self._info.name,
                          self.__callback, None)

    def __unregister_callback(self):
        call_vimba_c_func('VmbFeatureInvalidationUnregister', self._handle, self._info.name,
                          self.__callback)

    def __callback_impl(self, *ignored):
        with self.__change_handlers_lock:
            for change_handler in self.__change_handlers:

                # Since this is called from the C-Context, all exceptions
                # should be fetched.
                try:
                    change_handler(self)

                except BaseException as e:
                    msg = 'Caught Exception in change_handler: '
                    msg += 'Type: {}, '.format(type(e))
                    msg += 'Value: {}, '.format(e)
                    msg += 'raised by: {}'.format(change_handler)

                    Log.get_instance().error(msg)

    def _build_access_error(self) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        read, write = self.get_access_mode()

        msg = 'Invalid access while calling \'{}()\' of Feature \'{}\'. '

        msg += 'Read access: {}. '.format('allowed' if read else 'not allowed')
        msg += 'Write access: {}. '.format('allowed' if write else 'not allowed')

        return VimbaFeatureError(msg.format(caller_name, self.get_name()))

    def _build_within_callback_error(self) -> VimbaFeatureError:
        caller_name = inspect.stack()[1][3]
        msg = 'Invalid access. Calling \'{}()\' of Feature \'{}\' in change_handler is invalid.'

        return VimbaFeatureError(msg.format(caller_name, self.get_name()))
