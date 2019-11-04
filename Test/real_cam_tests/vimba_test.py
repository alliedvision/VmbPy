import unittest

from vimba import *

class RealCamTestsVimbaTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()

    def tearDown(self):
        self.vimba.set_camera_access_mode(AccessMode.Full)
        self.vimba.set_camera_capture_timeout(2000)

    def test_context_entry_exit(self):
        """ Expected Behavior:
        Before context entry Vimba shall have no detected features, no detected cameras and
        no detected Interfaces. On entering the context features, cameras and interfaces shall
        be detected and after leaving the context, everything should be reverted.
        """
        self.assertEqual(self.vimba.get_all_features(), ())
        self.assertEqual(self.vimba.get_all_interfaces(), ())
        self.assertEqual(self.vimba.get_all_cameras(), ())

        with self.vimba:
            self.assertNotEqual(self.vimba.get_all_features(), ())
            self.assertNotEqual(self.vimba.get_all_interfaces(), ())
            self.assertNotEqual(self.vimba.get_all_cameras(), ())

        self.assertEqual(self.vimba.get_all_features(), ())
        self.assertEqual(self.vimba.get_all_interfaces(), ())
        self.assertEqual(self.vimba.get_all_cameras(), ())

    def test_global_value_propagation(self):
        """Expectation: Global Settings in Vimba are passed down to discovered entities"""
        self.vimba.set_camera_access_mode(AccessMode.Read)

        with self.vimba:
            for cam in self.vimba.get_all_cameras():
                self.assertEqual(cam.get_access_mode(), self.vimba.get_camera_access_mode())

        self.vimba.set_camera_capture_timeout(100)

        with self.vimba:
            for cam in self.vimba.get_all_cameras():
                self.assertEqual(cam.get_capture_timeout(), self.vimba.get_camera_capture_timeout())

    def test_get_all_interfaces(self):
        """Expected Behavior: get_all_interfaces() must be empty in closed state and
           non-empty then opened.
        """
        self.assertFalse(self.vimba.get_all_interfaces())

        with self.vimba:
            self.assertTrue(self.vimba.get_all_interfaces())

    def test_get_interface_by_id(self):
        """Expected Behavior: All detected Interfaces must be lookupable by their Id.

        If outside of given scope, an errpr must be returned
        """

        with self.vimba:
            ids = [inter.get_id() for inter in self.vimba.get_all_interfaces()]

            for id_ in ids:
                self.assertNoRaise(self.vimba.get_interface_by_id, id_)

        for id_ in ids:
            self.assertRaises(VimbaInterfaceError, self.vimba.get_interface_by_id, id_)


    def test_get_all_cameras(self):
        """Expected Behavior: get_all_cameras() must only return camera handles on a open camera.
        """
        self.assertFalse(self.vimba.get_all_cameras())

        with self.vimba:
            self.assertTrue(self.vimba.get_all_cameras())

    def test_get_camera_by_id(self):
        """Expected Behavior: Lookup of test camera must not fail after system opening """
        camera_id = self.get_test_camera_id()
        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, camera_id)

        with self.vimba:
            self.assertNoRaise(self.vimba.get_camera_by_id, camera_id)

        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, camera_id)

