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
import multiprocessing
import os
import sys
import threading
import time
import unittest

from vmbpy import *
from vmbpy.frame import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase, calculate_acquisition_time


def dummy_frame_handler(cam: Camera, stream: Stream, frame: Frame):
    pass


def _open_camera(id: str,
                 shutdown_request: multiprocessing.Event):
    """Helper function to open a camera in a different process via multiprocessing

    This function can be used in a process spawned by the multiprocessing library. This allows a
    separate process to open a camera, making tests possible that rely on cameras being accessed
    from different processes. Used e.g. in CamCameraTest.test_permitted_access_mode_is_updated.

    Example on how to use:
    p = multiprocessing.Process(target=_open_camera, args=('<cam-id>', shutdown_event)
    p.start()
    # camera is now opened in separate process, maybe some wait time is needed so that an
    # appropriate camera event is received by VmbC.
    # Perform test here
    shutdown_event.set()
    p.join()
    """
    import vmbpy
    with vmbpy.VmbSystem.get_instance() as vmb:
        with vmb.get_camera_by_id(id):
            # Set a timeout so we can be sure the process exits and does not remain as an orphaned
            # process forever
            shutdown_request.wait(timeout=15)


class CamCameraTest(VmbPyTestCase):
    def setUp(self):
        self.vmb = VmbSystem.get_instance()
        self.vmb._startup()

        try:
            self.cam = self.vmb.get_camera_by_id(self.get_test_camera_id())

        except VmbCameraError as e:
            self.vmb._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        self.cam.set_access_mode(AccessMode.Full)

    def tearDown(self):
        self.cam.set_access_mode(AccessMode.Full)
        self.vmb._shutdown()

    def test_camera_context_manager_access_mode(self):
        # Expectation: Entering Context must not throw in cases where the current access mode is
        # within get_permitted_access_modes()

        permitted_modes = self.cam.get_permitted_access_modes()

        for mode in permitted_modes:
            self.cam.set_access_mode(mode)

            try:
                with self.cam:
                    pass

            except BaseException as e:
                self.fail(f'Failed due to exception: {e}')

    def test_camera_context_manager_feature_discovery(self):
        # Expectation: Outside of context, all features must be cleared,
        # inside of context all features must be detected.
        with self.cam:
            self.assertNotEqual(self.cam.get_all_features(), ())

    def test_camera_access_mode(self):
        # Expectation: set/get access mode
        for mode in AccessMode:
            self.cam.set_access_mode(mode)
            self.assertEqual(self.cam.get_access_mode(), mode)

    def test_camera_get_id(self):
        # Expectation: get decoded camera id
        self.assertTrue(self.cam.get_id())

    def test_camera_get_extended_id(self):
        # Expectation: get decoded extended camera id
        self.assertTrue(self.cam.get_extended_id())

    def test_camera_get_name(self):
        # Expectation: get decoded camera name
        self.assertTrue(self.cam.get_name())

    def test_camera_get_model(self):
        # Expectation: get decoded camera model
        self.assertTrue(self.cam.get_model())

    def test_camera_get_serial(self):
        # Expectation: get decoded camera serial
        self.assertTrue(self.cam.get_serial())

    def test_camera_get_permitted_access_modes(self):
        # Expectation: get currently permitted access modes
        expected = (AccessMode.None_,
                    AccessMode.Full,
                    AccessMode.Read,
                    AccessMode.Unknown,
                    AccessMode.Exclusive)

        for mode in self.cam.get_permitted_access_modes():
            self.assertIn(mode, expected)

    @unittest.skipIf(sys.platform.startswith('linux'),
                     'Multiple VmbSystem startups via Multiprocessing seems to be problematic on '
                     'Linux')
    def test_permitted_access_mode_is_updated(self):
        # Expectation: When the camera is opened, permitted access mode changes
        device_unreachable_event = threading.Event()

        # Additional change handler that will inform us when our camera became "Unreachable"
        def _device_unreachable_informer(device: Camera, event: CameraEvent):
            if (device == self.cam and event == CameraEvent.Unreachable):
                device_unreachable_event.set()

        self.vmb.register_camera_change_handler(_device_unreachable_informer)

        # Prepare a process that will open the camera for us so we can observe the change in
        # permitted access modes. Must be a separate process, separate thread is not enough.
        shutdown_request = multiprocessing.Event()
        p = multiprocessing.Process(target=_open_camera,
                                    args=(self.cam.get_id(), shutdown_request))

        self.assertIn(AccessMode.Full, self.cam.get_permitted_access_modes())
        # Open camera in separate process to trigger a CameraEvent.Unreachable
        p.start()
        # Wait for a CameraEvent.Unreachable to be triggered for our device
        self.assertTrue(device_unreachable_event.wait(timeout=10),
                        'Waiting for the device discovery timed out')
        # Camera is now open in separate process. Make sure our permitted access modes reflects this
        self.assertNotIn(AccessMode.Full, self.cam.get_permitted_access_modes())
        # Tell spawned process to close camera and wait for it to shut down
        shutdown_request.set()
        p.join()
        # Remove the additional change handler we registered
        self.vmb.unregister_camera_change_handler(_device_unreachable_informer)

    def test_camera_get_transport_layer_type(self):
        # Expectation: returns instance of transport layer for Camera instance
        self.assertIsInstance(self.cam.get_transport_layer(), TransportLayer)

    def test_camera_get_interface_type(self):
        # Expectation: returns instance of interface for Camera instance
        self.assertIsInstance(self.cam.get_interface(), Interface)

    def test_camera_get_interface_id(self):
        # Expectation: get interface Id this camera is connected to
        self.assertTrue(self.cam.get_interface_id())

    def test_camera_get_streams_type(self):
        # Expectation: returns instances of Stream for Camera instance
        with self.cam:
            for stream in self.cam.get_streams():
                self.assertIsInstance(stream, Stream)

    def test_camera_get_local_device_type(self):
        # Expectation: returns instance of LocalDevice for Camera instance
        with self.cam:
            self.assertIsInstance(self.cam.get_local_device(), LocalDevice)

    def test_camera_frame_generator_limit_set(self):
        # Expectation: The Frame generator fetches the given number of images.
        with self.cam:
            for expected_frames in (1, 7, 11):
                count = 0
                for _ in self.cam.get_frame_generator(expected_frames):
                    count += 1
                self.assertEqual(count, expected_frames)

    def test_camera_frame_generator_error(self):
        # Expectation: The Frame generator raises a ValueError on a
        # negative limit and the camera raises an ValueError
        # if the camera is not opened.

        with self.cam:
            # Check limits
            for limits in ((0, ), (-1, ), (1, 0), (1, -1)):
                with self.assertRaises(ValueError):
                    for _ in self.cam.get_frame_generator(*limits):
                        pass

            # generator execution must throw if streaming is enabled
            self.cam.start_streaming(dummy_frame_handler, 5)

            self.assertRaises(VmbCameraError, self.cam.get_frame)
            with self.assertRaises(VmbCameraError):
                for _ in self.cam.get_frame_generator(1):
                    pass

            # Stop Streaming: Everything should be fine.
            self.cam.stop_streaming()
            self.assertNoRaise(self.cam.get_frame)
            for f in self.cam.get_frame_generator(1):
                self.assertIsInstance(f, Frame)

    def test_camera_get_frame(self):
        # Expectation: Gets single Frame without any exception. Image data must be set.
        # If a zero or negative timeouts must lead to a ValueError.
        with self.cam:
            self.assertRaises(ValueError, self.cam.get_frame, 0)
            self.assertRaises(ValueError, self.cam.get_frame, -1)

            self.assertNoRaise(self.cam.get_frame)
            self.assertIsInstance(self.cam.get_frame(), Frame)

    def test_camera_get_frame_with_context(self):
        # Expectation: Gets a single context managed Frame.
        with self.cam:
            with self.cam.get_frame_with_context() as frame:
                self.assertIsInstance(frame, Frame)

    def test_camera_get_frame_with_context_invalid_timeouts_raise_error(self):
        # Expectation: Using an invalid value for the timeout parameter raises a `ValueError`.
        for invalid_value in (0, -1):
            with self.subTest(f'timeout_ms={invalid_value}'):
                with self.assertRaises(ValueError):
                    with self.cam:
                        with self.cam.get_frame_with_context(timeout_ms=invalid_value):
                            pass

    def test_camera_capture_error_outside_vmbsystem_scope(self):
        # Expectation: Camera access outside of VmbSystem scope must lead to a RuntimeError
        gener = None

        with self.cam:
            gener = self.cam.get_frame_generator(1)

        # Shutdown API
        self.vmb._shutdown()

        # Access invalid Iterator
        with self.assertRaises(RuntimeError):
            for _ in gener:
                pass

    def test_camera_capture_error_outside_camera_scope(self):
        # Expectation: Camera access outside of Camera scope must lead to a RuntimeError
        gener = None

        with self.cam:
            gener = self.cam.get_frame_generator(1)

        with self.assertRaises(RuntimeError):
            for _ in gener:
                pass

    @unittest.skipIf(VmbPyTestCase.get_test_camera_id().startswith("Sim"),
                     "Test skipped in simulation mode.")
    def test_camera_capture_timeout(self):
        # Expectation: Camera access outside of Camera scope must lead to a VmbTimeout
        with self.cam:
            self.assertRaises(VmbTimeout, self.cam.get_frame, 1)

    def test_camera_is_streaming(self):
        # Expectation: After start_streaming() is_streaming() must return true. After stop it must
        # return false. If the camera context is left without stop_streaming(), leaving
        # the context must stop streaming.

        # Normal Operation
        self.assertEqual(self.cam.is_streaming(), False)
        with self.cam:
            self.cam.start_streaming(dummy_frame_handler)
            self.assertEqual(self.cam.is_streaming(), True)
            # Wait a little bit before stopping the stream again to give camera time to settle
            time.sleep(0.1)

            self.cam.stop_streaming()
            self.assertEqual(self.cam.is_streaming(), False)

        # Missing the stream stop. Close must stop streaming
        with self.cam:
            self.cam.start_streaming(dummy_frame_handler, 5)
            self.assertEqual(self.cam.is_streaming(), True)

        self.assertEqual(self.cam.is_streaming(), False)

    def test_camera_streaming_error_frame_count(self):
        # Expectation: A negative or zero frame_count must lead to an value error
        with self.cam:
            self.assertRaises(ValueError, self.cam.start_streaming, dummy_frame_handler, 0)
            self.assertRaises(ValueError, self.cam.start_streaming, dummy_frame_handler, -1)

    def test_camera_streaming(self):
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

        with self.cam:
            try:
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                self.cam.start_streaming(handler, frame_count)

                # Wait until the FrameHandler has been executed for each queued frame
                self.assertTrue(handler.event.wait(timeout),
                                'Handler event was not set. Frame count was not reached')

            finally:
                self.cam.stop_streaming()

    def test_camera_streaming_queue(self):
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

                cam.queue_frame(frame)

        frame_count = 5
        frame_reuse = 2
        handler = FrameHandler(frame_count * frame_reuse)

        with self.cam:
            try:
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count * frame_reuse)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                self.cam.start_streaming(handler, frame_count)

                # Wait until the FrameHandler has been executed for each queued frame
                self.assertTrue(handler.event.wait(timeout))

            finally:
                self.cam.stop_streaming()

    def test_ensure_frame_ids_increment_by_one_each_time(self):
        # Expectation: Frame IDs increment by one for each received frame (this depends on a stable
        # stream with no lost frames!)

        class FrameHandler:
            def __init__(self, frame_count, test_instance):
                self.cnt = None
                self.frame_count = frame_count
                self._test_instance = test_instance
                self.event = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                if self.cnt is None:
                    # On first execution of callback, get first frame ID
                    self.cnt = frame.get_id()
                else:
                    # On subsequent executions ensure that the frame ID was incremented by exactly 1
                    self.cnt += 1
                    self._test_instance.assertEqual(self.cnt, frame.get_id())

                if self.cnt == self.frame_count:
                    self.event.set()

                cam.queue_frame(frame)

        frame_count = 5
        handler = FrameHandler(frame_count, self)
        with self.cam:
            try:
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                self.cam.start_streaming(handler, frame_count)

                # Wait until the FrameHandler has been executed for each queued frame
                self.assertTrue(handler.event.wait(timeout))

            finally:
                self.cam.stop_streaming()

    def test_camera_runtime_type_check(self):
        def valid_handler(cam, stream, frame):
            pass

        def invalid_handler_1(cam):
            pass

        def invalid_handler_2(cam, stream):
            pass

        def invalid_handler_3(cam, stream, frame, extra):
            pass

        self.assertRaises(TypeError, self.cam.set_access_mode, -1)

        with self.cam:
            # Expectation: raise TypeError on passing invalid parameters
            self.assertRaises(TypeError, self.cam.get_frame, 'hi')
            self.assertRaises(TypeError, self.cam.get_features_selected_by, 'No Feature')
            self.assertRaises(TypeError, self.cam.get_features_by_type, 0.0)
            self.assertRaises(TypeError, self.cam.get_feature_by_name, 0)
            self.assertRaises(TypeError, self.cam.start_streaming, valid_handler, 'no int')
            self.assertRaises(TypeError, self.cam.start_streaming, invalid_handler_1)
            self.assertRaises(TypeError, self.cam.start_streaming, invalid_handler_2)
            self.assertRaises(TypeError, self.cam.start_streaming, invalid_handler_3)
            self.assertRaises(TypeError, self.cam.save_settings, 0, PersistType.All)
            self.assertRaises(TypeError, self.cam.save_settings, 'foo.xml', 'false type')
            for args in (('3',), (1, 'foo')):
                with self.assertRaises(TypeError):
                    for _ in self.cam.get_frame_generator(*args):
                        pass

    def test_callback_parameter_types(self):
        # Expectation: All parameters of the frame callback are of instances of their expected type
        class FrameHandler:
            def __init__(self, test_instance):
                self._test_instance = test_instance
                self.event = threading.Event()

            def __call__(self, cam: Camera, stream: Stream, frame: Frame):
                self._test_instance.assertIsInstance(cam, Camera)
                self._test_instance.assertIsInstance(stream, Stream)
                self._test_instance.assertIsInstance(frame, Frame)

                self.event.set()

        frame_count = 5
        handler = FrameHandler(self)
        with self.cam:
            try:
                try:
                    timeout = calculate_acquisition_time(self.cam, frame_count)
                    # Add one second extra time for acquisition overhead and additional 10% buffer
                    timeout = 1.1 * (1.0 + timeout)
                except VmbFeatureError:
                    timeout = 5.0
                self.cam.start_streaming(handler, frame_count)

                # Wait until the FrameHandler has been executed for each queued frame
                self.assertTrue(handler.event.wait(timeout))

            finally:
                self.cam.stop_streaming()

    def test_camera_context_manager_reentrancy(self):
        # Expectation: Camera Context Manager must be reentrant. Multiple calls to _open
        # must be prevented (would cause VmbC - Error)
        with self.cam:
            with self.cam:
                with self.cam:
                    pass

    def test_camera_api_context_sensitivity_outside_context(self):
        # Expectation: Call set_access_mode withing with scope must raise a RuntimeError
        with self.cam:
            self.assertRaises(RuntimeError, self.cam.set_access_mode)

    def test_camera_api_context_sensitivity_inside_context(self):
        # Expectation: Most Camera related functions are only valid then called within the given
        # Context. If called from Outside a runtime error must be raised.
        self.assertRaises(RuntimeError, self.cam.get_streams)
        self.assertRaises(RuntimeError, self.cam.get_local_device)
        self.assertRaises(RuntimeError, self.cam.read_memory)
        self.assertRaises(RuntimeError, self.cam.write_memory)
        self.assertRaises(RuntimeError, self.cam.get_all_features)
        self.assertRaises(RuntimeError, self.cam.get_features_selected_by)
        self.assertRaises(RuntimeError, self.cam.get_features_by_type)
        self.assertRaises(RuntimeError, self.cam.get_features_by_category)
        self.assertRaises(RuntimeError, self.cam.get_feature_by_name)
        self.assertRaises(RuntimeError, self.cam.get_frame)
        self.assertRaises(RuntimeError, self.cam.start_streaming)
        self.assertRaises(RuntimeError, self.cam.stop_streaming)
        self.assertRaises(RuntimeError, self.cam.queue_frame)
        self.assertRaises(RuntimeError, self.cam.get_pixel_formats)
        self.assertRaises(RuntimeError, self.cam.get_pixel_format)
        self.assertRaises(RuntimeError, self.cam.set_pixel_format)
        self.assertRaises(RuntimeError, self.cam.save_settings)
        self.assertRaises(RuntimeError, self.cam.load_settings)
        with self.assertRaises(RuntimeError):
            for _ in self.cam.get_frame_generator():
                pass
