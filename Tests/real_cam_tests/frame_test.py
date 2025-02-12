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
import ctypes
import os
import sys

from vmbpy import *
from vmbpy.frame import *

try:
    import numpy as np
except ImportError:
    np = None

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase, set_throughput_to_fraction, reset_roi


class CamFrameTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        # prevent camera sending completely black frames
        with self.cam as cam:
            _, max_exposure_time = cam.ExposureTime.get_range()
            new_exposure_time = min(100000, max_exposure_time)
            self._old_exposure_time = cam.ExposureTime.get()
            cam.ExposureTime.set(new_exposure_time)
            # Determine how long our get_frame timeout should be so we do not run into timeout
            # issues with the long exposure time. SFNC defines that ExposureTime feature gives time
            # in us. get_frame expects timeout duration in ms. Timeout is at least three seconds or
            # calculated based on exposure time.
            self.frame_timeout_ms = max(3000, int(1.5 * new_exposure_time * 1e-3))
            _, max_gain = cam.Gain.get_range()
            self._old_gain = cam.Gain.get()
            cam.Gain.set(max_gain)
            try:
                set_throughput_to_fraction(self.cam, 0.8)
                self.cam.DeviceLinkThroughputLimitMode.set("On")
                reset_roi(cam, 64)
            except AttributeError:
                pass

    def tearDown(self):
        # Reset ExposureTime and Gain to values that were set before this class was executed
        with self.cam as cam:
            cam.ExposureTime.set(self._old_exposure_time)
            cam.Gain.set(self._old_gain)
            try:
                self.cam.DeviceLinkThroughputLimitMode.set("Off")
                reset_roi(self.cam)
            except AttributeError:
                pass
        self.vmb._shutdown()

    def test_verify_buffer(self):
        # Expectation: A Frame buffer shall have exactly the specified size on construction.
        # Allocation is performed by vmbpy
        self.assertEqual(Frame(0, AllocationMode.AnnounceFrame).get_buffer_size(), 0)
        self.assertEqual(Frame(1024, AllocationMode.AnnounceFrame).get_buffer_size(), 1024)
        self.assertEqual(Frame(1024 * 1024, AllocationMode.AnnounceFrame).get_buffer_size(),
                         1024 * 1024)

    def test_verify_no_copy_empty_buffer_access(self):
        # Expectation: Accessing the internal buffer must not create a copy
        # frame._buffer is only set on construction if buffer is allocated by vmbpy
        frame = Frame(10, AllocationMode.AnnounceFrame)
        self.assertEqual(id(frame._buffer), id(frame.get_buffer()))

    def test_verify_no_copy_filled_buffer_access(self):
        # Expectation: Accessing the internal buffer must not create a copy
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                with self.cam:
                    frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                               allocation_mode=allocation_mode)
                self.assertEqual(id(frame._buffer), id(frame.get_buffer()))

    def test_get_id(self):
        # Expectation: get_id() must return None if it is locally constructed
        # else it must return the frame id.
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                self.assertIsNone(Frame(0, allocation_mode).get_id())

                with self.cam:
                    self.assertIsNotNone(
                        self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                           allocation_mode=allocation_mode).get_id())

    def test_get_timestamp(self):
        # Expectation: get_timestamp() must return None if it is locally constructed
        # else it must return the timestamp.
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                self.assertIsNone(Frame(0, allocation_mode).get_timestamp())

                with self.cam:
                    self.assertIsNotNone(
                        self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                           allocation_mode=allocation_mode).get_timestamp())

    def test_get_payload_type(self):
        # Expectation: get_payload_type() must return None if it is locally constructed
        # else it must return the payload type.
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                self.assertIsNone(Frame(0, allocation_mode).get_payload_type())

                with self.cam:
                    self.assertIsNotNone(
                        self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                           allocation_mode=allocation_mode).get_payload_type())

    def test_get_offset(self):
        # Expectation: get_offset_x() must return None if it is locally constructed
        # else it must return the offset as int. Same goes for get_offset_y()
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                self.assertIsNone(Frame(0, allocation_mode).get_offset_x())
                self.assertIsNone(Frame(0, allocation_mode).get_offset_y())

                with self.cam:
                    frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                               allocation_mode=allocation_mode)
                    self.assertIsNotNone(frame.get_offset_x())
                    self.assertIsNotNone(frame.get_offset_y())

    def test_get_dimension(self):
        # Expectation: get_width() must return None if it is locally constructed
        # else it must return width as int. Same goes for get_height()
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                self.assertIsNone(Frame(0, allocation_mode).get_width())
                self.assertIsNone(Frame(0, allocation_mode).get_height())

                with self.cam:
                    frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                               allocation_mode=allocation_mode)
                    self.assertIsNotNone(frame.get_width())
                    self.assertIsNotNone(frame.get_height())

    def test_deepcopy(self):
        # Expectation: a deepcopy must clone the frame buffer with it is contents an
        # update the internally store pointer in VmbFrame struct.
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                with self.cam:
                    frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                               allocation_mode=allocation_mode)

                frame_cpy = copy.deepcopy(frame)

                # Ensure frames and their members are not the same object
                self.assertNotEqual(id(frame), id(frame_cpy))
                self.assertNotEqual(id(frame._buffer), id(frame_cpy._buffer))
                self.assertNotEqual(id(frame._frame), id(frame_cpy._frame))

                # Ensure that both buffers have the same size and contain the same data.
                self.assertEqual(frame.get_buffer_size(), frame_cpy.get_buffer_size())
                self.assertTrue(all(a == b for a, b in zip(frame.get_buffer(),
                                                           frame_cpy.get_buffer())))

                # Ensure that internal Frame Pointer points to correct buffer.
                self.assertEqual(frame._frame.buffer,
                                 ctypes.cast(frame._buffer, ctypes.c_void_p).value)

                self.assertEqual(frame_cpy._frame.buffer,
                                 ctypes.cast(frame_cpy._buffer, ctypes.c_void_p).value)

                self.assertEqual(frame._frame.bufferSize, frame_cpy._frame.bufferSize)

    def test_get_pixel_format(self):
        # Expectation: Frames have an image format set after acquisition
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                with self.cam:
                    self.assertNotEqual(
                        self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                           allocation_mode=allocation_mode).get_pixel_format(), 0)

    def test_incompatible_formats_value_error(self):
        # Expectation: Conversion into incompatible formats must lead to an value error
        for allocation_mode in AllocationMode:
            with self.subTest(f'allocation_mode={str(allocation_mode)}'):
                with self.cam:
                    frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms,
                                               allocation_mode=allocation_mode)

                current_fmt = frame.get_pixel_format()
                convertable_fmt = current_fmt.get_convertible_formats()

                for fmt in PixelFormat.__members__.values():
                    if (fmt != current_fmt) and (fmt not in convertable_fmt):
                        self.assertRaises(ValueError, frame.convert_pixel_format, fmt)

    def test_convert_to_all_given_formats(self):
        # Expectation: A Series of Frame, each acquired with a different Pixel format Must be
        # convertible to all formats the given format claims it is convertible to without any
        # errors.

        test_frames = []

        with self.cam:
            initial_pixel_format = self.cam.get_pixel_format()
            for fmt in self.cam.get_pixel_formats():
                self.cam.set_pixel_format(fmt)

                frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms)

                self.assertEqual(fmt, frame.get_pixel_format())
                test_frames.append(frame)
            self.cam.set_pixel_format(initial_pixel_format)

        for frame in test_frames:
            original_fmt = frame.get_pixel_format()
            for expected_fmt in frame.get_pixel_format().get_convertible_formats():
                with self.subTest(f'convert {repr(original_fmt)} to {repr(expected_fmt)}'):
                    transformed_frame = frame.convert_pixel_format(expected_fmt)

                    self.assertEqual(expected_fmt, transformed_frame.get_pixel_format())
                    self.assertEqual(original_fmt, frame.get_pixel_format())

                    # Ensure that width and height of frames are identical (if both formats can be
                    # represented as numpy arrays)
                    try:
                        original_shape = frame.as_numpy_ndarray().shape
                        transformed_shape = transformed_frame.as_numpy_ndarray().shape
                        self.assertTupleEqual(original_shape[0:2], transformed_shape[0:2])
                    except VmbFrameError:
                        # one of the pixel formats does not support representation as numpy array
                        self.skipTest(f'{repr(original_fmt)} or {repr(expected_fmt)} is not '
                                      'representable as numpy array')
                    except ImportError:
                        # Numpy is not available. Checking shape is not possible.
                        self.skipTest('Numpy not installed. Could not check frame shapes for '
                                      'equality')

    def test_numpy_arrays_can_be_accessed_after_frame_is_garbage_collected(self):
        # Expectation: A numpy array that was created from a VmbPy frame is valid even if the
        # original VmbPy frame has been deleted and the garbage collector cleaned it up. The
        # lifetime of the VmbPy frame's self._buffer must be tied to both, the frame and the numpy
        # array. Otherwise a segfault occurs (execution aborts immediately!)

        # WARNING: IF A SEGFAULT IS CAUSED, THIS WILL IMMEDIATELY HALT ALL EXECUTION OF THE RUNNING
        # PROCESS. THIS MEANS THAT THE TEST CASE WILL NOT REALLY REPORT A FAILURE, BUT SIMPLY EXIT
        # WITHOUT BEING MARKED AS PASSED. ALL SUBSEQUENT TEST CASES WILL ALSO NOT BE EXECUTED
        with self.cam:
            compatible_formats = intersect_pixel_formats(OPENCV_PIXEL_FORMATS,
                                                         self.cam.get_pixel_formats())
            if not compatible_formats:
                self.skipTest(f'Camera does not support a compatible format. Available formats '
                              f'from camera are: {self.cam.get_pixel_formats()}. Numpy compatible '
                              f'formats are {OPENCV_PIXEL_FORMATS}')
            if self.cam.get_pixel_format() not in compatible_formats:
                self.cam.set_pixel_format(compatible_formats[0])
            frame = self.cam.get_frame(timeout_ms=self.frame_timeout_ms)
        try:
            np_array = frame.as_numpy_ndarray()
        except ImportError:
            self.skipTest('Numpy is not imported')
        del frame

        # Ensure that garbage collection has cleaned up the frame object
        import gc
        gc.collect()

        # Perform some calculation with numpy array to ensure that access is possible
        self.assertNoRaise(np_array.mean)


