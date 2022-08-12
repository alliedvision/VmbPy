from vmbpy import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class PersistableFeatureContainerTest(VmbPyTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.vmb = VmbSystem.get_instance()
        cls.vmb._startup()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.vmb._shutdown()
        super().tearDownClass()

    def test_transport_layer_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        for tl in self.vmb.get_all_transport_layers():
            with self.subTest(f'transport_layer={str(tl)}'):
                fname = 'transport_layer.xml'
                tl.save_settings(fname)
                # Room for improvement: Unfortunately there is no generic writeable feature that
                # every interface supports that we can modify here to check that loading the
                # settings resets the feature to the original value. So we just load again and if no
                # errors occur assume the test to be passed.
                tl.load_settings(fname)

                os.remove(fname)

    def test_interface_save_load(self):
        # Expectation: Settings can be saved to a file and loaded from it.
        for inter in self.vmb.get_all_interfaces():
            with self.subTest(f'interface={str(inter)}'):
                fname = 'interface.xml'
                inter.save_settings(fname)
                # Room for improvement: Unfortunately there is no generic writeable feature that
                # every interface supports that we can modify here to check that loading the
                # settings resets the feature to the original value. So we just load again and if no
                # errors occur assume the test to be passed.
                inter.load_settings(fname)

                os.remove(fname)

    def test_save_settings_type_error(self):
        # Expectation: Using parameters with incorrect type raises a TypeError
        # Use a transport layer to access save settings. Precise class does not matter. It only
        # needs to provide access to the method
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(TypeError, tl.save_settings, 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', PersistType.All, 123)
        self.assertRaises(TypeError, tl.save_settings, 'foo.xml', PersistType.All, ModulePersistFlags.None_, 'foo')

    def test_load_settings_type_error(self):
        # Expectation: Using parameters with incorrect type raises a TypeError
        # Use a transport layer to access save settings. Precise class does not matter. It only
        # needs to provide access to the method
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(TypeError, tl.load_settings, 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', PersistType.All, 123)
        self.assertRaises(TypeError, tl.load_settings, 'foo.xml', PersistType.All, ModulePersistFlags.None_, 'foo')

    def test_save_settings_verify_path(self):
        # Expectation: Valid files end with .xml and can be either a absolute path or relative
        # path to the given File. Everything else is a ValueError.

        valid_paths = (
            'valid1.xml',
            os.path.join('.', 'valid2.xml'),
            os.path.join('Tests', 'valid3.xml'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valid4.xml'),
        )
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(ValueError, tl.save_settings, 'inval.xm')

        for path in valid_paths:
            self.assertNoRaise(tl.save_settings, path)
            os.remove(path)

    def test_load_settings_verify_path(self):
        # Expectation: Valid files end with .xml and must exist before before any execution.
        valid_paths = (
            'valid1.xml',
            os.path.join('.', 'valid2.xml'),
            os.path.join('Tests', 'valid3.xml'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valid4.xml'),
        )
        tl = self.vmb.get_all_transport_layers()[0]
        self.assertRaises(ValueError, tl.load_settings, 'inval.xm', PersistType.All)

        for path in valid_paths:
            self.assertRaises(ValueError, tl.load_settings, path, PersistType.All)

        for path in valid_paths:
            tl.save_settings(path, PersistType.All)

            self.assertNoRaise(tl.load_settings, path, PersistType.All)
            os.remove(path)