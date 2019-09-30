import unittest

from vimba import *
from vimba.frame import *

class TlCameraTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        self.cam = self.vimba.get_camera_by_id('DEV_Testimage1')
        self.cam.set_access_mode(AccessMode.Full)
        self.cam.set_capture_timeout(2000)

        self.other_cam = self.vimba.get_camera_by_id('DEV_Testimage2')
        self.other_cam.set_access_mode(AccessMode.Full)
        self.other_cam.set_capture_timeout(2000)

    def tearDown(self):
        self.vimba._shutdown()

    def test_context_manager_access_mode(self):
        """Expectation: Entering Context must not throw in cases where the current access mode is
        within get_permitted_access_modes()
        """

        permitted_modes = self.cam.get_permitted_access_modes()

        # There are some known Issues regarding permissions from the underlaying C-Layer.
        # Filter buggy modes. This is a VimbaC issue not a VimbaPython issue
        permitted_modes = [p for p in permitted_modes if p not in (AccessMode.Lite,)]

        for mode in permitted_modes:
            self.cam.set_access_mode(mode)

            try:
                with self.cam:
                    pass

            except BaseException as e:
                self.fail()

    def test_context_manager_feature_discovery(self):
        """Expectation: Outside of context, all features must be cleared,
        inside of context all features must be detected.
        """

        self.assertEqual(self.cam.get_all_features(), ())

        with self.cam:
            self.assertNotEqual(self.cam.get_all_features(), ())

        self.assertEqual(self.cam.get_all_features(), ())

    def test_access_mode(self):
        """Expectation: set/get access mode"""
        self.cam.set_access_mode(AccessMode.None_)
        self.assertEqual(self.cam.get_access_mode(), AccessMode.None_)
        self.cam.set_access_mode(AccessMode.Full)
        self.assertEqual(self.cam.get_access_mode(), AccessMode.Full)
        self.cam.set_access_mode(AccessMode.Read)
        self.assertEqual(self.cam.get_access_mode(), AccessMode.Read)

    def test_capture_timeout(self):
        """Expectation: set/get access mode"""
        self.cam.set_capture_timeout(2001)
        self.assertEqual(self.cam.get_capture_timeout(), 2001)

        self.assertRaises(ValueError, self.cam.set_capture_timeout, 0)
        self.assertRaises(ValueError, self.cam.set_capture_timeout, -1)

        self.assertEqual(self.cam.get_capture_timeout(), 2001)


    def test_get_id(self):
        """Expectation: get decoded camera id"""
        self.assertEqual(self.cam.get_id(),'DEV_Testimage1')

    def test_get_name(self):
        """Expectation: get decoded camera name"""
        self.assertEqual(self.cam.get_name(),'AVT Testimage1')

    def test_get_model(self):
        """Expectation: get decoded camera model"""
        self.assertEqual(self.cam.get_model(),'Testimage1')

    def test_get_serial(self):
        """Expectation: get decoded camera serial"""
        self.assertEqual(self.cam.get_serial(), 'N/A')

    def test_get_permitted_access_modes(self):
        """Expectation: get currently permitted access modes"""
        expected = (AccessMode.Full, AccessMode.Read, AccessMode.Lite)
        self.assertEqual(self.cam.get_permitted_access_modes(), expected)

    def test_get_interface_id(self):
        """Expectation: get interface Id this camera is connected to"""
        self.assertEqual(self.cam.get_interface_id(), 'VimbaFileInterface_0')

    def test_get_features_affected(self):
        """Expectation: Features that affect other features shall return a set of affected feature
        Features that don't affect other features shall return (). If a Feature is supplied that
        is not associated with that camera, a TypeError must be raised.
        """
        with self.cam:
            affect = self.cam.get_feature_by_name('Height')
            not_affect = self.cam.get_feature_by_name('AcquisitionFrameCount')

            self.assertEqual(self.cam.get_features_affected_by(not_affect), ())

            expected = (
                self.cam.get_feature_by_name('PacketSize'),
                self.cam.get_feature_by_name('PayloadSize')
            )

            for feat in self.cam.get_features_affected_by(affect):
                self.assertIn(feat, expected)

            with self.other_cam:

                self.assertRaises(
                    VimbaFeatureError,
                    self.cam.get_features_affected_by,
                    self.other_cam.get_feature_by_name('Height')
                )

                self.assertRaises(
                    VimbaFeatureError,
                    self.cam.get_features_affected_by,
                    self.other_cam.get_feature_by_name('AcquisitionFrameCount')
                )

    def test_get_features_selected(self):
        """Expectation: Features that select other features shall return a set of select feature
        Features that don't select other features shall return (). If a Feature is supplied that
        is not associated with that camera, a TypeError must be raised.
        Note: FileTL offers no selected Features. All so most of it is not testable.
        """
        with self.cam:
            not_select = self.cam.get_feature_by_name('DeviceID')

            self.assertEqual(self.cam.get_features_selected_by(not_select), ())

            with self.other_cam:

                self.assertRaises(
                    VimbaFeatureError,
                    self.cam.get_features_selected_by,
                    self.other_cam.get_feature_by_name('DeviceID')
                )

    def test_frame_iterator_limit_set(self):
        """Expectation: The Frame Iterator fetches the given number of images."""
        with self.cam:
            self.assertEqual(len([i for i in self.cam.get_frame_iter(0)]), 0)
            self.assertEqual(len([i for i in self.cam.get_frame_iter(1)]), 1)
            self.assertEqual(len([i for i in self.cam.get_frame_iter(7)]), 7)
            self.assertEqual(len([i for i in self.cam.get_frame_iter(11)]), 11)

    def test_frame_iterator_error(self):
        """Expectation: The Frame Iterator raises a VimbaCameraError on a
        negative limit and the camera raises an VimbaCameraError
        if the camera is not opened.
        """
        # Check limits
        self.assertRaises(ValueError, self.cam.get_frame_iter, -1)

        # Usage on closed camera
        try:
            [i for i in self.cam.get_frame_iter(1)]
            self.fail('Generator expression on closed camera must raise')

        except VimbaCameraError:
            pass

    def test_get_frame(self):
        """Expectation: Gets single Frame without any exception. Image data must be set"""
        with self.cam:
            self.assertNoRaise(self.cam.get_frame)
            self.assertEqual(type(self.cam.get_frame()), Frame)


    def test_capture_error_outside_vimba_scope(self):
        """Expectation: Camera access outside of Vimba scope must lead to a VimbaSystemError"""
        frame_iter = None

        with self.cam:
            frame_iter = self.cam.get_frame_iter(1)

        # Shutdown API
        self.vimba._shutdown()

        # Access invalid Iterator
        self.assertRaises(VimbaSystemError, frame_iter.__next__)

    def test_capture_error_outside_camera_scope(self):
        """Expectation: Camera access outside of Camera scope must lead to a VimbaCameraError"""
        frame_iter = None

        with self.cam:
            frame_iter = self.cam.get_frame_iter(1)

        self.assertRaises(VimbaCameraError, frame_iter.__next__)

    def test_capture_timeout(self):
        """Expectation: Camera access outside of Camera scope must lead to a VimbaCameraError"""
        self.cam.set_capture_timeout(1)

        with self.cam:
            self.assertRaises(VimbaTimeout, self.cam.get_frame)


    @unittest.skip('Fix me')
    def test_runtime_type_check(self):
        """Expectation: raise TypeError on passing invalid parameters"""
        self.assertRaises(TypeError,  self.cam.set_access_mode, -1)
        self.assertRaises(TypeError,  self.cam.set_capture_timeout_millisec, 'hi')
        self.assertRaises(TypeError,  self.cam.get_features_affected_by, 'No Feature')
        self.assertRaises(TypeError,  self.cam.get_features_selected_by, 'No Feature')
        self.assertRaises(TypeError,  self.cam.get_features_by_type, 0.0)
        self.assertRaises(TypeError,  self.cam.get_feature_by_name, 0)
        self.assertRaises(TypeError,  self.cam.get_frame_iter, '3')

        def func_err(no_cam: Frame,  no_frame: Camera):
            pass

        def func_ok(cam: Camera,  frame: Frame):
            pass

        self.assertRaises(TypeError,  self.cam.start_streaming, func_err, 3)
        self.assertRaises(TypeError,  self.cam.start_streaming, func_ok, 'no int')