class UserSuppliedBufferTest(VmbPyTestCase):
    def setUp(self):
        if np is None:
            self.skipTest('Numpy is needed for these tests')

        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        try:
            # Camera is opened in setUp to make enabling/disabling chunk features in subclass below
            # possible in setUp and tearDown
            self.cam._open()
            try:
                set_throughput_to_fraction(self.cam, 0.8)
                self.cam.DeviceLinkThroughputLimitMode.set("On")
                reset_roi(self.cam, 64)
                _, max_gain = self.cam.Gain.get_range()
                self._old_gain = self.cam.Gain.get()
                # set Gain to max. to make sure, that dark frames won't contain only zeros
                self.cam.Gain.set(max_gain)
            except AttributeError:
                pass
            self.local_device = self.cam.get_local_device()
        except VmbCameraError as e:
            self.cam._close()
            raise Exception('Failed to open Camera {}.'.format(self.cam)) from e

    def tearDown(self):
        try:
            self.cam.DeviceLinkThroughputLimitMode.set("Off")
            reset_roi(self.cam)
            self.cam.Gain.set(self._old_gain)
        except AttributeError:
            pass
        self.cam._close()
        self.vmb._shutdown()

    def test_conversion_writes_to_user_supplied_buffer(self):
        # Expectation: Performing a conversion from one format to another writes pixel data to the
        # user supplied buffer
        record_format = PixelFormat.Mono8
        target_format = PixelFormat.Bgr8
        self.cam.set_pixel_format(record_format)
        original_frame = self.cam.get_frame()
        self.assertEqual(original_frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. We cannot reliably work with a possibly '
                         'empty frame because we want to check if pixel values are written '
                         'correctly.')
        # Do conversion once without user supplied buffer. This creates a new VmbPy Frame with fresh
        # buffer. We can then reuse that buffer for future conversions
        np_buffer = original_frame.convert_pixel_format(target_format).as_numpy_ndarray()
        np_buffer[:] = 0  # Set buffer to 0 to be sure that next conversion writes new data to it
        self.assertEqual(np_buffer.sum(), 0, 'buffer values were not set to 0 correctly')
        # Discard VmbPy Frame. We are only interested to see if the buffer values actually changed
        _ = original_frame.convert_pixel_format(target_format, destination_buffer=np_buffer.data)
        self.assertNotEqual(np_buffer.sum(),
                            0,
                            'destination_buffer still contains only 0s. Either data was not '
                            'written to buffer or recorded camera image contained only 0s')

    def test_conversion_to_same_format_as_input(self):
        # Expectation: If the target format is the same as the input format the image data in the
        # user supplied buffer is identical to the input frame
        record_format = PixelFormat.Mono8
        self.cam.set_pixel_format(record_format)
        original_frame = self.cam.get_frame()
        self.assertEqual(original_frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. We cannot reliably work with a possibly '
                         'empty frame because we want to check if pixel values are written '
                         'correctly.')
        # Do conversion once without user supplied buffer. This creates a new VmbPy Frame with fresh
        # buffer. We can then reuse that buffer for future conversions
        np_buffer = original_frame.convert_pixel_format(original_frame.get_pixel_format()) \
                                  .as_numpy_ndarray()
        np_buffer[:] = 0  # Set buffer to 0 to be sure that next conversion writes new data to it
        self.assertEqual(np_buffer.sum(), 0, 'buffer values were not set to 0 correctly')
        converted_frame = original_frame.convert_pixel_format(original_frame.get_pixel_format(),
                                                              destination_buffer=np_buffer.data)
        self.assertEqual(original_frame.get_pixel_format(), converted_frame.get_pixel_format())
        # Since target format is the same as input format all elements should be identical. Compare
        # them element-wise
        self.assertTrue(np.allclose(original_frame.as_numpy_ndarray(), np_buffer),
                        'Pixel data after conversion is not identical to original pixel data')

    def test_image_data_is_as_expected(self):
        # Expectation: Format conversion works correctly. Tested here only with RGB8 -> BGR8 as the
        # flipped channel order is easy to verify with numpy. Not a full test for the image
        # transform library
        record_format = PixelFormat.Rgb8
        target_format = PixelFormat.Bgr8
        try:
            self.cam.set_pixel_format(record_format)
        except ValueError:
            self.skipTest(f'{str(self.cam)} does not support pixel format "{record_format}"')
        original_frame = self.cam.get_frame()
        self.assertEqual(original_frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. We cannot reliably work with a possibly '
                         'empty frame because we want to check if pixel values are written '
                         'correctly.')
        # Do conversion once without user supplied buffer. This creates a new VmbPy Frame with fresh
        # buffer. We can then reuse that buffer for future conversions
        np_buffer = original_frame.convert_pixel_format(target_format).as_numpy_ndarray()
        np_buffer[:] = 0  # Set buffer to 0 to be sure that next conversion writes new data to it
        self.assertEqual(np_buffer.sum(), 0, 'buffer values were not set to 0 correctly')
        _ = original_frame.convert_pixel_format(target_format, destination_buffer=np_buffer.data)
        self.assertNotEqual(np_buffer.sum(),
                            0,
                            'destination_buffer still contains only 0s. Either data was not '
                            'written to buffer or recorded camera image contained only 0s')
        # BGR8 is just RGB8 with the channel order flipped. Compare the actual pixel data by
        # flipping channels again and comparing element-wise
        self.assertTrue(np.allclose(original_frame.as_numpy_ndarray(), np_buffer[:, :, ::-1]),
                        'Pixel data did not match expected values')

    def test_numpy_reports_shared_memory_for_user_buffer_and_new_ndarray(self):
        # Expectation: If a numpy array is taken of the frame conversion result numpy reports that
        # it shares memory with the user supplied buffer
        record_format = PixelFormat.Mono8
        target_format = PixelFormat.Bgr8
        self.cam.set_pixel_format(record_format)
        original_frame = self.cam.get_frame()
        self.assertEqual(original_frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. We cannot reliably work with a possibly '
                         'empty frame because we want to check if pixel values are written '
                         'correctly.')
        # Do conversion once without user supplied buffer. This creates a new VmbPy Frame with fresh
        # buffer. We can then reuse that buffer for future conversions
        np_buffer = original_frame.convert_pixel_format(target_format).as_numpy_ndarray()
        np_buffer[:] = 0  # Set buffer to 0 to be sure that next conversion writes new data to it
        self.assertEqual(np_buffer.sum(), 0, 'buffer values were not set to 0 correctly')
        conversion_result = original_frame.convert_pixel_format(target_format,
                                                                destination_buffer=np_buffer.data)
        self.assertNotEqual(np_buffer.sum(),
                            0,
                            'destination_buffer still contains only 0s. Either data was not '
                            'written to buffer or recorded camera image contained only 0s')
        # Creating a numpy array from the conversion results uses the user supplied buffer
        conversion_result_np_array = conversion_result.as_numpy_ndarray()
        self.assertTrue(np.shares_memory(conversion_result_np_array, np_buffer))
        # No memory is shared with the original frame
        self.assertFalse(np.shares_memory(original_frame.as_numpy_ndarray(), np_buffer))
        # Additional check: if the conversion_result_np_array changes the same change should be
        # visible in np_buffer since they use the same memory
        conversion_result_np_array.flat[0] += 1
        self.assertEqual(conversion_result_np_array.flat[0], np_buffer.flat[0])
        conversion_result_np_array.flat[-1] += 1
        self.assertEqual(conversion_result_np_array.flat[-1], np_buffer.flat[-1])

    def test_too_small_buffer_raises_exception(self):
        # Expectation: If the buffer provided is too small, an exception is raised. The exception
        # message provides information why the buffer was not accepted
        record_format = PixelFormat.Mono8
        target_format = PixelFormat.Bgr8
        self.cam.set_pixel_format(record_format)
        original_frame = self.cam.get_frame()
        np_buffer = np.zeros((1))
        with self.assertRaisesRegex(BufferError, ".*size.*"):
            original_frame.convert_pixel_format(target_format, destination_buffer=np_buffer.data)
        # Make sure that error message is also correct if no actual transformation is expected
        # because target format is same as record format
        with self.assertRaisesRegex(BufferError, ".*size.*"):
            original_frame.convert_pixel_format(original_frame.get_pixel_format(),
                                                destination_buffer=np_buffer.data)

    def test_wrong_buffer_type_raises_exception(self):
        # Expectation: If the buffer has an incorrect type, a TypeError is raised.
        record_format = PixelFormat.Mono8
        target_format = PixelFormat.Bgr8
        self.cam.set_pixel_format(record_format)
        original_frame = self.cam.get_frame()
        np_buffer = original_frame.convert_pixel_format(target_format).as_numpy_ndarray()
        with self.assertRaises(TypeError):
            # Try to pass full numpy array instead of the `.data` field of the array
            original_frame.convert_pixel_format(target_format, destination_buffer=np_buffer)


class UserSuppliedBufferWithChunkTest(UserSuppliedBufferTest):
    def setUp(self):
        super().setUp()
        try:
            self.enable_chunk_features()
        except (VmbFeatureError, AttributeError):
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'ChunkModeActive\' not available.')

    def tearDown(self):
        self.disable_chunk_features()
        super().tearDown()

    def enable_chunk_features(self):
        # Turn on all Chunk features
        self.cam.ChunkModeActive.set(False)
        for value in self.cam.ChunkSelector.get_available_entries():
            self.cam.ChunkSelector.set(value)
            self.cam.ChunkEnable.set(True)
        self.cam.ChunkModeActive.set(True)

    def disable_chunk_features(self):
        self.cam.ChunkModeActive.set(False)
        for value in self.cam.ChunkSelector.get_available_entries():
            self.cam.ChunkSelector.set(value)
            self.cam.ChunkEnable.set(False)
