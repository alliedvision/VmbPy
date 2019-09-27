"""VimbaPython top level module.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__version__ = '0.0.1'

__all__ = [
    'Vimba',
    'CameraChangeHandler',
    'InterfaceChangeHandler',
    'FrameHandler',

    'AccessMode',
    'VimbaSystemError',
    'VimbaCameraError',
    'VimbaInterfaceError',
    'VimbaFeatureError',

    'IntFeature',
    'FloatFeature',
    'StringFeature',
    'BoolFeature',
    'EnumFeature',
    'CommandFeature',
    'RawFeature',

    'LogLevel',
    'LogConfig',
    'Log',
    'LOG_CONFIG_TRACE_CONSOLE_ONLY',
    'LOG_CONFIG_TRACE_FILE_ONLY',
    'LOG_CONFIG_TRACE',
    'LOG_CONFIG_INFO_CONSOLE_ONLY',
    'LOG_CONFIG_INFO_FILE_ONLY',
    'LOG_CONFIG_INFO',
    'LOG_CONFIG_WARNING_CONSOLE_ONLY',
    'LOG_CONFIG_WARNING_FILE_ONLY',
    'LOG_CONFIG_WARNING',
    'LOG_CONFIG_ERROR_CONSOLE_ONLY',
    'LOG_CONFIG_ERROR_FILE_ONLY',
    'LOG_CONFIG_ERROR',
    'LOG_CONFIG_CRITICAL_CONSOLE_ONLY',
    'LOG_CONFIG_CRITICAL_FILE_ONLY',
    'LOG_CONFIG_CRITICAL',

    'TraceEnable',
    'ScopedLogEnable',
    'RuntimeTypeCheckEnable'
]

from .vimba import Vimba

from .camera import AccessMode, CameraChangeHandler, FrameHandler

from .interface import InterfaceChangeHandler

from .error import VimbaSystemError, VimbaCameraError, VimbaInterfaceError, VimbaFeatureError

from .feature import IntFeature, FloatFeature, StringFeature, BoolFeature, EnumFeature, \
                     CommandFeature, RawFeature

from .util import Log, LogLevel, LogConfig, LOG_CONFIG_TRACE_CONSOLE_ONLY, \
                  LOG_CONFIG_TRACE_FILE_ONLY, LOG_CONFIG_TRACE, LOG_CONFIG_INFO_CONSOLE_ONLY, \
                  LOG_CONFIG_INFO_FILE_ONLY, LOG_CONFIG_INFO, LOG_CONFIG_WARNING_CONSOLE_ONLY, \
                  LOG_CONFIG_WARNING_FILE_ONLY, LOG_CONFIG_WARNING, LOG_CONFIG_ERROR_CONSOLE_ONLY, \
                  LOG_CONFIG_ERROR_FILE_ONLY, LOG_CONFIG_ERROR, LOG_CONFIG_CRITICAL_CONSOLE_ONLY, \
                  LOG_CONFIG_CRITICAL_FILE_ONLY, LOG_CONFIG_CRITICAL, ScopedLogEnable, \
                  TraceEnable, RuntimeTypeCheckEnable
