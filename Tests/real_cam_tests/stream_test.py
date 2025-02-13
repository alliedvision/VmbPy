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
import time

from vmbpy import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase, calculate_acquisition_time, set_throughput_to_fraction, reset_roi


def dummy_frame_handler(cam: Camera, stream: Stream, frame: Frame):
    pass


class StreamTest(VmbPyTestCase):
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
            try:
                set_throughput_to_fraction(self.cam, 0.8)
                self.cam.DeviceLinkThroughputLimitMode.set("On")
                reset_roi(self.cam, 64)
            except AttributeError:
                pass
            self.streams = self.cam.get_streams()
        except VmbCameraError as e:
            self.cam._close()
            raise Exception('Failed to open Camera {}.'.format(self.cam)) from e

    def tearDown(self):
        # In some test cases the camera might already have been closed. In that case an additional
        # call to `cam._close` will result in an error. This can be ignored in our test tearDown.
        try:
            try:
                self.cam.DeviceLinkThroughputLimitMode.set("Off")
                reset_roi(self.cam)
            except AttributeError:
                pass
            self.cam._close()
        except Exception:
            pass
        self.vmb._shutdown()

    def test_stream_feature_discovery(self):
        # Expectation: Outside of context, all features must be cleared,
        # inside of context all features must be detected.
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                self.assertNotEqual(stream.get_all_features(), ())

    def test_stream_features_category(self):
        # Expectation: Getting features by category for an existing category returns a set of
        # features, for a non-existent category an empty set is returned
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                category = stream.get_all_features()[0].get_category()
                self.assertNotEqual(stream.get_features_by_category(category), ())
                self.assertEqual(stream.get_features_by_category("Invalid Category"), ())

    def test_stream_feature_by_name(self):
        # Expectation: A feature can be gotten by name. Invalid feature names raise a
        # VmbFeatureError
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                feat = stream.get_all_features()[0]
                self.assertEqual(stream.get_feature_by_name(feat.get_name()), feat)
                self.assertRaises(VmbFeatureError, stream.get_feature_by_name, "Invalid Name")

    def test_stream_features_by_type(self):
        # Expectation: Getting features by type returns a set of features for an existing type
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                type = stream.get_all_features()[0].get_type()
                self.assertNotEqual(stream.get_features_by_type(type), ())

    def test_stream_features_selected_by(self):
        # Expectation: Selected features can be gotten for a feature instance
        for stream in self.streams:
            with self.subTest(f'stream={stream}'):
                try:
                    feat = [f for f in stream.get_all_features()
                            if f.has_selected_features()].pop()
                except IndexError:
                    self.skipTest('Could not find feature with \'selected features\'')
                self.assertNotEqual(stream.get_features_selected_by(feat), ())

    def test_stream_frame_generator_limit_set(self):
        # Expectation: The Frame generator fetches the given number of images.
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                for expected_frames in (1, 7, 11):
                    count = 0
                    for _ in self.cam.get_frame_generator(expected_frames):
                        count += 1
                    self.assertEqual(count, expected_frames)

    def test_stream_frame_generator_error(self):
        # Expectation: The Frame generator raises a ValueError on a negative limit

        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                # Check limits
                for limits in ((0, ), (-1, ), (1, 0), (1, -1)):
                    with self.assertRaises(ValueError):
                        for _ in self.cam.get_frame_generator(*limits):
                            pass

                # generator execution must throw if streaming is enabled
                self.cam.start_streaming(dummy_frame_handler, 5)

                self.assertRaises(VmbCameraError, stream.get_frame)
                with self.assertRaises(VmbCameraError):
                    for _ in stream.get_frame_generator(1):
                        pass

                # Stop Streaming: Everything should be fine.
                self.cam.stop_streaming()
                self.assertNoRaise(stream.get_frame)
                for f in self.cam.get_frame_generator(1):
                    self.assertIsInstance(f, Frame)

    def test_stream_get_frame(self):
        # Expectation: Gets single Frame without any exception. Image data must be set.
        # If a zero or negative timeouts must lead to a ValueError.
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                self.assertRaises(ValueError, stream.get_frame, 0)
                self.assertRaises(ValueError, stream.get_frame, -1)

                self.assertNoRaise(stream.get_frame)
                self.assertIsInstance(stream.get_frame(), Frame)

    def test_camera_get_frame_with_context(self):
        # Expectation: Gets a single context managed Frame.
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                with stream.get_frame_with_context() as frame:
                    self.assertIsInstance(frame, Frame)

    def test_camera_get_frame_with_context_invalid_timeouts_raise_error(self):
        # Expectation: Using an invalid value for the timeout parameter raises a `ValueError`.
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                for invalid_value in (0, -1):
                    with self.subTest(f'timeout_ms={invalid_value}'):
                        with self.assertRaises(ValueError):
                            with stream.get_frame_with_context(timeout_ms=invalid_value):
                                pass

    def test_stream_is_streaming(self):
        # Expectation: After start_streaming() is_streaming() must return true. After stop it must
        # return false. If the camera context is left without stop_streaming(), leaving
        # the context must stop all streams.

        # self.cam was already entered in the setUp method. Exit here for clean context manager
        # state so that leaving the context closes the Camera as expected
        # self.cam._close()

        # Normal Operation
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                self.cam.start_streaming(dummy_frame_handler)
                self.assertEqual(stream.is_streaming(), True)
                # Wait a little bit before stopping the stream again to give camera time to settle
                time.sleep(0.1)

                self.cam.stop_streaming()
                self.assertEqual(stream.is_streaming(), False)

        # Missing the stream stop. Close must stop all active streams
        streams = []
        for stream in self.cam.get_streams():
            streams.append(stream)
            stream.start_streaming(dummy_frame_handler, 5)
            self.assertEqual(stream.is_streaming(), True)

        # Closing camera connection must stop all active streams
        self.cam._close()

        for stream in streams:
            # This is actually not how users should use the Stream class. Camera is closed and the
            # Stream class is useless without an open Camera connection!
            self.assertEqual(stream.is_streaming(), False)

        # Open camera again so tests tearDown method works correctly
        self.cam._open()

    def test_stream_streaming_error_frame_count(self):
        # Expectation: A negative or zero frame_count must lead to an value error
        # with self.cam:
        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                self.assertRaises(ValueError, stream.start_streaming, dummy_frame_handler, 0)
                self.assertRaises(ValueError, stream.start_streaming, dummy_frame_handler, -1)

    def test_stream_streaming(self):
        # Expectation: A given frame_handler must be executed for each buffered frame.

        class FrameHandler:
            def __init__(self, frame_count):
                self.cnt = 0
                self.frame_count = frame_count
                self.event = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                self.cnt += 1

                if self.cnt == self.frame_count:
                    self.event.set()

        frame_count = 10
        handler = FrameHandler(frame_count)

        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                try:
                    self.cam.start_streaming(handler, frame_count)

                    # Wait until the FrameHandler has been executed for each queued frame
                    self.assertTrue(handler.event.wait(timeout),
                                    'Handler event was not set. Frame count was not reached')

                finally:
                    self.cam.stop_streaming()

    def test_stream_streaming_requeue(self):
        # Expectation: A given frame must be reused if it is enqueued again.

        class FrameHandler:
            def __init__(self, frame_count):
                self.cnt = 0
                self.frame_count = frame_count
                self.event = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                self.cnt += 1

                if self.cnt == self.frame_count:
                    self.event.set()

                stream.queue_frame(frame)

        frame_count = 5
        frame_reuse = 2
        handler = FrameHandler(frame_count * frame_reuse)

        for stream in self.cam.get_streams():
            with self.subTest(f'Stream={stream}'):
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count * frame_reuse)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                try:
                    stream.start_streaming(handler, frame_count)

                    # Wait until the FrameHandler has been executed for each queued frame
                    self.assertTrue(handler.event.wait(timeout),
                                    'Handler event was not set. Frame count was not reached')

                finally:
                    stream.stop_streaming()

    def test_stream_context_sensitivity(self):
        # Expectation: Call get_all_features outside of Camera context raises a RuntimeError and
        # the error message references the Camera context
        stream = self.cam.get_streams()[0]
        feat = stream.get_all_features()[0]
        feat_name = feat.get_name()

        # Ensure that normal calls work while context is still open
        self.assertNoRaise(stream.get_all_features)
        self.assertNoRaise(stream.get_features_selected_by, feat)
        self.assertNoRaise(stream.get_features_by_type, IntFeature)
        self.assertNoRaise(stream.get_features_by_category, 'foo')
        self.assertNoRaise(stream.get_feature_by_name, feat_name)

        # This closes the stream[0] of self.cam implicitly. Alternatively it is possible to call
        # stream.close() here if that implicit behavior should not be relied upon
        self.cam._close()
        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.get_all_features)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.get_features_selected_by,
                               feat)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.get_features_by_type,
                               IntFeature)

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.get_features_by_category,
                               'foo')

        self.assertRaisesRegex(RuntimeError,
                               'outside of Camera.* context',
                               stream.get_feature_by_name,
                               feat_name)

        # open camera context again so tearDown works as expected
        self.cam._open()
