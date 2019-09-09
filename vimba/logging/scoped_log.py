# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from .log import LogLevel, Log


class _ScopedLogger:
    _log = Log.get_instance()

    def __init__(self, loglevel: LogLevel):
        self._loglevel = loglevel

    def __enter__(self):
        _ScopedLogger._log.enable(self._loglevel)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _ScopedLogger._log.disable()


def scoped_log_enable(loglevel: LogLevel):
    def decorate(func):
        def wrapper(*args):
            with _ScopedLogger(loglevel):
                return func(*args)
        return wrapper
    return decorate
