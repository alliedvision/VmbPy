import unittest
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
