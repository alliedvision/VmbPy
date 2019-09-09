# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from .log import LogConfig, Log


class _ScopedLog:
    _log = Log.get_instance()

    def __init__(self, config: LogConfig):
        self._config = config

    def __enter__(self):
        _ScopedLog._log.enable(self._config)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _ScopedLog._log.disable()


class ScopedLogEnable:
    def __init__(self, config):
        self._config = config

    def __call__(self, func):
        def decorate(*args):
            with _ScopedLog(self._config):
                return func(*args)

        return decorate
