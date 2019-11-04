"""VimbaPython top level module.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__version__ = '0.0.1'

__all__ = [
    'Vimba',
    'Camera',
    'CameraChangeHandler',
    'CameraEvent',
    'AccessMode',
    'PersistType',
    'Interface',
    'InterfaceChangeHandler',
    'InterfaceEvent',
    'VimbaPixelFormat',
    'Frame',
    'FrameHandler',
    'Debayer',
    'intersect_pixel_formats',
    'MONO_PIXEL_FORMATS',
    'BAYER_PIXEL_FORMATS',
    'RGB_PIXEL_FORMATS',
    'RGBA_PIXEL_FORMATS',
    'BGR_PIXEL_FORMATS',
    'BGRA_PIXEL_FORMATS',
    'YUV_PIXEL_FORMATS',
    'YCBCR_PIXEL_FORMATS',
    'COLOR_PIXEL_FORMATS',
    'OPENCV_PIXEL_FORMATS',

    'VimbaSystemError',
    'VimbaCameraError',
    'VimbaInterfaceError',
    'VimbaFeatureError',
    'VimbaTimeout',

    'IntFeature',
    'FloatFeature',
    'StringFeature',
    'BoolFeature',
    'EnumEntry',
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

from .camera import AccessMode, PersistType, Camera, CameraChangeHandler, CameraEvent, FrameHandler

from .interface import Interface, InterfaceChangeHandler, InterfaceEvent

from .frame import VimbaPixelFormat, Frame, Debayer, intersect_pixel_formats, MONO_PIXEL_FORMATS, \
                   BAYER_PIXEL_FORMATS, RGB_PIXEL_FORMATS, RGBA_PIXEL_FORMATS, BGR_PIXEL_FORMATS, \
                   BGRA_PIXEL_FORMATS, YUV_PIXEL_FORMATS, YCBCR_PIXEL_FORMATS, \
                   COLOR_PIXEL_FORMATS, OPENCV_PIXEL_FORMATS

from .error import VimbaSystemError, VimbaCameraError, VimbaInterfaceError, VimbaFeatureError, \
                   VimbaTimeout

from .feature import IntFeature, FloatFeature, StringFeature, BoolFeature, EnumEntry, EnumFeature, \
                     CommandFeature, RawFeature

from .util import Log, LogLevel, LogConfig, LOG_CONFIG_TRACE_CONSOLE_ONLY, \
                  LOG_CONFIG_TRACE_FILE_ONLY, LOG_CONFIG_TRACE, LOG_CONFIG_INFO_CONSOLE_ONLY, \
                  LOG_CONFIG_INFO_FILE_ONLY, LOG_CONFIG_INFO, LOG_CONFIG_WARNING_CONSOLE_ONLY, \
                  LOG_CONFIG_WARNING_FILE_ONLY, LOG_CONFIG_WARNING, LOG_CONFIG_ERROR_CONSOLE_ONLY, \
                  LOG_CONFIG_ERROR_FILE_ONLY, LOG_CONFIG_ERROR, LOG_CONFIG_CRITICAL_CONSOLE_ONLY, \
                  LOG_CONFIG_CRITICAL_FILE_ONLY, LOG_CONFIG_CRITICAL, ScopedLogEnable, \
                  TraceEnable, RuntimeTypeCheckEnable
