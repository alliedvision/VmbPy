import unittest
import copy
import ctypes

from vimba import *
from vimba.frame import *

class TlFrameTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()
        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')

    def tearDown(self):
        self.vimba._shutdown()

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
        self.assertEqual(id(frame._buffer), id(frame.get_buffer()))

    def test_get_id(self):
        """Expectation: get_id() must return None if Its locally constructed
        else it must return the frame id.
        """

        self.assertIsNone(Frame(0).get_id())

        with self.cam:
            self.assertIsNotNone(self.cam.get_frame().get_id())

    def test_get_timestamp(self):
        """Expectation: get_timestamp() must return None if Its locally constructed
        else it must return the timestamp.
        """

        self.assertIsNone(Frame(0).get_timestamp())

        with self.cam:
            self.assertIsNotNone(self.cam.get_frame().get_timestamp())

    def test_get_offset(self):
        """Expectation: get_offset_x() must return None if Its locally constructed
        else it must return the offset as int. Same goes for get_offset_y()
        """

        self.assertIsNone(Frame(0).get_offset_x())
        self.assertIsNone(Frame(0).get_offset_y())

    def test_get_dimension(self):
        """Expectation: get_width() must return None if Its locally constructed
        else it must return the offset as int. Same goes for get_height()
        """

        self.assertIsNone(Frame(0).get_width())
        self.assertIsNone(Frame(0).get_height())

        with self.cam:
            self.assertIsNotNone(self.cam.get_frame().get_width())
            self.assertIsNotNone(self.cam.get_frame().get_height())

    def test_get_image_size(self):
        """Expectation: get_image_size() must return 0 if locally constructed
        else it must return the image_size as int.
        """

        self.assertEquals(Frame(0).get_image_size(), 0)

        with self.cam:
            self.assertNotEquals(self.cam.get_frame().get_image_size(), 0)

    def test_deepcopy(self):
        """Expectation: a deepcopy must clone the frame buffer with its contents an
        update the internally store pointer in VmbFrame struct.
        """
        with self.cam:
            frame = self.cam.get_frame()


        frame_cpy = copy.deepcopy(frame)

        # Ensure frames and their members are not the same object
        self.assertNotEquals(id(frame), id(frame_cpy))
        self.assertNotEquals(id(frame._buffer), id(frame_cpy._buffer))
        self.assertNotEquals(id(frame._frame), id(frame_cpy._frame))

        # Ensure that both buffers have the same size and contain the same data.
        self.assertEquals(frame.get_buffer_size(), frame_cpy.get_buffer_size())
        self.assertEquals(frame.get_buffer().raw, frame_cpy.get_buffer().raw)

        # Ensure that internal Frame Pointer points to correct buffer.
        self.assertEquals(frame._frame.buffer,
                          ctypes.cast(frame._buffer, ctypes.c_void_p).value)

        self.assertEquals(frame_cpy._frame.buffer,
                          ctypes.cast(frame_cpy._buffer, ctypes.c_void_p).value)

        self.assertEquals(frame._frame.bufferSize, frame_cpy._frame.bufferSize)

    def test_get_pixel_format(self):
        """Expectation: Frames have an image format set after acquisition"""
        with self.cam:
            self.assertNotEquals(self.cam.get_frame().get_pixel_format(), 0)

    def test_incompatible_formats_value_error(self):
        """Expectation: Conversion into incompatible formats must lead to an value error """
        with self.cam:
            frame = self.cam.get_frame()

        convertable_fmt = frame.get_pixel_format().get_convertible_formats()
        for fmt in VimbaPixelFormat.__members__.values():
            if fmt not in convertable_fmt:
                self.assertRaises(ValueError, frame.convert_pixel_format, fmt)


    def test_convert_to_all_given_formats(self):
        """Expectation: A Series of Frame, each acquired with a different Pixel format
        Must be convertible to all formats the given format claims its convertible to without any
        errors.
        """
        test_frames = []

        with self.cam:
            pixel_format = self.cam.get_feature_by_name('PixelFormat')

            for fmt in pixel_format.get_available_entries():
                pixel_format.set(fmt)

                test_frames.append(self.cam.get_frame())


        for frame in test_frames:

            # The test shall work on a copy to keep the original Frame untouched
            cpy_frame = copy.deepcopy(frame)

            for expected_fmt in frame.get_pixel_format().get_convertible_formats():
                cpy_frame.convert_pixel_format(expected_fmt)

                self.assertEquals(expected_fmt, cpy_frame.get_pixel_format())


