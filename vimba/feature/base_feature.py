"""Basic Feature access implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

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
    """Enumeration specifying additional information on the feature.

    Enumeration values:
        None_       - No additional information is provided
        Read        - Static info about read access.
        Write       - Static info about write access.
        Volatile    - Value may change at any time
        ModifyWrite - Value may change after a write
    """

    None_ = VmbFeatureFlags.None_
    Read = VmbFeatureFlags.Read
    Write = VmbFeatureFlags.Write
    Volatile = VmbFeatureFlags.Volatile
    ModifyWrite = VmbFeatureFlags.ModifyWrite


class FeatureVisibility(IntEnum):
    """Enumeration specifying UI feature visibility.

    Enumeration values:
        Unknown   - Feature visibility is not known
        Beginner  - Feature is visible in feature list (beginner level)
        Expert    - Feature is visible in feature list (expert level)
        Guru      - Feature is visible in feature list (guru level)
        Invisible - Feature is not visible in feature listSu
    """

    Unknown = VmbFeatureVisibility.Unknown
    Beginner = VmbFeatureVisibility.Beginner
    Expert = VmbFeatureVisibility.Expert
    Guru = VmbFeatureVisibility.Guru
    Invisible = VmbFeatureVisibility.Invisible


class BaseFeature:
    """This class provides most basic feature access functionality.
    All FeatureType implementations must derive from BaseFeature.
    """

    def __init__(self,  handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        self._handle: VmbHandle = handle
        self._info: VmbFeatureInfo = info

        self.__handlers: List[ChangeHandler] = []
        self.__handlers_lock = Lock()
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
        """Get Feature Name, e.g. DiscoveryInterfaceEvent"""
        return decode_cstr(self._info.name)

    def get_type(self) -> Type['BaseFeature']:
        """Get Feature Type, e.g. IntFeature"""
        return type(self)

    def get_flags(self) -> Tuple[FeatureFlags, ...]:
        """Get a set of FeatureFlags, e.g. (FeatureFlags.Read, FeatureFlags.Write))"""
        val = self._info.featureFlags

        # The feature flag could contain undocumented values at third bit.
        # To prevent any issues, clear the third bit before decoding.
        val &= ~4

        return decode_flags(FeatureFlags, val)

    def get_category(self) -> str:
        """Get Feature category, e.g. '/Discovery'"""
        return decode_cstr(self._info.category)

    def get_display_name(self) -> str:
        """Get lengthy Feature name e.g. 'Discovery Interface Event'"""
        return decode_cstr(self._info.displayName)

    def get_polling_time(self) -> int:
        """Predefined Polling Time for volatile features."""
        return self._info.pollingTime

    def get_unit(self) -> str:
        """Get Unit of this Feature, e.g. 'dB' on Feature 'GainAutoMax'"""
        return decode_cstr(self._info.unit)

    def get_representation(self) -> str:
        """Representation of a numeric feature."""
        return decode_cstr(self._info.representation)

    def get_visibility(self) -> FeatureVisibility:
        """UI visibility of this feature"""
        return FeatureVisibility(self._info.visibility)

    def get_tooltip(self) -> str:
        """Short Feature description."""
        return decode_cstr(self._info.tooltip)

    def get_description(self) -> str:
        """Long feature description."""
        return decode_cstr(self._info.description)

    def get_sfnc_namespace(self) -> str:
        """This features namespace"""
        return decode_cstr(self._info.sfncNamespace)

    def is_streamable(self) -> bool:
        """Indicates if a feature can be stored in /loaded from a file."""
        return self._info.isStreamable

    def has_affected_features(self) -> bool:
        """Indicates if this feature can affect other features."""
        return self._info.hasAffectedFeatures

    def has_selected_features(self) -> bool:
        """Indicates if this feature selects other features."""
        return self._info.hasSelectedFeatures

    def get_access_mode(self) -> Tuple[bool, bool]:
        """Get features current access mode.

        Returns:
            A pair of bool. In the first bool is True, read access on this Feature is granted.
            If the second bool is True write access on this Feature is granted.
        """
        c_read = VmbBool(False)
        c_write = VmbBool(False)

        call_vimba_c_func('VmbFeatureAccessQuery', self._handle, self._info.name, byref(c_read),
                          byref(c_write))

        return (c_read.value, c_write.value)

    def is_readable(self) -> bool:
        """Is read access on this Features granted?

        Returns:
            True if read access is allowed on this feature. False is returned if read access
            is not allowed.
        """
        r, _ = self.get_access_mode()
        return r

    def is_writeable(self) -> bool:
        """Is write access on this Features granted?

        Returns:
            True if write access is allowed on this feature. False is returned if write access
            is not allowed.
        """
        _, w = self.get_access_mode()
        return w

    # RuntimeCheckEnable()
    def register_change_handler(self, handler: ChangeHandler):
        """Register Callable on the Feature.

        The Callable will be executed as soon as the Features value changes. The first parameter
        on a registered handler will be called with the changed feature itself. The methods
        returns early if a given handler is already registered.

        Arguments:
            handler - The Callable that should be executed on change.
        """

        with self.__handlers_lock:
            if handler in self.__handlers:
                return

            self.__handlers.append(handler)

            if len(self.__handlers) == 1:
                self.__register_callback()

    def unregister_all_change_handlers(self):
        """Remove all registered change handlers."""
        with self.__handlers_lock:
            if self.__handlers:
                self.__unregister_callback()
                self.__handlers.clear()

    # RuntimeCheckEnable()
    def unregister_change_handler(self, handler: ChangeHandler):
        """Remove registered Callable from the Feature.

        Removes a previously registered handler from this Feature. In case the
        handler that should be removed was never added in the first place, the method
        returns silently.

        Arguments:
            handler - The Callable that should be removed.
        """

        with self.__handlers_lock:
            if handler not in self.__handlers:
                return

            if len(self.__handlers) == 1:
                self.__unregister_callback()

            self.__handlers.remove(handler)

    def __register_callback(self):
        call_vimba_c_func('VmbFeatureInvalidationRegister', self._handle, self._info.name,
                          self.__callback, None)

    def __unregister_callback(self):
        call_vimba_c_func('VmbFeatureInvalidationUnregister', self._handle, self._info.name,
                          self.__callback)

    def __callback_impl(self, *ignored):   # coverage: skip
        # Note: This function is executed from the C-Context. This means that:
        # 1) All Exceptions must be fetched since there is no direct caller that could catch a
        #    thrown exception.
        # 2) Coverage is disabled, because it can't track execution from the C-Context.

        with self.__handlers_lock:
            for handler in self.__handlers:

                try:
                    handler(self)

                except BaseException as e:
                    msg = 'Caught Exception in handler: '
                    msg += 'Type: {}, '.format(type(e))
                    msg += 'Value: {}, '.format(e)
                    msg += 'raised by: {}'.format(handler)

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
