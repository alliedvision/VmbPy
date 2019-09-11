# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from functools import reduce
from typing import Callable, Any, Tuple
from .log import Log

_FMT_MSG_ENTRY: str = 'Enter         | {}'
_FMT_MSG_LEAVE: str = 'Leave(normal) | {}'
_FMT_MSG_RAISE: str = 'Leave(except) | {}, {}'
_FMT_ERROR: str = 'ErrorType: {}, ErrorValue: {}'
_INDENT_PER_LEVEL: str = '  '


class _Tracer:
    _log: Log._Impl = Log.get_instance()
    _level: int = 0

    def __init__(self, expand_args: bool, func: Callable[..., Any], *args: Tuple[Any, ...]):
        self._full_name: str = '{}.{}'.format(func.__module__, func.__qualname__)
        self._full_args: str = _args_to_str(*args) if expand_args else '(...)'

    def __enter__(self):
        msg = _create_enter_msg(self._full_name, self._full_args)

        _Tracer._log.trace(msg)
        _Tracer._level += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _Tracer._level -= 1

        if exc_type:
            msg = _create_raise_msg(self._full_name, exc_type, exc_value)

        else:
            msg = _create_leave_msg(self._full_name)

        _Tracer._log.trace(msg)


def _args_to_str(*args) -> str:
    def fold(args_as_str: str, arg: Any):
        return '{}{}, '.format(args_as_str, str(arg))

    args_str = reduce(fold, args, '')

    if not args_str:
        return '(None)'

    return '({})'.format(args_str[:-2])


def _get_indent() -> str:
    return _INDENT_PER_LEVEL * _Tracer._level


def _create_enter_msg(name: str, args_str: str) -> str:
    msg = '{}{}{}'.format(_get_indent(), name, args_str)
    return _FMT_MSG_ENTRY.format(msg)


def _create_leave_msg(name: str) -> str:
    msg = '{}{}'.format(_get_indent(), name)
    return _FMT_MSG_LEAVE.format(msg)


def _create_raise_msg(name: str, exc_type: Exception, exc_value: str) -> str:
    msg = '{}{}'.format(_get_indent(), name)
    exc = _FMT_ERROR.format(exc_type, exc_value)
    return _FMT_MSG_RAISE.format(msg, exc)


class TraceEnable:
    def __init__(self, expand_args: bool = True):
        self._expand_args: bool = expand_args

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def decorate(*args: Tuple[Any, ...]):
            if _Tracer._log:
                with _Tracer(self._expand_args, func, *args):
                    result = func(*args)

                return result

            else:
                return func(*args)

        return decorate
