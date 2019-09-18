"""VimbaPython specific error Types.

This module contains VimbaPython specific Error Types.
All contained error types add a Log entry upon error construction.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

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
    """Errors related to the underlaying Vimba System

    Error Type to indicate system wide errors like:
    - Incomplete Vimba installation.
    - Incompatible version of the underlaying C-Layer.
    - Running on an unsupported OS.
    """
    pass

class VimbaCameraError(_LoggedError):
    """ Errors related to Cameras

    Error Type to indicated Camera related Errors like
    - Access on a disconnected camera Object
    - Lookup of non-existing cameras etc
    """
    pass

class VimbaFeatureError(_LoggedError):
    """Error related to Feature access.

    Error Type to indicate invalid Feature access like:
    - Invalid access mode on Feature access.
    - Out of range values upon setting a value.
    - Failed lookup of Features.
    """
    pass
