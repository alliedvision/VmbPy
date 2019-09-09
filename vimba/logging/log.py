# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import os
import enum
import datetime
import logging


class LogLevel(enum.IntEnum):
    Trace = logging.DEBUG
    Info = logging.INFO
    Warning = logging.WARNING
    Error = logging.ERROR
    Critical = logging.CRITICAL

    def __str__(self):
        return self._name_

    def as_equal_len_str(self):
        return _LEVEL_TO_EQUAL_LEN_STR[self]


_LEVEL_TO_EQUAL_LEN_STR = {
    LogLevel.Trace: 'Trace   ',
    LogLevel.Info: 'Info    ',
    LogLevel.Warning: 'Warning ',
    LogLevel.Error: 'Error   ',
    LogLevel.Critical: 'Critical'
}


class LogConfig:
    _ENTRY_FORMAT = logging.Formatter('%(asctime)s | %(message)s')

    def __init__(self):
        self._handlers = []
        self._max_msg_length = None

    def add_file_log(self, level: LogLevel):
        log_ts = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = 'VimbaPython_{}_{}.log'.format(log_ts, str(level))
        log_file = os.path.join(os.getcwd(), log_file)

        handler = logging.FileHandler(log_file, delay=True)
        handler.setLevel(level)
        handler.setFormatter(LogConfig._ENTRY_FORMAT)

        self._handlers.append(handler)
        return self

    def add_console_log(self, level: LogLevel):
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(LogConfig._ENTRY_FORMAT)

        self._handlers.append(handler)
        return self

    def set_max_msg_length(self, max_msg_length):
        self._max_msg_length = max_msg_length

    def get_max_msg_length(self):
        return self._max_msg_length

    def get_handlers(self):
        return self._handlers


class Log:
    class _Impl:
        def __init__(self):
            self._logger = None
            self._config = None

        def __bool__(self):
            return bool(self._logger) and bool(self._config)

        def enable(self, config: LogConfig):
            self.disable()

            logger = logging.getLogger('VimbaPythonLog')
            logger.setLevel(logging.DEBUG)

            for handler in config.get_handlers():
                logger.addHandler(handler)

            self._config = config
            self._logger = logger

        def disable(self):
            if self._logger and self._config:
                for handler in self._config.get_handlers():
                    handler.close()
                    self._logger.removeHandler(handler)

                self._logger = None
                self._config = None

        def get_config(self):
            return self._config

        def trace(self, msg: str):
            if self._logger:
                self._logger.debug(self._build_msg(LogLevel.Trace, msg))

        def info(self, msg: str):
            if self._logger:
                self._logger.info(self._build_msg(LogLevel.Info, msg))

        def warning(self, msg: str):
            if self._logger:
                self._logger.warning(self._build_msg(LogLevel.Warning, msg))

        def error(self, msg: str):
            if self._logger:
                self._logger.error(self._build_msg(LogLevel.Error, msg))

        def critical(self, msg: str):
            if self._logger:
                self._logger.critical(self._build_msg(LogLevel.Critical, msg))

        def _build_msg(self, loglevel: LogLevel, msg: str):
            msg = '{} | {}'.format(loglevel.as_equal_len_str(), msg)
            max_len = self._config.get_max_msg_length()

            if max_len and (max_len < len(msg)):
                suffix = ' ...'
                msg = msg[:max_len - len(suffix)] + suffix

            return msg

    _instance = _Impl()

    @staticmethod
    def get_instance():
        return Log._instance


def _build_cfg(console_level, file_level):
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
