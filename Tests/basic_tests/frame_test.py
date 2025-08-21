"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import copy
import os
import sys

from vmbpy import *
from vmbpy.c_binding import VmbFrameFlags

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class FrameTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deepcopy_empty_frame(self):
        f = Frame(10, allocation_mode=AllocationMode.AnnounceFrame)
        self.assertNoRaise(copy.deepcopy, f)

    def test_convert_pixel_format_empty_frame(self):
        f = Frame(10 * 10, allocation_mode=AllocationMode.AnnounceFrame)
        f._frame.pixelFormat = PixelFormat.Mono8
        f._frame.width = 10
        f._frame.height = 10
        self.assertNoRaise(f.convert_pixel_format, PixelFormat.Mono8)
        self.assertNoRaise(f.convert_pixel_format, PixelFormat.Rgb8)

    def test_as_numpy_array_empty_frame(self):
        f = Frame(10 * 10, allocation_mode=AllocationMode.AnnounceFrame)
        f._frame.pixelFormat = PixelFormat.Mono8
        f._frame.width = 10
        f._frame.height = 10
        self.assertNoRaise(f.as_numpy_ndarray)

    def test_repr_empty_frame(self):
        f = Frame(10, allocation_mode=AllocationMode.AnnounceFrame)
        self.assertNoRaise(repr, f)
        self.assertNoRaise(repr, f._frame)

class DeinterlaceFrameTest(VmbPyTestCase):
    @staticmethod
    def __get_frame(width: int, height: int, pixelformat: PixelFormat) -> Frame:
        """Helper function to create a dummy Frame instance with valid width, height, and pixel
        format"""
        f = Frame(width * height, allocation_mode=AllocationMode.AnnounceFrame)
        # Make sure all pixels have a value corresponding to their result image index
        f._frame.pixelFormat = pixelformat
        f._frame.width = width
        f._frame.height = height
        f._frame.receiveFlags |= VmbFrameFlags.Dimension
        return f

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deinterlace_frame_to_four_images(self):
        f = self.__get_frame(12, 12, PixelFormat.Mono8)
        arr = f.as_numpy_ndarray()
        arr[0::2, 0::2] = 0
        arr[0::2, 1::2] = 1
        arr[1::2, 0::2] = 2
        arr[1::2, 1::2] = 3
        # Resulting frame should look like this only bigger:
        # [[0, 1, 0, 1],
        #  [2, 3, 2, 3],
        #  [0, 1, 0, 1],
        #  [2, 3, 2, 3]]
        images = f.deinterlace_frame(((0, 1),
                                      (2, 3)))
        self.assertEqual(len(images), 4)
        for i, image in enumerate(images):
            self.assertEqual(image.get_width(), f.get_width() // 2)
            self.assertEqual(image.get_height(), f.get_height() // 2)
            # The sub-image at index i should only hold pixels with value i
            self.assertTrue((image.as_numpy_ndarray() == i).all())

    def test_deinterlace_frame_to_three_images(self):
        f = self.__get_frame(12, 12, PixelFormat.Mono8)
        arr = f.as_numpy_ndarray()
        arr[0::2, 0::2] = 0
        arr[0::2, 1::2] = 1
        arr[1::2, 0::2] = 1
        arr[1::2, 1::2] = 2
        # Resulting frame should look like this only bigger:
        # [[0, 1, 0, 1],
        #  [1, 2, 1, 2],
        #  [0, 1, 0, 1],
        #  [1, 2, 1, 2]]
        images = f.deinterlace_frame(((0, 1),
                                      (1, 2)))
        self.assertEqual(len(images), 3)
        for i, image in enumerate(images):
            self.assertEqual(image.get_width(), f.get_width() // 2)
            self.assertEqual(image.get_height(), f.get_height() // 2)
            # The sub-image at index i should only hold pixels with value i
            self.assertTrue((image.as_numpy_ndarray() == i).all())

    def test_deinterlace_frame_to_two_images(self):
        f = self.__get_frame(12, 12, PixelFormat.Mono8)
        arr = f.as_numpy_ndarray()
        arr[0::2, 0::2] = 0
        arr[0::2, 1::2] = 1
        arr[1::2, 0::2] = 1
        arr[1::2, 1::2] = 0
        # Resulting frame should look like this only bigger:
        # [[0, 1, 0, 1],
        #  [1, 0, 1, 0],
        #  [0, 1, 0, 1],
        #  [1, 0, 1, 0]]
        images = f.deinterlace_frame(((0, 1),
                                      (1, 0)))
        self.assertEqual(len(images), 2)
        for i, image in enumerate(images):
            self.assertEqual(image.get_width(), f.get_width() // 2)
            self.assertEqual(image.get_height(), f.get_height() // 2)
            # The sub-image at index i should only hold pixels with value i
            self.assertTrue((image.as_numpy_ndarray() == i).all())

    def test_deinterlace_frame_to_one_image(self):
        f = self.__get_frame(12, 12, PixelFormat.Mono8)
        arr = f.as_numpy_ndarray()
        arr[0::2, 0::2] = 0
        arr[0::2, 1::2] = 1
        arr[1::2, 0::2] = 1
        arr[1::2, 1::2] = 0
        # Resulting frame should look like this only bigger:
        # [[0, 1, 0, 1],
        #  [1, 0, 1, 0],
        #  [0, 1, 0, 1],
        #  [1, 0, 1, 0]]
        images = f.deinterlace_frame(((0, 1),
                                      (1, 0)))
        self.assertEqual(len(images), 2)
        for i, image in enumerate(images):
            self.assertEqual(image.get_width(), f.get_width() // 2)
            self.assertEqual(image.get_height(), f.get_height() // 2)
            # The sub-image at index i should only hold pixels with value i
            self.assertTrue((image.as_numpy_ndarray() == i).all())
