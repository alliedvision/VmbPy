import unittest

from vimba import *

class TlVimbaTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        vimba = Vimba.get_instance()
        vimba.set_camera_access_mode(AccessMode.Full)
        vimba.set_camera_capture_timeout(2000)

    def test_context_entry_exit(self):
        """ Expected Behavior for FileTL:
        Before context entry Vimba shall have no detected features, no detected cameras and
        no detected Interfaces. On entering the context features, cameras and interfaces shall
        be detected and after leaving the context, everything should be reverted.
        """

        vimba = Vimba.get_instance()

        self.assertEqual(vimba.get_all_features(), ())
        self.assertEqual(vimba.get_all_interfaces(), ())
        self.assertEqual(vimba.get_all_cameras(), ())

        with vimba:
            self.assertNotEqual(vimba.get_all_features(), ())
            self.assertNotEqual(vimba.get_all_interfaces(), ())
            self.assertNotEqual(vimba.get_all_cameras(), ())

        self.assertEqual(vimba.get_all_features(), ())
        self.assertEqual(vimba.get_all_interfaces(), ())
        self.assertEqual(vimba.get_all_cameras(), ())

    def test_global_value_propagation(self):
        """Expectation: Global Settings in Vimba are passed down to discovered entities"""
        vimba = Vimba.get_instance()
        vimba.set_camera_access_mode(AccessMode.Read)

        with vimba:
            for cam in vimba.get_all_cameras():
                self.assertEqual(cam.get_access_mode(), vimba.get_camera_access_mode())

        vimba.set_camera_capture_timeout(100)

        with vimba:
            for cam in vimba.get_all_cameras():
                self.assertEqual(cam.get_capture_timeout(), vimba.get_camera_capture_timeout())

    def test_get_all_interfaces(self):
        """Expected Behavior for FileTL:

        get_all_interfaces() must contains an interface with id 'VimbaFileInterface_0'.
        """
        expected = 'VimbaFileInterface_0'

        vimba = Vimba.get_instance()

        with vimba:
            inters = [i for i in vimba.get_all_interfaces() if i.get_id() in expected]
            self.assertEqual(len(inters), 1)

    def test_get_interface_by_id(self):
        """Expected Behavior for FileTL:

        get_interface_by_id() returns interface 'VimbaFileInterface_0' inside scope.
        """
        expected = 'VimbaFileInterface_0'

        vimba = Vimba.get_instance()

        self.assertRaises(VimbaInterfaceError, vimba.get_interface_by_id, 'VimbaFileInterface_0')

        with vimba:
            self.assertNoRaise(vimba.get_interface_by_id, 'VimbaFileInterface_0')

        self.assertRaises(VimbaInterfaceError, vimba.get_interface_by_id, 'VimbaFileInterface_0')


    def test_get_all_cameras(self):
        """Expected Behavior for FileTL:

        get_all_cameras() contains cameras with Id: 'DEV_Testimage1' and 'DEV_Testimage2'.
        """
        expected = ('DEV_Testimage1', 'DEV_Testimage2')
        vimba = Vimba.get_instance()

        with vimba:
            cams = [c for c in vimba.get_all_cameras() if c.get_id() in expected]
            self.assertEqual(len(cams), 2)

    def test_get_camera_by_id(self):
        """Expected Behavior for FileTL:

        get_camera_by_id() returns cameras 'DEV_Testimage1' and 'DEV_Testimage2' inside scope.
        """
        vimba = Vimba.get_instance()

        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'DEV_Testimage1')
        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'DEV_Testimage2')

        with vimba:
            self.assertNoRaise(vimba.get_camera_by_id, 'DEV_Testimage1')
            self.assertNoRaise(vimba.get_camera_by_id, 'DEV_Testimage2')

        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'DEV_Testimage1')
        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'DEV_Testimage2')
