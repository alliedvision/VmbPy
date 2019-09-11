# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

from inspect import getfullargspec
from typing import get_type_hints, Any, Callable, Tuple


class RuntimeTypeCheckEnable:
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def decorate(*args: Tuple[Any, ...]):
            self.__dismantle_sig(func, *args)

            for name_hint, type_hint in self.__hints.items():
                self.__verify_arg(type_hint, name_hint)

            return_value = func(*args)

            self.__verify_result(return_value)

            return return_value

        return decorate

    def __dismantle_sig(self, func: Callable[..., Any], *args: Tuple[Any, ...]):
        self.__func = func
        self.__kwargs = dict(zip(getfullargspec(func)[0], args))
        self.__hints = get_type_hints(func)
        self.__return_type = self.__hints.pop('return', None)

    def __get_func_name(self) -> str:
        func = self.__func
        return '{}.{}'.format(func.__module__, func.__qualname__)

    def __verify_arg(self, expected: Any, arg_name: str):
        actual = type(self.__kwargs.get(arg_name))

        if expected == actual:
            return

        name = self.__get_func_name()
        err_msg = 'Function \'{}\'() called with unexpected argument type.'
        err_msg += ' Argument Name \'{}\'.'
        err_msg += ' Expected type: {},'
        err_msg += ' Actual type: {}'

        raise TypeError(err_msg.format(name, arg_name, expected, actual))

    def __verify_result(self, return_value: Any):
        expected = self.__return_type
        actual = type(return_value)

        if (not expected) or (expected == actual):
            return

        func_name = self.__get_func_name()
        err_msg = 'Function \'{}\' returns unexpected type.'
        err_msg += ' Expected type: {},'
        err_msg += ' Actual type: {}'

        raise TypeError(err_msg.format(func_name, expected, actual))
