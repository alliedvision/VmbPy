# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from vimba.util import Log

__all__ = [
    'VimbaSystemError',
    'VimbaFeatureError'
]


class _LoggedError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        Log.get_instance().error(msg)


class VimbaSystemError(_LoggedError):
    pass


class VimbaFeatureError(_LoggedError):
    pass
