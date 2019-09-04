# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

import logging
import enum

from functools import reduce


class LogLevel(enum.IntEnum):
    Trace = logging.DEBUG
    Info = logging.INFO
    Warning = logging.WARNING
    Error = logging.ERROR
    Critical = logging.CRITICAL

    def as_equal_len_str(self):
        level = self.value

        if level == LogLevel.Trace:
            return 'Trace   '

        elif level == LogLevel.Info:
            return 'Info    '

        elif level == LogLevel.Warning:
            return 'Warning '

        elif level == LogLevel.Error:
            return 'Error   '

        elif level == LogLevel.Critical:
            return 'Critical'


class Log:
    class _Impl:
        def __init__(self):
            self._logger = None

        def __bool__(self):
            return True if self._logger else False

        def enable(self, loglevel: LogLevel):
            if not self._logger:
                fmt = logging.Formatter('%(asctime)s | %(message)s')

                console = logging.StreamHandler()
                console.setLevel(loglevel)
                console.setFormatter(fmt)

                self._logger = logging.getLogger()
                self._logger.setLevel(loglevel)
                self._logger.addHandler(console)

        def disable(self):
            if self._logger:
                self._logger = None

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
            return u'{} | {}'.format(loglevel.as_equal_len_str(), msg)

    _instance = _Impl()

    @staticmethod
    def get_instance():
        return Log._instance


class _ScopedLogger:
    _log = Log.get_instance()

    def __init__(self, loglevel: LogLevel):
        self._loglevel = loglevel

    def __enter__(self):
        _ScopedLogger._log.enable(self._loglevel)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _ScopedLogger._log.disable()


class _Tracer:
    _FMT_MSG_ENTRY = 'Enter         | {}'
    _FMT_MSG_LEAVE = 'Leave(normal) | {}'
    _FMT_MSG_RAISE = 'Leave(except) | {}, {}'
    _FMT_ERROR = 'Error: {}, ErrorValue: {}'
    _INDENT_PER_LEVEL = '  '

    _log = Log.get_instance()
    _level = 0

    @staticmethod
    def _get_indent():
        return _Tracer._INDENT_PER_LEVEL * _Tracer._level

    @staticmethod
    def _stringify_args(*args):
        def fold(args_as_str, arg):
            return '{}{}, '.format(args_as_str, str(arg))

        return reduce(fold, args, '(')[:-2] + ')'

    @staticmethod
    def _create_enter_msg(sig):
        msg = '{}{}'.format(_Tracer._get_indent(), sig)
        return _Tracer._FMT_MSG_ENTRY.format(msg)

    @staticmethod
    def _create_leave_msg(sig):
        msg = '{}{}'.format(_Tracer._get_indent(), sig)
        return _Tracer._FMT_MSG_LEAVE.format(msg)

    @staticmethod
    def _create_raise_msg(sig, exc_type, exc_value):
        msg = '{}{}'.format(_Tracer._get_indent(), sig)
        exc = _Tracer._FMT_ERROR.format(exc_type, exc_value)
        return _Tracer._FMT_MSG_RAISE.format(msg, exc)

    def __init__(self, log_args, func, *args):
        full_name = '{}.{}'.format(func.__module__, func.__name__)
        full_args = _Tracer._stringify_args(*args) if log_args else '(...)'

        self._sig = '{}{}'.format(full_name, full_args)

    def __enter__(self):
        _Tracer._log.trace(_Tracer._create_enter_msg(self._sig))
        _Tracer._level += 1
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _Tracer._level -= 1

        if exc_type:
            _Tracer._log.trace(_Tracer._create_raise_msg(self._sig, exc_type,
                                                         exc_value))

        else:
            _Tracer._log.trace(_Tracer._create_leave_msg(self._sig))


def scoped_log_enable(loglevel: LogLevel):
    def decorate(func):
        def wrapper(*args):
            with _ScopedLogger(loglevel):
                return func(*args)
        return wrapper
    return decorate


def trace_enable(log_args=True):
    def decorate(func):
        def wrapper(*args):
            if _Tracer._log:
                with _Tracer(log_args, func, *args):
                    return func(*args)

            else:
                return func(*args)

        return wrapper
    return decorate
