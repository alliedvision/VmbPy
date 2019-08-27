import unittest
from vimba.c_binding.util import load_vimba_raw

class CBindingUtilTest(unittest.TestCase):

    def assertMustNotRaise(self, func, *args):
        try:
            func(*args)

        except:  # noqa: E722b
            self.fail()

    def test_load_vimba(self):
        self.assertMustNotRaise(load_vimba_raw)

if __name__ == '__main__':
    import xmlrunner

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False,
        buffer=False,
        catchbreak=False)
