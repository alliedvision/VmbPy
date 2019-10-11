"""Runtime type checking.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import collections

from inspect import getfullargspec, isfunction, ismethod, signature
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

    def __verify_arg(self, type_hint: Any, arg_name: str):
        arg = self.__kwargs.get(arg_name)

        if (self.__matches(type_hint, arg)):
            return

        msg = '\'{}\' called with unexpected argument type.'
        msg += ' Argument\'{}\'.'
        msg += ' Expected type: {},'
        msg = msg.format(self.__func.__qualname__, arg_name, type_hint, type(arg))

        RuntimeTypeCheckEnable._log.error(msg)
        raise TypeError(msg)

    def __matches(self, type_hint: Any, arg: Any) -> bool:
        if self.__matches_base_types(type_hint, arg):
            return True

        if self.__matches_union_types(type_hint, arg):
            return True

        if self.__matches_tuple_types(type_hint, arg):
            return True

        return self.__matches_callable(type_hint, arg)

    def __matches_base_types(self, type_hint: Any, arg: Any) -> bool:
        return type_hint == type(arg)

    def __matches_union_types(self, type_hint: Any, arg: Any) -> bool:
        try:
            if not type_hint.__origin__ == Union:
                return False

        except AttributeError:
            return False

        return type(arg) in type_hint.__args__

    def __matches_tuple_types(self, type_hint: Any, arg: Any) -> bool:
        try:
            if not (type_hint.__origin__ == tuple and type(arg) == tuple):
                return False

        except AttributeError:
            return False

        if arg is ():
            return True

        if Ellipsis in type_hint.__args__:
            fn = self.__matches_var_length_tuple

        else:
            fn = self.__matches_fixed_size_tuple

        return fn(type_hint, arg)

    def __matches_fixed_size_tuple(self, type_hint: Any, arg: Any) -> bool:
        # To pass, the entire tuple must match in length and all types
        expand_hint = type_hint.__args__

        if len(expand_hint) != len(arg):
            return False

        for hint, value in zip(expand_hint, arg):
            if not self.__matches(hint, value):
                return False

        return True

    def __matches_var_length_tuple(self, type_hint: Any, arg: Any) -> bool:
        # To pass a tuple can be empty or all contents must match the given type.
        hint, _ = type_hint.__args__

        for value in arg:
            if not self.__matches(hint, value):
                return False

        return True

    def __matches_callable(self, type_hint: Any, arg: Any) -> bool:
        # Return if the given hint is no callable
        try:
            if not type_hint.__origin__ == collections.abc.Callable:
                return False

        except AttributeError:
            return False

        # Verify that are is some form of callable.:
        # 1) Check if it is either a function or a method
        # 2) If it is an object, check if it has a __call__ method. If so use call for checks.
        if not (isfunction(arg) or ismethod(arg)):

            try:
                fn = getattr(arg, '__call__')

            except AttributeError:
                return False

            arg = fn

        # Examine signature of given callable
        sig_args = list(signature(arg).parameters.values())
        hint_args = list(type_hint.__args__)
        hint_return = hint_args.pop()

        if len(sig_args) != len(hint_args):
            return False

        # TODO: Verify hints if they are specified
        #  print(sig_args)
        #  print(hint_args)
        #  print(hint_return)

        return True
