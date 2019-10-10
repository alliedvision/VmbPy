import unittest

from vimba import *

class TlVimbaTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()

    def tearDown(self):
        self.vimba.set_camera_access_mode(AccessMode.Full)
        self.vimba.set_camera_capture_timeout(2000)

    def test_context_entry_exit(self):
        """ Expected Behavior for FileTL:
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
        """Expected Behavior for FileTL:

        get_all_interfaces() must contains an interface with id 'VimbaFileInterface_0'.
        """
        expected = 'VimbaFileInterface_0'

        with self.vimba:
            inters = [i for i in self.vimba.get_all_interfaces() if i.get_id() in expected]
            self.assertEqual(len(inters), 1)

    def test_get_interface_by_id(self):
        """Expected Behavior for FileTL:

        get_interface_by_id() returns interface 'VimbaFileInterface_0' inside scope.
        """
        expected = 'VimbaFileInterface_0'

        self.assertRaises(VimbaInterfaceError, self.vimba.get_interface_by_id, 'VimbaFileInterface_0')

        with self.vimba:
            self.assertNoRaise(self.vimba.get_interface_by_id, 'VimbaFileInterface_0')

        self.assertRaises(VimbaInterfaceError, self.vimba.get_interface_by_id, 'VimbaFileInterface_0')


    def test_get_all_cameras(self):
        """Expected Behavior for FileTL:

        get_all_cameras() contains cameras with Id: 'DEV_Testimage1' and 'DEV_Testimage2'.
        """
        expected = ('DEV_Testimage1', 'DEV_Testimage2')

        with self.vimba:
            cams = [c for c in self.vimba.get_all_cameras() if c.get_id() in expected]
            self.assertEqual(len(cams), 2)

    def test_get_camera_by_id(self):
        """Expected Behavior for FileTL:

        get_camera_by_id() returns cameras 'DEV_Testimage1' and 'DEV_Testimage2' inside scope.
        """
        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, 'DEV_Testimage1')
        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, 'DEV_Testimage2')

        with self.vimba:
            self.assertNoRaise(self.vimba.get_camera_by_id, 'DEV_Testimage1')
            self.assertNoRaise(self.vimba.get_camera_by_id, 'DEV_Testimage2')

        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, 'DEV_Testimage1')
        self.assertRaises(VimbaCameraError, self.vimba.get_camera_by_id, 'DEV_Testimage2')
