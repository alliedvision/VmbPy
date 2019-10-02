import unittest

from vimba import *
from vimba.frame import *

class TlFrameTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()

    def tearDown(self):
        pass

    def test_verify_buffer(self):
        """Expectation: A Frame buffer shall have exactly the specified size on
        construction.
        """
        self.assertEqual(Frame(0).get_buffer_size(), 0)
        self.assertEqual(Frame(1024).get_buffer_size(), 1024)
        self.assertEqual(Frame(1024 * 1024).get_buffer_size(), 1024 * 1024)

    def test_verify_no_copy_buffer_access(self):
        """Expectation: Accessing the internal buffer must not create a copy"""
        frame = Frame(10)
        self.assertEqual(id(frame._Frame__buffer), id(frame.get_buffer()))
