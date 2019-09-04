# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add getters to all members given interface struct. Handle Encoding
# TODO: Add repr and str

from vimba.c_binding import call_vimba_c_func, byref
from vimba.c_binding import VmbFeatureInfo, VmbHandle, VmbBool


class BaseFeature:
    def __init__(self,  handle: VmbHandle, info: VmbFeatureInfo):
        self._handle = handle
        self._info = info

    def __str__(self):
        return 'Feature(handle={}, name={})'.format(self._handle,
                                                    self.get_name())

    def __repr__(self):
        rep = 'Feature'
        rep += '(_handle=' + repr(self._handle)
        rep += ',_info=' + repr(self._info)
        rep += ')'
        return rep

    def get_name(self):
        return self._info.name.decode()

    def get_type(self):
        return type(self)

    def get_flags(self):
        pass

    def get_category(self):
        return self._info.category.decode()

    def get_display_name(self):
        return self._info.displayName.decode()

    def get_polling_time(self):
        return self._info.pollingTime.value

    def get_unit(self):
        return self._info.unit.decode()

    def get_representation(self):
        return self._info.representation.decode()

    def get_tooltip(self):
        return self._info.get_tooltip.decode()

    def get_description(self):
        return self._info.get_description.decode()

    def is_streamable(self):
        return self._info.is_streamable

    def has_affected_features(self):
        return self._info.hasAffectedFeatures

    def has_selected_features(self):
        return self._info.hasSelectedFeatures

    def get_access_mode(self):
        c_read = VmbBool()
        c_write = VmbBool()

        call_vimba_c_func('VmbFeatureAccessQuery', self._handle,
                          self._info.name, byref(c_read), byref(c_write))

        return (c_read.value, c_write.value)

    def is_readable(self):
        r, _ = self.get_access_mode()
        return r

    def is_writeable(self):
        _, w = self.get_access_mode()
        return w
