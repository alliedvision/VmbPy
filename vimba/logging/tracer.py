# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities

from functools import reduce
from .log import Log

_FMT_MSG_ENTRY = 'Enter         | {}'
_FMT_MSG_LEAVE = 'Leave(normal) | {}'
_FMT_MSG_RAISE = 'Leave(except) | {}, {}'
_FMT_ERROR = 'ErrorType: {}, ErrorValue: {}'
_INDENT_PER_LEVEL = '  '


class _Tracer:
    _log = Log.get_instance()
    _level = 0

    def __init__(self, expand_args, func, *args):
        self._full_name = '{}.{}'.format(func.__module__, func.__name__)
        self._full_args = _args_to_str(*args) if expand_args else '(...)'

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


def _args_to_str(*args):
    def fold(args_as_str, arg):
        return '{}{}, '.format(args_as_str, str(arg))

    args_str = reduce(fold, args, '')

    if not args_str:
        return '(None)'

    return '(' + args_str[:-2] + ')'


def _get_indent():
    return _INDENT_PER_LEVEL * _Tracer._level


def _create_enter_msg(name, args):
    msg = '{}{}{}'.format(_get_indent(), name, args)
    return _FMT_MSG_ENTRY.format(msg)


def _create_leave_msg(name):
    msg = '{}{}'.format(_get_indent(), name)
    return _FMT_MSG_LEAVE.format(msg)


def _create_raise_msg(name, exc_type, exc_value):
    msg = '{}{}'.format(_get_indent(), name)
    exc = _FMT_ERROR.format(exc_type, exc_value)
    return _FMT_MSG_RAISE.format(msg, exc)


class TraceEnable:
    def __init__(self, expand_args=True):
        self._expand_args = expand_args

    def __call__(self, func):
        def decorate(*args):
            if _Tracer._log:
                with _Tracer(self._expand_args, func, *args):
                    result = func(*args)

                return result

            else:
                return func(*args)

        return decorate
