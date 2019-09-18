"""Scoped logging implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from functools import wraps
from typing import Any, Callable, Tuple, Optional
from .log import LogConfig, Log


__all__ = [
    'ScopedLogEnable'
]


class _ScopedLog:
    __log = Log.get_instance()

    def __init__(self, config: LogConfig):
        self.__config: LogConfig = config
        self.__old_config: Optional[LogConfig] = None

    def __enter__(self):
        self.__old_config = _ScopedLog.__log.get_config()
        _ScopedLog.__log.enable(self.__config)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.__old_config:
            _ScopedLog.__log.enable(self.__old_config)

        else:
            _ScopedLog.__log.disable()


class ScopedLogEnable:
    """Decorator: Enables Logging facility before execution of the wrapped function
    and disables logging after exiting the wrapped function. This allows more specific
    Logging of a code section compared to enabling/disabling the global logging mechanism.
    """
    def __init__(self, config: LogConfig):
        """Add scoped logging to a Callable.

        Arguments:
            config: The configuration the log should be enabled with.
        """
        self.__config = config

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args: Tuple[Any, ...]):
            with _ScopedLog(self.__config):
                return func(*args)

        return wrapper
