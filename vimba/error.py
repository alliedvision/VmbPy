# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.c_binding import VmbError


class VimbaCError(Exception):
    def __init__(self, c_error: VmbError):
        assert type(c_error) == VmbError

        super().__init__(str(c_error))
        self.c_error = c_error


class FeatureAccessError(Exception):
    pass
