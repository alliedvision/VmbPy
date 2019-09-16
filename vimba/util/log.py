# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import os
import enum
import datetime
import logging

from typing import List, Optional


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
    'LOG_CONFIG_CRITICAL'
]


class LogLevel(enum.IntEnum):
    Trace = logging.DEBUG
    Info = logging.INFO
    Warning = logging.WARNING
    Error = logging.ERROR
    Critical = logging.CRITICAL

    def __str__(self):
        return self._name_

    def as_equal_len_str(self) -> str:
        return _LEVEL_TO_EQUAL_LEN_STR[self]


_LEVEL_TO_EQUAL_LEN_STR = {
    LogLevel.Trace: 'Trace   ',
    LogLevel.Info: 'Info    ',
    LogLevel.Warning: 'Warning ',
    LogLevel.Error: 'Error   ',
    LogLevel.Critical: 'Critical'
}


class LogConfig:
    __ENTRY_FORMAT = logging.Formatter('%(asctime)s | %(message)s')

    def __init__(self):
        self.__handlers: List[logging.Handler] = []
        self.__max_msg_length: Optional[int] = None

    def add_file_log(self, level: LogLevel) -> 'LogConfig':
        log_ts = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = 'VimbaPython_{}_{}.log'.format(log_ts, str(level))
        log_file = os.path.join(os.getcwd(), log_file)

        handler = logging.FileHandler(log_file, delay=True)
        handler.setLevel(level)
        handler.setFormatter(LogConfig.__ENTRY_FORMAT)

        self.__handlers.append(handler)
        return self

    def add_console_log(self, level: LogLevel) -> 'LogConfig':
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(LogConfig.__ENTRY_FORMAT)

        self.__handlers.append(handler)
        return self

    def set_max_msg_length(self, max_msg_length: int):
        self.__max_msg_length = max_msg_length

    def get_max_msg_length(self) -> Optional[int]:
        return self.__max_msg_length

    def get_handlers(self) -> List[logging.Handler]:
        return self.__handlers


class Log:
    class __Impl:
        def __init__(self):
            self.__logger: Optional[logging.Logger] = None
            self.__config: Optional[LogConfig] = None

        def __bool__(self):
            return bool(self.__logger) and bool(self.__config)

        def enable(self, config: LogConfig):
            self.disable()

            logger = logging.getLogger('VimbaPythonLog')
            logger.setLevel(logging.DEBUG)

            for handler in config.get_handlers():
                logger.addHandler(handler)

            self.__config = config
            self.__logger = logger

        def disable(self):
            if self.__logger and self.__config:
                for handler in self.__config.get_handlers():
                    handler.close()
                    self.__logger.removeHandler(handler)

                self.__logger = None
                self.__config = None

        def get_config(self) -> Optional[LogConfig]:
            return self.__config

        def trace(self, msg: str):
            if self.__logger:
                self.__logger.debug(self.__build_msg(LogLevel.Trace, msg))

        def info(self, msg: str):
            if self.__logger:
                self.__logger.info(self.__build_msg(LogLevel.Info, msg))

        def warning(self, msg: str):
            if self.__logger:
                self.__logger.warning(self.__build_msg(LogLevel.Warning, msg))

        def error(self, msg: str):
            if self.__logger:
                self.__logger.error(self.__build_msg(LogLevel.Error, msg))

        def critical(self, msg: str):
            if self.__logger:
                self.__logger.critical(self.__build_msg(LogLevel.Critical, msg))

        def __build_msg(self, loglevel: LogLevel, msg: str) -> str:
            msg = '{} | {}'.format(loglevel.as_equal_len_str(), msg)
            max_len = self.__config.get_max_msg_length() if self.__config else None

            if max_len and (max_len < len(msg)):
                suffix = ' ...'
                msg = msg[:max_len - len(suffix)] + suffix

            return msg

    __instance = __Impl()

    @staticmethod
    def get_instance() -> '__Impl':
        return Log.__instance


def _build_cfg(console_level: Optional[LogLevel], file_level: Optional[LogLevel]) -> LogConfig:
    cfg = LogConfig()

    cfg.set_max_msg_length(200)

    if console_level:
        cfg.add_console_log(console_level)

    if file_level:
        cfg.add_file_log(file_level)

    return cfg


LOG_CONFIG_TRACE_CONSOLE_ONLY = _build_cfg(LogLevel.Trace, None)
LOG_CONFIG_TRACE_FILE_ONLY = _build_cfg(None, LogLevel.Trace)
LOG_CONFIG_TRACE = _build_cfg(LogLevel.Trace, LogLevel.Trace)
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
