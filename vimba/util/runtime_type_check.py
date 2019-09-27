"""Runtime type checking.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from inspect import getfullargspec
from functools import wraps
from typing import get_type_hints, Any, Callable, Tuple, Union
from .log import Log


__all__ = [
    'RuntimeTypeCheckEnable'
]


class RuntimeTypeCheckEnable:
    """ Decorator adding runtime Type checking to the Wrapped Callable.

    Each time the callable is executed, all arguments checked if they match with the given
    Typehints. If all checks are passed, the wrapped function will be executed, if the given
    Arguments to not match a TypeError is raised.
    Note: This Decorator is no replacement for a feature complete TypeChecker supports only
    a subset of all Types expressible by Typehints.

    """
    _log = Log.get_instance()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Tuple[Any, ...]):
            self.__dismantle_sig(func, *args)

            for name_hint, type_hint in self.__hints.items():
                self.__verify_arg(type_hint, name_hint)

            return func(*args)

        return wrapper

    def __dismantle_sig(self, func: Callable[..., Any], *args: Tuple[Any, ...]):
        self.__func = func
        self.__kwargs = dict(zip(getfullargspec(func)[0], args))
        self.__hints = get_type_hints(func)
        self.__return_type = self.__hints.pop('return', None)

    def __verify_arg(self, expected: Any, arg_name: str):
        arg = self.__kwargs.get(arg_name)
        actual = type(arg)

        if (self.__matches_base_types(expected, actual) or
                self.__matches_union_types(expected, actual) or
                self.__matches_tuple_types(expected, actual, arg)):
            return

        msg = '\'{}\' called with unexpected argument type.'
        msg += ' Argument\'{}\'.'
        msg += ' Expected type: {},'
        msg += ' Actual type: {}'
        msg = msg.format(self.__func.__qualname__, arg_name, expected, actual)

        RuntimeTypeCheckEnable._log.error(msg)
        raise TypeError(msg)

    def __matches_base_types(self, expected: Any, actual: Any) -> bool:
        return expected == actual

    def __matches_union_types(self, expected: Any, actual: Any) -> bool:
        try:
            if not expected.__origin__ == Union:
                return False

        except AttributeError:
            return False

        if actual in expected.__args__:
            return True

        else:
            return False

    def __matches_tuple_types(self, expected: Any, actual: Any, arg_tuple: Any) -> bool:
        try:
            if not (expected.__origin__ == tuple and actual == tuple):
                return False

        except AttributeError:
            return False

        if arg_tuple is ():
            return True

        if Ellipsis in expected.__args__:
            return self.__matches_var_length_tuple(expected.__args__, arg_tuple)

        else:
            return self.__matches_fixed_size_tuple(expected.__args__, arg_tuple)

    def __matches_fixed_size_tuple(self, expected_tuple_types: Any, arg_tuple: Any) -> bool:
        # To pass, the entire tuple must match in length and all types
        if len(expected_tuple_types) != len(arg_tuple):
            return False

        for expected_type, arg in zip(expected_tuple_types, arg_tuple):
            if not expected_type == type(arg):
                return False

        return True

    def __matches_var_length_tuple(self, expected_types: Any, arg_tuple: Any) -> bool:
        # To pass a tuple can be empty or all contents must match the given type.
        expected_type, _ = expected_types

        for arg in arg_tuple:
            if not expected_type == type(arg):
                return False

        return True
