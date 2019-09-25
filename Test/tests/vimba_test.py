import unittest

from vimba import *

class VimbaTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_singleton(self):
        """Expected behavior: Multiple calls to Vimba.get_instance() return the same object."""
        self.assertEqual(Vimba.get_instance(), Vimba.get_instance())

    def test_get_camera_by_id_failure(self):
        """Expected behavior: Lookup of a currently unavailable camera must throw an
        VimbaCameraError regardless of context.
        """
        vimba = Vimba.get_instance()

        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'Invalid ID')

        with vimba:
            self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'Invalid ID')

        self.assertRaises(VimbaCameraError, vimba.get_camera_by_id, 'Invalid ID')

    def test_get_interface_by_id_failure(self):
        """Expected behavior: Lookup of a currently unavailable interface must throw an
        VimbaInterfaceError regardless of context.
        """
        vimba = Vimba.get_instance()

        self.assertRaises(VimbaInterfaceError, vimba.get_interface_by_id, 'Invalid ID')

        with vimba:
            self.assertRaises(VimbaInterfaceError, vimba.get_interface_by_id, 'Invalid ID')

        self.assertRaises(VimbaInterfaceError, vimba.get_interface_by_id, 'Invalid ID')

    def test_get_feature_by_name_failure(self):
        """Expected behavior: Lookup of a currently unavailable feature must throw an
        VimbaFeatureError regardless of context.
        """
        vimba = Vimba.get_instance()

        self.assertRaises(VimbaFeatureError, vimba.get_feature_by_name, 'Invalid ID')

        with vimba:
            self.assertRaises(VimbaFeatureError, vimba.get_feature_by_name, 'Invalid ID')

        self.assertRaises(VimbaFeatureError, vimba.get_feature_by_name, 'Invalid ID')

    def test_runtime_check_failure(self):
        """All functions with RuntimeTypeCheckEnable must return a TypeError on Failure"""
        vimba = Vimba.get_instance()

        self.assertRaises(TypeError, vimba.set_camera_access_mode, 'RootAccess')
        self.assertRaises(TypeError, vimba.set_network_discovery, 0.0)
        self.assertRaises(TypeError, vimba.get_camera_by_id, 0)
        self.assertRaises(TypeError, vimba.get_interface_by_id, 1)
        self.assertRaises(TypeError, vimba.get_feature_by_name, 0)
        self.assertRaises(TypeError, vimba.enable_log, '-1')

        self.assertRaises(TypeError, vimba.get_features_affected_by, '-1')
        self.assertRaises(TypeError, vimba.get_features_selected_by, '-1')
        self.assertRaises(TypeError, vimba.get_features_by_type, [])
        self.assertRaises(TypeError, vimba.register_camera_change_handler, 0)
        self.assertRaises(TypeError, vimba.unregister_camera_change_handler, 0)
        self.assertRaises(TypeError, vimba.register_interface_change_handler, 0)
        self.assertRaises(TypeError, vimba.unregister_interface_change_handler, 0)
