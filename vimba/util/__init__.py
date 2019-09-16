"""Submodule containing all utility classes.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

# Suppress 'imported but unused' - Error from static style checker.
# flake8: noqa: F401

__all__ = [
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

    # Decorators
    'TraceEnable',
    'ScopedLogEnable',
    'RuntimeTypeCheckEnable'
]

from .log import Log, LogLevel, LogConfig, LOG_CONFIG_TRACE_CONSOLE_ONLY, \
                 LOG_CONFIG_TRACE_FILE_ONLY, LOG_CONFIG_TRACE, LOG_CONFIG_INFO_CONSOLE_ONLY, \
                 LOG_CONFIG_INFO_FILE_ONLY, LOG_CONFIG_INFO, LOG_CONFIG_WARNING_CONSOLE_ONLY, \
                 LOG_CONFIG_WARNING_FILE_ONLY, LOG_CONFIG_WARNING, LOG_CONFIG_ERROR_CONSOLE_ONLY, \
                 LOG_CONFIG_ERROR_FILE_ONLY, LOG_CONFIG_ERROR, LOG_CONFIG_CRITICAL_CONSOLE_ONLY, \
                 LOG_CONFIG_CRITICAL_FILE_ONLY, LOG_CONFIG_CRITICAL

from .tracer import TraceEnable
from .scoped_log import ScopedLogEnable
from .runtime_type_check import RuntimeTypeCheckEnable
