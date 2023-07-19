"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
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
import datetime
import logging
import os
from typing import List, Optional

from .vmb_enum import VmbIntEnum

__all__ = [
    'LogLevel',
    'LogConfig',
    'Log',
    'LOG_CONFIG_TRACE_CONSOLE_ONLY',
    'LOG_CONFIG_TRACE_FILE_ONLY',
    'LOG_CONFIG_TRACE',
    'LOG_CONFIG_DEBUG_CONSOLE_ONLY',
    'LOG_CONFIG_DEBUG_FILE_ONLY',
    'LOG_CONFIG_DEBUG',
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
    'LOG_CONFIG_CRITICAL'
]


class LogLevel(VmbIntEnum):
    """Enum containing all LogLevels."""
    Trace = logging.DEBUG - 5    #: Show Tracing information. Show all messages.
    Debug = logging.DEBUG        #: Show Debug, Informational, Warning, Error, and Critical Events.
    Info = logging.INFO          #: Show Informational, Warning, Error, and Critical Events.
    Warning = logging.WARNING    #: Show Warning, Error, and Critical Events.
    Error = logging.ERROR        #: Show Errors and Critical Events.
    Critical = logging.CRITICAL  #: Show Critical Events only.

    def __str__(self):
        return self._name_


class LogConfig:
    """The LogConfig is a builder to configure various specialized logging configurations.
    The constructed LogConfig must set via vmbpy.VmbSystem or the ScopedLogEnable Decorator
    to start logging.
    """

    def __init__(self):
        self.__handlers: List[logging.Handler] = []
        self.__max_msg_length: Optional[int] = None
        # Format for log output. The maximum message length must be filled via string formatting
        self.__entry_format = '%(asctime)s | %(message).{}s'

    def add_file_log(self, level: LogLevel) -> 'LogConfig':
        """Add a new Log file to the Config Builder.

        Arguments:
            level:
                LogLevel of the added log file.

        Returns:
            Reference to the LogConfig instance (builder pattern).
        """
        log_ts = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = 'vmbpy_{}_{}.log'.format(log_ts, str(level))
        log_file = os.path.join(os.getcwd(), log_file)

        handler = logging.FileHandler(log_file, delay=True)
        handler.setLevel(level)
        handler.setFormatter(self._get_formatter())

        self.__handlers.append(handler)
        return self

    def add_console_log(self, level: LogLevel) -> 'LogConfig':
        """Add a new Console Log to the Config Builder.

        Arguments:
            level:
                LogLevel of the added console log file.

        Returns:
            Reference to the LogConfig instance (builder pattern).
        """
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(self._get_formatter())

        self.__handlers.append(handler)
        return self

    def set_max_msg_length(self, max_msg_length: int):
        """Set max length of a log entry. Messages longer than this entry will be cut off."""
        self.__max_msg_length = max_msg_length

    def get_max_msg_length(self) -> Optional[int]:
        """Get configured max message length"""
        return self.__max_msg_length

    def get_handlers(self) -> List[logging.Handler]:
        """Get all configured log handlers"""
        return self.__handlers

    def _get_formatter(self) -> logging.Formatter:
        """Create and return a formatter for consistent log output"""
        return logging.Formatter(self.__entry_format.format(self.get_max_msg_length()))


class Log(logging.Logger):
    __instance = None

    def __init__(self, name: str) -> None:
        """Do not call directly. Use ``Log.get_instance()`` instead."""
        super().__init__(name)
        # Add a new `TRACE` level for tracing function enter/leave
        trace_name = LogLevel.Trace.name.upper()
        logging.addLevelName(LogLevel.Trace, trace_name)
        self.setLevel(LogLevel.Trace)

        # Do not output any logs by default. only if the user specifically enables them
        self.addHandler(logging.NullHandler())
        self.__config: Optional[LogConfig] = None

    @staticmethod
    def get_instance() -> 'Log':
        """Get Log instance."""
        if Log.__instance is None:
            # Use `logging.getLogger` so the logging manager handles the instance as expected. But
            # since the custom `Log` class should actually be used, temporarily change the class
            # that is used to instantiate new loggers.
            old_logging_class = logging.getLoggerClass()
            logging.setLoggerClass(Log)
            Log.__instance = logging.getLogger('vmbpyLog')
            logging.setLoggerClass(old_logging_class)
        return Log.__instance  # type: ignore

    def trace(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'TRACE' (custom level!).
        """
        if self.isEnabledFor(LogLevel.Trace):
            self._log(LogLevel.Trace, msg, args, **kwargs)

    def enable(self, config: LogConfig):
        # TODO: Validate if this is an appropriate implementation
        self.disable()
        for handler in config.get_handlers():
            self.addHandler(handler)
        self.__config = config

    def disable(self):
        for handler in list(self.handlers):
            if not isinstance(handler, logging.NullHandler):
                self.removeHandler(handler)
        self.__config = None

    def get_config(self) -> Optional[LogConfig]:
        """ Get log configuration

        Returns:
            Configuration if the log is enabled. In case the log is disabled return None.
        """
        return self.__config


def _build_cfg(console_level: Optional[LogLevel], file_level: Optional[LogLevel]) -> LogConfig:
    cfg = LogConfig()

    cfg.set_max_msg_length(200)

    if console_level:
        cfg.add_console_log(console_level)

    if file_level:
        cfg.add_file_log(file_level)

    return cfg


# Exported Default Log configurations.
LOG_CONFIG_TRACE_CONSOLE_ONLY = _build_cfg(LogLevel.Trace, None)
LOG_CONFIG_TRACE_FILE_ONLY = _build_cfg(None, LogLevel.Trace)
LOG_CONFIG_TRACE = _build_cfg(LogLevel.Trace, LogLevel.Trace)
LOG_CONFIG_DEBUG_CONSOLE_ONLY = _build_cfg(LogLevel.Debug, None)
LOG_CONFIG_DEBUG_FILE_ONLY = _build_cfg(None, LogLevel.Debug)
LOG_CONFIG_DEBUG = _build_cfg(LogLevel.Debug, LogLevel.Debug)
LOG_CONFIG_INFO_CONSOLE_ONLY = _build_cfg(LogLevel.Info, None)
LOG_CONFIG_INFO_FILE_ONLY = _build_cfg(None, LogLevel.Info)
LOG_CONFIG_INFO = _build_cfg(LogLevel.Info, LogLevel.Info)
LOG_CONFIG_WARNING_CONSOLE_ONLY = _build_cfg(LogLevel.Warning, None)
LOG_CONFIG_WARNING_FILE_ONLY = _build_cfg(None, LogLevel.Warning)
LOG_CONFIG_WARNING = _build_cfg(LogLevel.Warning, LogLevel.Warning)
LOG_CONFIG_ERROR_CONSOLE_ONLY = _build_cfg(LogLevel.Error, None)
LOG_CONFIG_ERROR_FILE_ONLY = _build_cfg(None, LogLevel.Error)
LOG_CONFIG_ERROR = _build_cfg(LogLevel.Error, LogLevel.Error)
LOG_CONFIG_CRITICAL_CONSOLE_ONLY = _build_cfg(LogLevel.Critical, None)
LOG_CONFIG_CRITICAL_FILE_ONLY = _build_cfg(None, LogLevel.Critical)
LOG_CONFIG_CRITICAL = _build_cfg(LogLevel.Critical, LogLevel.Critical)
