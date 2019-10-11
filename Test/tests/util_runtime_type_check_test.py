import unittest
from typing import Union, Optional, List, Tuple, Callable

from vimba.util import *

class RuntimeTypeCheckTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_func_mixed_args_kwargs_and_defaults(self):
        """Expectation: The typecheck must be able to deal with a valid mixture of args, kwargs
        and default values.
        """

        @RuntimeTypeCheckEnable()
        def test_func(a: int, b: str, c:float = 11.0/7.0):
            pass

        self.assertNoRaise(test_func, 1, '2', 0.0)
        self.assertNoRaise(test_func, c=0.0, b='str', a=1)
        self.assertNoRaise(test_func, 1, c=0.0, b='str')
        self.assertNoRaise(test_func, 1, b='str')
        self.assertNoRaise(test_func, 1, 'str')

        self.assertRaises(TypeError, test_func, c=0.0, b='str', a=0.0)
        self.assertRaises(TypeError, test_func, c='invalid type', b='str', a=0.0)

    def test_func_no_hints(self):
        """ Expectation: Functions without type hints
            should not throw any type errors
        """
        @RuntimeTypeCheckEnable()
        def test_func(arg1, arg2):
            return str()

        self.assertNoRaise(test_func, 'str', 0)

    def test_func_some_hints(self):
        """ Expectation: Type checks are only enforced on Arguments with hint.
            Argument without hints should be accepted
        """
        @RuntimeTypeCheckEnable()
        def test_func(arg1, arg2: int):
            return str()

        self.assertNoRaise(test_func, 'str', 0)
        self.assertNoRaise(test_func, 0.5, 0)
        self.assertRaises(TypeError, test_func, 'str', 0.0)


    def test_object(self):
        """ Expectation: The runtime checker must work on Objects just as on
            functions.
        """
        class TestObject:
            @RuntimeTypeCheckEnable()
            def __init__(self, arg1: str, arg2: int):
                pass

            @RuntimeTypeCheckEnable()
            def __call__(self, arg: str) -> str:
                return arg


        # Invalid construction
        self.assertRaises(TypeError, TestObject, 0.0, 0)

        obj = TestObject('str', 0)
        self.assertNoRaise(obj, 'arg')

        self.assertRaises(TypeError, obj, 0.0)

    def test_union(self):
        """ Expectation: int and string are valid parameters. Everything else must throw """
        @RuntimeTypeCheckEnable()
        def func(arg: Union[int, str]) -> Union[int, str]:
            return arg

        self.assertNoRaise(func, 0)
        self.assertNoRaise(func, 'str')
        self.assertRaises(TypeError, func, 0.0)


    def test_optional(self):
        """ Expectation: For optionals the check must accept the given type or None.
            Anything else must lead to an TypeError
        """

        @RuntimeTypeCheckEnable()
        def func(arg: Optional[int]) -> Optional[str]:
            return str(arg)

        self.assertNoRaise(func, 0)
        self.assertNoRaise(func, None)
        self.assertRaises(TypeError, func, 'str')

    def test_tuple(self):
        """ Expectation: Fixed size tuples checking must verify that size and type order is
            enforced.
        """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[int, str, float]) -> Tuple[float, int, str]:
            i, s, f = arg
            return (f, i, s)

        self.assertNoRaise(func, (1, 'str', 0.1))

        self.assertRaises(TypeError, func, (1, 'str'))
        self.assertRaises(TypeError, func, (1, 'str', 0.0, 'extra'))
        self.assertRaises(TypeError, func, ('str1', 'str', 0.0))

    def test_tuple_var_length(self):
        """ Expectation: Var length tuples checking must verify that contained type is enforced.
        """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[int, ...]) -> Tuple[str, ...]:
            return tuple([str(i) for i in arg])

        self.assertNoRaise(func, ())
        self.assertNoRaise(func, (1,))
        self.assertNoRaise(func, (1, 2, 3, 4, 5, 6))
        self.assertRaises(TypeError, func, ('str', ))
        self.assertRaises(TypeError, func, (1, 'str'))

    def test_tuple_empty(self):
        """ Empty Tuples must satisfy the requirements to Tuple types as argument and results """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[int, ...]) -> Tuple[int, ...]:
            return ()

        self.assertNoRaise(func, ())
        self.assertEqual(func(()), ())

    def test_tuple_union(self):
        """ Tuples of union types must be detected correctly """
        @RuntimeTypeCheckEnable()
        def func(arg: Tuple[Union[int, str], ...]):
            return arg

        self.assertNoRaise(func, (0,))
        self.assertNoRaise(func, ('1',))
        self.assertNoRaise(func, (2, 3))
        self.assertNoRaise(func, ('4', '5'))
        self.assertNoRaise(func, (6, '7'))
        self.assertNoRaise(func, ('8', 9))
        self.assertRaises(TypeError, func, (2, 0.0))

    def test_callable_no_func(self):
        """Expectation: The Callable verification shall fail if given Parameter is no callable."""
        @RuntimeTypeCheckEnable()
        def func(fn: Callable[[], None]):
            fn()

        #self.assertRaises(TypeError, func, 'no_callable')

    def test_callable_no_hints(self):
        """Expectation: A Callable without any hints must comply as long as the number of parameters
        matches to given hints. The Return Type doesn't matter if not given.
        """
        @RuntimeTypeCheckEnable()
        def func(fn: Callable[[str, float], int], arg1: str, arg2: float) -> int:
            return fn(arg1, arg2)

        def ok(arg1, arg2):
            return 0.0

        def err1(arg1):
            return 'str'

        def err2(arg1, arg2, arg3):
            return 23

        #self.assertNoRaise(func, ok, 'str', 0.0)
        #self.assertRaises(TypeError, func, err1, 'str', 0.0)
        #self.assertRaises(TypeError, func, err2, 'str', 0.0)

    def test_callable_obj(self):
        """Expectation: A Object that is callable must pass the runtime check
        """
        @RuntimeTypeCheckEnable()
        def func(fn: Callable[[str], None], arg: str) -> str:
            return fn(arg)

        class Ok:
            def __call__(self, arg: str) -> str:
                return str

        class Err1:
            def __call__(self) -> str:
                return 'Err1'

        class Err2:
            def __call__(self, arg1: str, arg2: str) -> str:
                return arg1 + arg2


        self.assertNoRaise(func, Ok(), 'str')
        self.assertRaises(TypeError, func, Err1(), 'str')
        self.assertRaises(TypeError, func, Err2(), 'str')
