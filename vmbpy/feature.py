"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import ctypes
import inspect
import threading
from typing import Callable, List, Optional, Tuple, Type, Union, cast

from .c_binding import (FeatureFlags, FeatureVisibility, VmbBool, VmbCError, VmbDouble, VmbError,
                        VmbFeatureData, VmbFeatureEnumEntry, VmbFeatureInfo, VmbHandle, VmbInt64,
                        VmbUint32, byref, call_vmb_c, create_string_buffer, decode_cstr,
                        decode_flags, sizeof)
from .c_binding.vmb_c import INVALIDATION_CALLBACK_TYPE
from .error import VmbFeatureError
from .util import Log, RuntimeTypeCheckEnable, TraceEnable

__all__ = [
    'ChangeHandler',
    'FeatureFlags',
    'FeatureVisibility',

    'IntFeature',
    'FloatFeature',
    'StringFeature',
    'BoolFeature',
    'EnumEntry',
    'EnumFeature',
    'CommandFeature',
    'RawFeature',

    'FeatureTypes',
    'FeatureTypeTypes',
    'FeaturesTuple',
    'discover_features',
    'discover_feature',
]


ChangeHandler = Callable[['FeatureTypes'], None]


class _BaseFeature:
    """This class provides most basic feature access functionality.

    All FeatureType implementations must derive from BaseFeature.
    """

    def __init__(self,  handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Access Features via System, Camera or Interface Types instead."""
        self._handle: VmbHandle = handle
        self._info: VmbFeatureInfo = info

        self.__handlers: List[ChangeHandler] = []
        self.__handlers_lock = threading.Lock()

        self.__feature_callback = INVALIDATION_CALLBACK_TYPE(self.__feature_cb_wrapper)

    def __repr__(self):
        rep = 'Feature'
        rep += '(_handle=' + repr(self._handle)
        rep += ',_info=' + repr(self._info)
        rep += ')'
        return rep

    def get_name(self) -> str:
        """Get Feature Name, e.g. 'DiscoveryInterfaceEvent'"""
        return decode_cstr(self._info.name)

    def get_type(self) -> Type['_BaseFeature']:
        """Get Feature Type, e.g. ``IntFeature``"""
        return type(self)

    def get_flags(self) -> Tuple[FeatureFlags, ...]:
        """Get a set of FeatureFlags, e.g. ``(FeatureFlags.Read, FeatureFlags.Write)``"""
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
        """Get unit of this Feature, e.g. 'dB' on Feature 'GainAutoMax'"""
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
        """Namespace of this feature"""
        return decode_cstr(self._info.sfncNamespace)

    def is_streamable(self) -> bool:
        """Indicates if a feature can be stored in /loaded from a file."""
        return self._info.isStreamable

    def has_selected_features(self) -> bool:
        """Indicates if this feature selects other features."""
        return self._info.hasSelectedFeatures

    @TraceEnable()
    def get_access_mode(self) -> Tuple[bool, bool]:
        """Get features current access mode.

        Returns:
            A pair of bool. In the first bool is ``True``, read access on this Feature is granted.
            If the second bool is ``True`` write access on this Feature is granted.
        """
        c_read = VmbBool(False)
        c_write = VmbBool(False)

        call_vmb_c('VmbFeatureAccessQuery', self._handle, self._info.name, byref(c_read),
                   byref(c_write))

        return (c_read.value, c_write.value)

    @TraceEnable()
    def is_readable(self) -> bool:
        """Is read access on this Features granted?

        Returns:
            ``True`` if read access is allowed on this feature. ``False`` is returned if read access
            is not allowed.
        """
        r, _ = self.get_access_mode()
        return r

    @TraceEnable()
    def is_writeable(self) -> bool:
        """Is write access on this Feature granted?

        Returns:
            ``True`` if write access is allowed on this feature. ``False`` is returned if write
            access is not allowed.
        """
        _, w = self.get_access_mode()
        return w

    @RuntimeTypeCheckEnable()
    def register_change_handler(self, handler: ChangeHandler):
        """Register Callable on the Feature.

        The Callable will be executed as soon as the Feature value changes. The first parameter on
        a registered handler will be called with the changed feature itself. The methods returns
        early if a given handler is already registered.

        Arguments:
            handler:
                The Callable that should be executed on change.

        Raises:
            TypeError:
                If parameters do not match their type hint.
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

    @RuntimeTypeCheckEnable()
    def unregister_change_handler(self, handler: ChangeHandler):
        """Remove registered Callable from the Feature.

        Removes a previously registered ``handler`` from this Feature. In case the ``handler`` that
        should be removed was never added in the first place, the method returns silently.

        Arguments:
            handler:
                The Callable that should be removed.

        Raises:
            TypeError:
                If parameters do not match their type hint.
        """

        with self.__handlers_lock:
            if handler not in self.__handlers:
                return

            if len(self.__handlers) == 1:
                self.__unregister_callback()

            self.__handlers.remove(handler)

    @TraceEnable()
    def __register_callback(self):
        call_vmb_c('VmbFeatureInvalidationRegister', self._handle, self._info.name,
                   self.__feature_callback, None)

    @TraceEnable()
    def __unregister_callback(self):
        call_vmb_c('VmbFeatureInvalidationUnregister', self._handle, self._info.name,
                   self.__feature_callback)

    def __feature_cb_wrapper(self, *_):   # coverage: skip
        # Skip coverage because it can't be measured. This is called from C-Context.
        with self.__handlers_lock:
            for handler in self.__handlers:

                try:
                    handler(self)

                except Exception as e:
                    msg = 'Caught Exception in handler: '
                    msg += 'Type: {}, '.format(type(e))
                    msg += 'Value: {}, '.format(e)
                    msg += 'raised by: {}'.format(handler)
                    Log.get_instance().error(msg)
                    raise e

    def _build_access_error(self) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        read, write = self.get_access_mode()

        msg = 'Invalid access while calling \'{}()\' of Feature \'{}\'. '

        msg += 'Read access: {}. '.format('allowed' if read else 'not allowed')
        msg += 'Write access: {}. '.format('allowed' if write else 'not allowed')

        return VmbFeatureError(msg.format(caller_name, self.get_name()))

    def _build_within_callback_error(self) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        msg = 'Invalid access. Calling \'{}()\' of Feature \'{}\' in change_handler is invalid.'

        return VmbFeatureError(msg.format(caller_name, self.get_name()))

    def _build_unhandled_error(self, c_exc: VmbCError) -> VmbFeatureError:
        return VmbFeatureError(repr(c_exc.get_error_code()))


class BoolFeature(_BaseFeature):
    """The BoolFeature is a feature represented by a boolean value."""

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface Types."""
        super().__init__(handle, info)

    def __str__(self):
        try:
            return 'BoolFeature(name={}, value={})'.format(self.get_name(), self.get())

        except Exception:
            return 'BoolFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def get(self) -> bool:
        """Get current feature value of type bool.

        Returns:
            Feature value of type bool.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = VmbBool(False)

        try:
            call_vmb_c('VmbFeatureBoolGet', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            err = e.get_error_code()
            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value

    @TraceEnable()
    def set(self, val):
        """Set current feature value of type bool.

        Arguments:
            val:
                The boolean value to set.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If called with an invalid value.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        as_bool = bool(val)

        try:
            call_vmb_c('VmbFeatureBoolSet', self._handle, self._info.name, as_bool)

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self._build_value_error(as_bool)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    def _build_value_error(self, val: bool) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value({}).'

        return VmbFeatureError(msg.format(caller_name, self.get_name(), val))


class CommandFeature(_BaseFeature):
    """The CommandFeature is a feature that can perform some kind of operation such as
    saving a user set.
    """

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface types."""
        super().__init__(handle, info)

    def __str__(self):
        return 'CommandFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def run(self):
        """Execute command feature.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        try:
            call_vmb_c('VmbFeatureCommandRun', self._handle, self._info.name)

        except VmbCError as e:
            exc = cast(VmbFeatureError, e)

            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    @TraceEnable()
    def is_done(self) -> bool:
        """Test if a feature execution is done.

        Returns:
            ``True`` if feature was fully executed. ``False`` if the feature is still being
            executed.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = VmbBool(False)

        try:
            call_vmb_c('VmbFeatureCommandIsDone', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value


class EnumEntry:
    """An EnumEntry represents a single value of an EnumFeature. An EnumEntry
    is a one-to-one association between a ``str`` and an ``int``.
    """
    @TraceEnable()
    def __init__(self, handle: VmbHandle, feat_name: str, info: VmbFeatureEnumEntry):
        """Do not call directly. Instead, access EnumEntries via EnumFeatures."""
        self.__handle: VmbHandle = handle
        self.__feat_name: str = feat_name
        self.__info: VmbFeatureEnumEntry = info

    def __str__(self):
        """Get EnumEntry as str"""
        return bytes(self).decode()

    def __int__(self):
        """Get EnumEntry as int"""
        return self.__info.intValue

    def __bytes__(self):
        """Get EnumEntry as bytes"""
        return self.__info.name

    def as_tuple(self) -> Tuple[str, int]:
        """Get EnumEntry in ``str`` and ``int`` representation"""
        return (str(self), int(self))

    @TraceEnable()
    def is_available(self) -> bool:
        """Query if the EnumEntry can currently be used as a value.

        Returns:
            ``True`` if the EnumEntry can be used as a value, otherwise ``False``.
        """

        c_val = VmbBool(False)

        call_vmb_c('VmbFeatureEnumIsAvailable', self.__handle, self.__feat_name, self.__info.name,
                   byref(c_val))

        return c_val.value


EnumEntryTuple = Tuple[EnumEntry, ...]


class EnumFeature(_BaseFeature):
    """The EnumFeature is a feature where only ``EnumEntry`` values are allowed.
    All possible values of an EnumFeature can be queried through the Feature itself.
    """

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface Types."""
        super().__init__(handle, info)

        self.__entries_var: Optional[EnumEntryTuple] = None

    def __str__(self):
        try:
            return 'EnumFeature(name={}, value={})'.format(self.get_name(), str(self.get()))

        except Exception:
            return 'EnumFeature(name={})'.format(self.get_name())

    @property
    def __entries(self) -> EnumEntryTuple:
        """Property for enum entries. Lazy initialization to reduce overhead in constructor."""
        if self.__entries_var is None:
            self.__entries_var = _discover_enum_entries(self._handle, self._info.name)

        return self.__entries_var

    def get_all_entries(self) -> EnumEntryTuple:
        """Get a set of all possible EnumEntries of this feature.

        Note:
            It is possible that not all EnumEntries returned by this area have currently valid
            values. See also :func:`get_available_entries`
        """
        return self.__entries

    @TraceEnable()
    def get_available_entries(self) -> EnumEntryTuple:
        """Get a set of all currently available EnumEntries of this feature."""
        return tuple([e for e in self.get_all_entries() if e.is_available()])

    def get_entry(self, val_or_name: Union[int, str]) -> EnumEntry:
        """Get a specific EnumEntry.

        Arguments:
            val_or_name:
                Look up EnumEntry either by its name or its associated value.

        Returns:
            EnumEntry associated with Argument ``val_or_name``.

        Raises:
            TypeError:
                If ``int_or_name`` is not of type ``int`` or type ``str``.
            VmbFeatureError:
                If no EnumEntry is associated with ``val_or_name``
        """
        for entry in self.__entries:
            if type(val_or_name)(entry) == val_or_name:
                return entry

        msg = 'EnumEntry lookup failed: No Entry associated with \'{}\'.'.format(val_or_name)
        raise VmbFeatureError(msg)

    @TraceEnable()
    def get(self) -> EnumEntry:
        """Get current feature value of type EnumEntry.

        Returns:
            Feature value of type EnumEntry.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = ctypes.c_char_p(None)

        try:
            call_vmb_c('VmbFeatureEnumGet', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return self.get_entry(c_val.value.decode() if c_val.value else '')

    @TraceEnable()
    def set(self, val: Union[int, str, EnumEntry]):
        """Set current feature value.

        Arguments:
            val:
                The value to set. Can be ``int``, or ``str``, or ``EnumEntry``.

        Raises:
            VmbFeatureError:
                If val is of type ``int`` or ``str`` and does not match an ``EnumEntry``.
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        if type(val) in (EnumEntry, str):
            as_entry = self.get_entry(str(val))

        else:
            as_entry = self.get_entry(int(val))

        try:
            call_vmb_c('VmbFeatureEnumSet', self._handle, self._info.name, bytes(as_entry))

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e


@TraceEnable()
def _discover_enum_entries(handle: VmbHandle, feat_name: str) -> EnumEntryTuple:
    result = []
    enums_count = VmbUint32(0)

    call_vmb_c('VmbFeatureEnumRangeQuery', handle, feat_name, None, 0, byref(enums_count))

    if enums_count.value:
        enums_found = VmbUint32(0)
        enums_names = (ctypes.c_char_p * enums_count.value)()

        call_vmb_c('VmbFeatureEnumRangeQuery', handle, feat_name, enums_names, enums_count,
                   byref(enums_found))

        for enum_name in enums_names[:enums_found.value]:
            enum_info = VmbFeatureEnumEntry()

            call_vmb_c('VmbFeatureEnumEntryGet', handle, feat_name, enum_name, byref(enum_info),
                       sizeof(VmbFeatureEnumEntry))

            result.append(EnumEntry(handle, feat_name, enum_info))

    return tuple(result)


class FloatFeature(_BaseFeature):
    """The FloatFeature is a feature represented by a floating point number."""

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface Types."""
        super().__init__(handle, info)

    def __str__(self):
        try:
            msg = 'FloatFeature(name={}, value={}, range={}, increment={})'
            return msg.format(self.get_name(), self.get(), self.get_range(), self.get_increment())

        except Exception:
            return 'FloatFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def get(self) -> float:
        """Get current value (float).

        Returns:
            Current float value.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = VmbDouble(0.0)

        try:
            call_vmb_c('VmbFeatureFloatGet', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value

    @TraceEnable()
    def get_range(self) -> Tuple[float, float]:
        """Get range of accepted values

        Returns:
            A pair of range boundaries. First value is the minimum, second value is the maximum.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_min = VmbDouble(0.0)
        c_max = VmbDouble(0.0)

        try:
            call_vmb_c('VmbFeatureFloatRangeQuery', self._handle, self._info.name, byref(c_min),
                       byref(c_max))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return (c_min.value, c_max.value)

    @TraceEnable()
    def get_increment(self) -> Optional[float]:
        """Get increment (steps between valid values, starting from minimum value).

        Returns:
            The increment or ``None`` if the feature currently has no increment.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_has_val = VmbBool(False)
        c_val = VmbDouble(False)

        try:
            call_vmb_c('VmbFeatureFloatIncrementQuery', self._handle, self._info.name,
                       byref(c_has_val), byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value if c_has_val else None

    @TraceEnable()
    def set(self, val: float):
        """Set current value of type float.

        Arguments:
            val:
                The float value to set.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If value is out of bounds.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        as_float = float(val)

        try:
            call_vmb_c('VmbFeatureFloatSet', self._handle, self._info.name, as_float)

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self._build_value_error(as_float)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    def _build_value_error(self, val: float) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        min_, max_ = self.get_range()

        # Value Errors for float mean always out-of-bounds
        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. {} is not within [{}, {}].'
        msg = msg.format(caller_name, self.get_name(), val, min_, max_)

        return VmbFeatureError(msg)


class IntFeature(_BaseFeature):
    """The IntFeature is a feature represented by an integer."""

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface Types."""
        super().__init__(handle, info)

    def __str__(self):
        try:
            msg = 'IntFeature(name={}, value={}, range={}, increment={})'
            return msg.format(self.get_name(), self.get(), self.get_range(), self.get_increment())

        except Exception:
            return 'IntFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def get(self) -> int:
        """Get current value (int).

        Returns:
            Current int value.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = VmbInt64()

        try:
            call_vmb_c('VmbFeatureIntGet', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value

    @TraceEnable()
    def get_range(self) -> Tuple[int, int]:
        """Get range of accepted values.

        Returns:
            A pair of range boundaries. First value is the minimum, second value is the maximum.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_min = VmbInt64()
        c_max = VmbInt64()

        try:
            call_vmb_c('VmbFeatureIntRangeQuery', self._handle, self._info.name, byref(c_min),
                       byref(c_max))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return (c_min.value, c_max.value)

    @TraceEnable()
    def get_increment(self) -> int:
        """Get increment (steps between valid values, starting from minimal values).

        Returns:
            The increment of this feature.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_val = VmbInt64()

        try:
            call_vmb_c('VmbFeatureIntIncrementQuery', self._handle, self._info.name, byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value

    @TraceEnable()
    def set(self, val: int):
        """Set current value of type int.

        Arguments:
            val:
                The int value to set.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If value is out of bounds or misaligned to the increment.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        as_int = int(val)

        try:
            call_vmb_c('VmbFeatureIntSet', self._handle, self._info.name, as_int)

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self._build_value_error(as_int)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    def _build_value_error(self, val) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        min_, max_ = self.get_range()

        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. '

        # Value out of bounds
        if (val < min_) or (max_ < val):
            msg += '{} is not within [{}, {}].'.format(val, min_, max_)

        # Misaligned value
        else:
            inc = self.get_increment()
            msg += '{} is not a multiple of {}, starting at {}'.format(val, inc, min_)

        return VmbFeatureError(msg.format(caller_name, self.get_name()))


class RawFeature(_BaseFeature):
    """The RawFeature is a feature represented by sequence of bytes."""

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera, or Interface Types."""
        super().__init__(handle, info)

    def __str__(self):
        try:
            msg = 'RawFeature(name={}, value={}, length={})'
            return msg.format(self.get_name(), self.get(), self.length())

        except Exception:
            return 'RawFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def get(self) -> bytes:  # coverage: skip
        """Get current value as a sequence of bytes

        Returns:
            Current value.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        # Note: Coverage is skipped. RawFeature is not testable in a generic way
        c_buf_avail = VmbUint32()
        c_buf_len = self.length()
        c_buf = create_string_buffer(c_buf_len)

        try:
            call_vmb_c('VmbFeatureRawGet', self._handle, self._info.name, c_buf, c_buf_len,
                       byref(c_buf_avail))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_buf.raw[:c_buf_avail.value]

    @TraceEnable()
    def set(self, buf: bytes):  # coverage: skip
        """Set current value as a sequence of bytes.

        Arguments:
            val:
                The value to set.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        # Note: Coverage is skipped. RawFeature is not testable in a generic way
        as_bytes = bytes(buf)

        try:
            call_vmb_c('VmbFeatureRawSet', self._handle, self._info.name, as_bytes, len(as_bytes))

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    @TraceEnable()
    def length(self) -> int:  # coverage: skip
        """Get length of byte sequence representing the value.

        Returns:
            Length of current value.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        # Note: Coverage is skipped. RawFeature is not testable in a generic way
        c_val = VmbUint32()

        try:
            call_vmb_c('VmbFeatureRawLengthQuery', self._handle, self._info.name,
                       byref(c_val))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_val.value


class StringFeature(_BaseFeature):
    """The StringFeature is a feature represented by a string."""

    @TraceEnable()
    def __init__(self, handle: VmbHandle, info: VmbFeatureInfo):
        """Do not call directly. Instead, access Features via System, Camera or Interface Types."""
        super().__init__(handle, info)

    def __str__(self):
        try:
            msg = 'StringFeature(name={}, value={}, max_length={})'
            return msg.format(self.get_name(), self.get(), self.get_max_length())

        except Exception:
            return 'StringFeature(name={})'.format(self.get_name())

    @TraceEnable()
    def get(self) -> str:
        """Get current value (str)

        Returns:
            Current str value.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_buf_len = VmbUint32(0)

        # Query buffer length
        try:
            call_vmb_c('VmbFeatureStringGet', self._handle, self._info.name, None, 0,
                       byref(c_buf_len))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        c_buf = create_string_buffer(c_buf_len.value)

        # Copy string from C-Layer
        try:
            call_vmb_c('VmbFeatureStringGet', self._handle, self._info.name, c_buf, c_buf_len,
                       None)

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_buf.value.decode()

    @TraceEnable()
    def set(self, val: str):
        """Set current value of type str.

        Arguments:
            val:
                The str value to set.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
            VmbFeatureError:
                If value exceeds the maximum string length.
            VmbFeatureError:
                If executed within a registered change_handler.
        """
        as_str = str(val)

        try:
            call_vmb_c('VmbFeatureStringSet', self._handle, self._info.name,
                       as_str.encode('utf8'))

        except VmbCError as e:
            err = e.get_error_code()

            if err == VmbError.InvalidAccess:
                exc = self._build_access_error()

            elif err == VmbError.InvalidValue:
                exc = self.__build_value_error(as_str)

            elif err == VmbError.InvalidCall:
                exc = self._build_within_callback_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

    @TraceEnable()
    def get_max_length(self) -> int:
        """Get maximum string length the Feature can store.

        Note:
            In this context, string length does not mean the number of characters, it means the
            number of bytes after encoding. A string encoded in UTF-8 could exceed the maximum
            length. Additionally the last byte of the string feature is reserved for a null-byte to
            indicate the end of the string.

        Returns:
            The number of ASCII characters the Feature can store.

        Raises:
            VmbFeatureError:
                If access rights are not sufficient.
        """
        c_max_len = VmbUint32(0)

        try:
            call_vmb_c('VmbFeatureStringMaxlengthQuery', self._handle, self._info.name,
                       byref(c_max_len))

        except VmbCError as e:
            if e.get_error_code() == VmbError.InvalidAccess:
                exc = self._build_access_error()

            else:
                exc = self._build_unhandled_error(e)

            raise exc from e

        return c_max_len.value

    def __build_value_error(self, val: str) -> VmbFeatureError:
        caller_name = inspect.stack()[1][3]
        val_as_bytes = val.encode('utf8')
        max_len = self.get_max_length()

        msg = 'Called \'{}()\' of Feature \'{}\' with invalid value. \'{}\' > max length \'{}\'.'

        return VmbFeatureError(msg.format(caller_name, self.get_name(), val_as_bytes, max_len))


FeatureTypes = Union[IntFeature, FloatFeature, StringFeature, BoolFeature, EnumFeature,
                     CommandFeature, RawFeature]

FeatureTypeTypes = Union[Type[IntFeature], Type[FloatFeature], Type[StringFeature],
                         Type[BoolFeature], Type[EnumFeature], Type[CommandFeature],
                         Type[RawFeature]]

FeaturesTuple = Tuple[FeatureTypes, ...]


def _build_feature(handle: VmbHandle, info: VmbFeatureInfo) -> FeatureTypes:
    feat_value = VmbFeatureData(info.featureDataType)
    feat: FeatureTypes

    if VmbFeatureData.Int == feat_value:
        feat = IntFeature(handle, info)

    elif VmbFeatureData.Float == feat_value:
        feat = FloatFeature(handle, info)

    elif VmbFeatureData.String == feat_value:
        feat = StringFeature(handle, info)

    elif VmbFeatureData.Bool == feat_value:
        feat = BoolFeature(handle, info)

    elif VmbFeatureData.Enum == feat_value:
        feat = EnumFeature(handle, info)

    elif VmbFeatureData.Command == feat_value:
        feat = CommandFeature(handle, info)

    else:
        feat = RawFeature(handle, info)

    return feat


@TraceEnable()
def discover_features(handle: VmbHandle) -> FeaturesTuple:
    """Discover all features associated with the given handle.

    Arguments:
        handle:
            VmbC entity used to find the associated features.

    Returns:
        A set of all discovered Features associated with handle.
    """
    result = []

    feats_count = VmbUint32(0)

    call_vmb_c('VmbFeaturesList', handle, None, 0, byref(feats_count), sizeof(VmbFeatureInfo))

    if feats_count:
        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vmb_c('VmbFeaturesList', handle, feats_infos, feats_count, byref(feats_found),
                   sizeof(VmbFeatureInfo))

        for info in feats_infos[:feats_found.value]:
            result.append(_build_feature(handle, info))

    return tuple(result)


@TraceEnable()
def discover_feature(handle: VmbHandle, feat_name: str) -> FeatureTypes:
    """Discover a singe feature associated with the given handle.

    Arguments:
        handle:
            VmbC entity used to find the associated feature.
        feat_name:
            Name of the Feature that should be searched.

    Returns:
        The Feature associated with 'handle' by the name of 'feat_name'
    """
    info = VmbFeatureInfo()

    call_vmb_c('VmbFeatureInfoQuery', handle, feat_name.encode('utf-8'), byref(info),
               sizeof(VmbFeatureInfo))

    return _build_feature(handle, info)
