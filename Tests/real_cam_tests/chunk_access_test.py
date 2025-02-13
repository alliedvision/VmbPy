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
import os
import sys
import threading

from vmbpy import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase, calculate_acquisition_time, set_throughput_to_fraction, reset_roi


class ChunkAccessTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        try:
            self.cam._open()
            self.local_device = self.cam.get_local_device()
            try:
                set_throughput_to_fraction(self.cam, 0.8)
                self.cam.DeviceLinkThroughputLimitMode.set("On")
                reset_roi(self.cam, 64)
            except AttributeError:
                pass
        except VmbCameraError as e:
            self.cam._close()
            raise Exception('Failed to open Camera {}.'.format(self.cam)) from e

        try:
            self.enable_chunk_features()

        except (VmbFeatureError, AttributeError):
            self.cam._close()
            self.vmb._shutdown()
            self.skipTest('Required Feature \'ChunkModeActive\' not available.')

    def tearDown(self):
        self.disable_chunk_features()
        try:
            self.cam.DeviceLinkThroughputLimitMode.set("Off")
            reset_roi(self.cam)
        except AttributeError:
            pass
        self.cam._close()
        self.vmb._shutdown()

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

    def test_chunk_callback_is_executed(self):
        # Expectation: The chunk callback is executed for every call to `Frame.access_chunk_data`
        class FrameHandler:
            def __init__(self, frame_limit) -> None:
                self.frame_limit = frame_limit
                self.frame_callbacks_executed = 0
                self.chunk_callbacks_executed = 0
                self.is_done = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                self.frame_callbacks_executed += 1
                frame.access_chunk_data(self.chunk_callback)
                stream.queue_frame(frame)

                if self.frame_callbacks_executed >= self.frame_limit:
                    self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                self.chunk_callbacks_executed += 1

        frame_count = 5
        handler = FrameHandler(frame_count)
        try:
            try:
                timeout = calculate_acquisition_time(self.cam, frame_count)
                # Add one second extra time for acquisition overhead and additional 10% buffer
                timeout = 1.1 * (1.0 + timeout)
            except VmbFeatureError:
                timeout = 5.0
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=timeout),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertEqual(handler.frame_callbacks_executed,
                         handler.chunk_callbacks_executed,
                         f'Number of executed frame callbacks '
                         f'({handler.frame_callbacks_executed}) does not equal number of '
                         f'executed chunk callbacks ({handler.chunk_callbacks_executed})')

    def test_managed_get_frame_chunk_access(self):
        # Expectation: Chunk access is possible for frames that are acquired using the context
        # managed get_frame method.
        class CallbackHelper:
            def __init__(self) -> None:
                self.chunk_callbacks_executed = 0

            def chunk_callback(self, feats: FeatureContainer):
                self.chunk_callbacks_executed += 1

        helper = CallbackHelper()
        with self.cam.get_frame_with_context() as frame:
            self.assertEqual(frame.get_status(),
                             FrameStatus.Complete,
                             'Recorded frame was not complete. '
                             'We cannot parse incomplete frame for chunk data.')
            frame.access_chunk_data(helper.chunk_callback)
        self.assertEqual(1, helper.chunk_callbacks_executed)

    def test_get_frame_chunk_access_raises_error(self):
        # Expectation: Chunk access is not possible for frames that are acquired using the
        # non-managed get_frame method. A VmbChunkError is raised
        def dummy_chunk_callback(feats: FeatureContainer):
            pass

        frame = self.cam.get_frame()
        self.assertRaises(VmbChunkError, frame.access_chunk_data, dummy_chunk_callback)

    def test_get_frame_generator_chunk_access(self):
        # Expectation: Chunk access is possible inside the loop for frames that are acquired using
        # the frame generator
        class CallbackHelper:
            def __init__(self) -> None:
                self.chunk_callbacks_executed = 0

            def chunk_callback(self, feats: FeatureContainer):
                self.chunk_callbacks_executed += 1

        helper = CallbackHelper()
        number_of_iterations = 5
        number_of_complete_frames = 0
        for frame in self.cam.get_frame_generator(limit=number_of_iterations):
            if frame.get_status() == FrameStatus.Complete:
                number_of_complete_frames += 1
                frame.access_chunk_data(helper.chunk_callback)
        self.assertNotEqual(number_of_complete_frames, 0)
        self.assertEqual(number_of_complete_frames, helper.chunk_callbacks_executed)

    def test_error_raised_if_chunk_is_not_active(self):
        # Expectation: If the frame does not contain chunk data `VmbFrameError` is raised upon
        # calling `Frame.access_chunk_data`
        class FrameHandler:
            def __init__(self, test_instance: VmbPyTestCase) -> None:
                self.expected_exception_raised = False
                self.is_done = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                try:
                    frame.access_chunk_data(self.chunk_callback)
                except VmbFrameError:
                    self.expected_exception_raised = True
                finally:
                    self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                # Will never be called because the C-API raises an error before we get this far
                pass

        self.disable_chunk_features()
        handler = FrameHandler(self)
        try:
            try:
                frame_count = 1
                timeout = calculate_acquisition_time(self.cam, frame_count)
                # Add one second extra time for acquisition overhead and additional 10% buffer
                timeout = 1.1 * (1.0 + timeout)
            except VmbFeatureError:
                timeout = 5.0
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=timeout),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertTrue(handler.expected_exception_raised,
                        'The expected Exception type was not raised by `access_chunk_data`')

    def test_exceptions_raised_in_callback_are_propagated(self):
        # Expectation: If an exception is raised in the user supplied chunk callback that is
        # propagated and raised from the call to `Frame.access_chunk_data`
        class _CustomException(Exception):
            pass

        class FrameHandler:
            def __init__(self) -> None:
                self.expected_exception_raised = False
                self.exception_message_as_expected = False
                self.is_done = threading.Event()
                self.__exception_message = 'foo'

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                try:
                    frame.access_chunk_data(self.chunk_callback)
                except _CustomException as e:
                    self.expected_exception_raised = True
                    self.exception_message_as_expected = str(e) == self.__exception_message
                finally:
                    self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                raise _CustomException(self.__exception_message)

        handler = FrameHandler()
        try:
            try:
                frame_count = 1
                timeout = calculate_acquisition_time(self.cam, frame_count)
                # Add one second extra time for acquisition overhead and additional 10% buffer
                timeout = 1.1 * (1.0 + timeout)
            except VmbFeatureError:
                timeout = 5.0
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=timeout),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertTrue(handler.expected_exception_raised,
                        'The expected Exception type was not raised by `access_chunk_data`')
        self.assertTrue(handler.exception_message_as_expected,
                        'The exception did not contain the expected message')

    def test_raising_exceptions_does_not_impact_later_chunk_access(self):
        # Expectation: An exception that was raised on a previous chunk access does not prevent
        # later chunk access
        class _CustomException(Exception):
            pass

        class FrameHandler:
            def __init__(self, frame_limit) -> None:
                self.frame_limit = frame_limit
                self.__frame_count = 0
                self.exception_was_raised_once = False
                self.later_access_worked = False
                self.is_done = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                try:
                    frame.access_chunk_data(self.chunk_callback)
                except _CustomException:
                    self.exception_was_raised_once = True
                finally:
                    self.__frame_count += 1
                    if self.__frame_count >= self.frame_limit:
                        self.is_done.set()

            def chunk_callback(self, feats: FeatureContainer):
                if self.__frame_count == 0:
                    raise _CustomException()
                if self.exception_was_raised_once:
                    self.later_access_worked = True

        frame_count = 5
        handler = FrameHandler(frame_count)
        try:
            try:
                timeout = calculate_acquisition_time(self.cam, frame_count)
                # Add one second extra time for acquisition overhead and additional 10% buffer
                timeout = 1.1 * (1.0 + timeout)
            except VmbFeatureError:
                timeout = 5.0
            self.cam.start_streaming(handler)
            self.assertTrue(handler.is_done.wait(timeout=timeout),
                            'Frame handler did not finish before timeout')
        finally:
            self.cam.stop_streaming()
        self.assertTrue(handler.exception_was_raised_once,
                        'The expected Exception was never raised by `access_chunk_data`')
        self.assertTrue(handler.later_access_worked,
                        'Access to the chunk data in later calls did not work')

    def test_chunk_runtime_type_check(self):
        # Expectation: A chunk callback function with incorrect number of parameters causes a
        # TypeError to be raised
        def valid_handler(feats):
            pass

        def invalid_handler1():
            pass

        def invalid_handler2(feats, foo):
            pass

        # Create a dummy Frame instance to call `access_chunk_data` on
        f = Frame(buffer_size=10, allocation_mode=AllocationMode.AnnounceFrame)
        self.assertRaises(TypeError, f.access_chunk_data, invalid_handler1)
        self.assertRaises(TypeError, f.access_chunk_data, invalid_handler2)
        # Even for a valid handler an error is raised. This is because the dummy frame is not
        # announced to VmbC. But it did pass the type check!
        self.assertRaises(VmbChunkError, f.access_chunk_data, valid_handler)

    def test_contains_chunk_data_true(self):
        # Expectation: if frame contains chunk data the function `contains_chunk_data`
        # will return true
        frame = self.cam.get_frame()
        self.assertEqual(frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. '
                         'We cannot parse incomplete frame for chunk data.')
        self.assertTrue(frame.contains_chunk_data())

    def test_contains_chunk_data_false(self):
        # Expectation: if frame contains no chunk data the function `contains_chunk_data`
        # will return false
        self.disable_chunk_features()
        frame = self.cam.get_frame()
        self.assertEqual(frame.get_status(),
                         FrameStatus.Complete,
                         'Recorded frame was not complete. '
                         'We cannot parse incomplete frame for chunk data.')
        self.assertFalse(frame.contains_chunk_data())
