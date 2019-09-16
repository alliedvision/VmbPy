import unittest
from typing import Union, Optional, List, Tuple, Callable
from vimba import RuntimeTypeCheckEnable

class RuntimeTypeCheckTest(unittest.TestCase):
    def test_func_no_hints_no_return(self):
        """ Expectation: Functions without type hints
            should not throw any type errors
        """
        @RuntimeTypeCheckEnable()
        def test_func(arg1, arg2):
            return str()

        try:
            test_func('str', 0)

        except:
            self.fail('Previous call must not raise')


    def test_func_no_hints_and_return(self):
        """ Expectation: Functions with a return hint must enforce it. """
        @RuntimeTypeCheckEnable()
        def test_func_valid(arg1, arg2) -> str:
            return str()

        try:
            test_func_valid('str', 0)

        except:
            self.fail('Previous call must not raise.')

        @RuntimeTypeCheckEnable()
        def test_func_invalid(arg1, arg2) -> str:
            return int()

        try:
            test_func_invalid('str', 0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

    def test_func_some_hints_no_return(self):
        """ Expectation: Type checks are only enforced on Arguments with hint.
            Argument without hints should be accepted
        """
        @RuntimeTypeCheckEnable()
        def test_func(arg1, arg2: int):
            return str()

        try:
            test_func('str', 0)
            test_func(0.5, 0)

        except:
            self.fail('Previous call must not raise.')

        try:
            test_func('str', 0.0)
            self.fail('Previous call must not raise.')

        except TypeError:
            pass


    def test_func_some_hints_and_return(self):
        """ Expectation: Type checks are only enforced on Arguments with hint.
            Argument without hints should be accepted. Additionally
            Return types must be checked if specified.
        """

        @RuntimeTypeCheckEnable()
        def test_func_valid(arg1: str, arg2) -> str:
            return 'str'

        @RuntimeTypeCheckEnable()
        def test_func_invalid(arg1: str, arg2) -> int:
            return 'str'

        try:
            test_func_valid('str', 0)

        except:
            self.fail('Previous call must not raise.')

        try:
            test_func_valid(0, 0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

        try:
            test_func_invalid('str', 0.0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

    def test_object(self):
        """ Expectation: The runtime checker must work on Objects just as on
            functions.
        """
        class TestObject:
            @RuntimeTypeCheckEnable()
            def __init__(self, arg1: str, arg2: int):
                pass

            @RuntimeTypeCheckEnable()
            def ok(self, arg: str) -> str:
                return arg

            @RuntimeTypeCheckEnable()
            def err(self, arg: str) -> int:
                return arg

        # Valid usage
        obj = TestObject('str', 0)
        obj.ok('arg')

        # Invalid usage
        try:
            TestObject(0.0, 0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

        try:
            obj.ok(0.0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

        try:
            obj.err('str')
            self.fail('Previous call must raise.')

        except TypeError:
            pass

        try:
            obj.err(0)
            self.fail('Previous call must raise.')

        except TypeError:
            pass

    def test_union(self):
        """ Expectation: int and string are valid parameters. Everything else must throw """
        @RuntimeTypeCheckEnable()
        def func(arg: Union[int, str]) -> Union[int, str]:
            return arg

        try:
            func(0)

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func('str')

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func(0.0)
            self.fail('Previous call must raise')
        except TypeError:
            pass


    def test_optional(self):
        """ Expectation: For optionals the check must accept the given type or None.
            Anything else must lead to an TypeError
        """

        @RuntimeTypeCheckEnable()
        def func(arg: Optional[int]) -> Optional[str]:
            return str(arg)

        try:
            func(0)

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func(None)

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func('str')
            self.fail('Previous call must raise')

        except TypeError:
            pass

    def test_tuple(self):
        """ Expectation: Fixed size tuples checking must verify that size and type order is
            enforced.
        """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[int, str, float]) -> Tuple[float, int, str]:
            i, s, f = arg
            return (f, i, s)

        try:
            func((1, 'str', 0.1))

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func((1, 'str'))
            self.fail('Previous call must raise')

        except TypeError:
            pass

        try:
            func((1, 'str', 0.0, 'extra'))
            self.fail('Previous call must raise')

        except TypeError:
            pass

        try:
            func(('str1', 'str', 0.0))
            self.fail('Previous call must raise')

        except TypeError:
            pass

    def test_tuple_var_length(self):
        """ Expectation: Var length tuples checking must verify that contained type is enforced.
        """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[int, ...]) -> Tuple[str, ...]:
            return tuple([str(i) for i in arg])

        try:
            func(())

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func((1,))

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func((1, 2, 3, 4, 5, 6))

        except TypeError:
            self.fail('Previous call must not raise')

        try:
            func(('str'))
            self.fail('Previous call must raise')

        except TypeError:
            pass

        try:
            func((1, 'str'))
            self.fail('Previous call must raise')

        except TypeError:
            pass
