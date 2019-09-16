"""Tracer implementation.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from functools import reduce, wraps
from typing import Callable, Any, Tuple
from .log import Log


__all__ = [
    'TraceEnable'
]


_FMT_MSG_ENTRY: str = 'Enter         | {}'
_FMT_MSG_LEAVE: str = 'Leave(normal) | {}'
_FMT_MSG_RAISE: str = 'Leave(except) | {}, {}'
_FMT_ERROR: str = 'ErrorType: {}, ErrorValue: {}'
_INDENT_PER_LEVEL: str = '  '


def _args_to_str(*args) -> str:
    def fold(args_as_str: str, arg: Any):
        return '{}{}, '.format(args_as_str, str(arg))

    args_str = reduce(fold, args, '')

    if not args_str:
        return '(None)'

    return '({})'.format(args_str[:-2])


def _get_indent(level: int) -> str:
    return _INDENT_PER_LEVEL * level


def _create_enter_msg(name: str, level: int, args_str: str) -> str:
    msg = '{}{}{}'.format(_get_indent(level), name, args_str)
    return _FMT_MSG_ENTRY.format(msg)


def _create_leave_msg(name: str, level: int, ) -> str:
    msg = '{}{}'.format(_get_indent(level), name)
    return _FMT_MSG_LEAVE.format(msg)


def _create_raise_msg(name: str, level: int,  exc_type: Exception, exc_value: str) -> str:
    msg = '{}{}'.format(_get_indent(level), name)
    exc = _FMT_ERROR.format(exc_type, exc_value)
    return _FMT_MSG_RAISE.format(msg, exc)


class _Tracer:
    __log = Log.get_instance()
    __level: int = 0

    @staticmethod
    def get_logger():
        return _Tracer.__log

    def __init__(self, expand_args: bool, func: Callable[..., Any], *args: Tuple[Any, ...]):
        self.__full_name: str = '{}.{}'.format(func.__module__, func.__qualname__)
        self.__full_args: str = _args_to_str(*args) if expand_args else '(...)'

    def __enter__(self):
        msg = _create_enter_msg(self.__full_name, _Tracer.__level, self.__full_args)

        _Tracer.__log.trace(msg)
        _Tracer.__level += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _Tracer.__level -= 1

        if exc_type:
            msg = _create_raise_msg(self.__full_name, _Tracer.__level, exc_type, exc_value)

        else:
            msg = _create_leave_msg(self.__full_name, _Tracer.__level)

        _Tracer.__log.trace(msg)


class TraceEnable:
    """Decorator: Adds a entry of LogLevel.Trace on entry and exit of the wrapped function.
    On Exit the Log entry contains information if the Function was left normally or with an
    Exception.
    """
    def __init__(self, expand_args: bool = True):
        """Add Tracing information to a Callable.

        Arguments:
            expand_args - If True the entire argument list is printed on execution. If False
                          (...) is printed instead.
        """
        self.__expand_args: bool = expand_args

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Tuple[Any, ...]):
            if _Tracer.get_logger():
                with _Tracer(self.__expand_args, func, *args):
                    result = func(*args)

                return result

            else:
                return func(*args)

        return wrapper
