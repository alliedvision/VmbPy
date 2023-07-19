from helpers import VmbPyTestCase
import os
import sys

from vmbpy import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class EnumTest(VmbPyTestCase):
    def test_string_representation_includes_entry_name(self):
        # Expectation: Converting an enum to a string includes the name of the entry in the
        # generated string.
        enums_to_test = (AccessMode,
                         AllocationMode,
                         CameraEvent,
                         Debayer,
                         FeatureVisibility,
                         FrameStatus,
                         InterfaceEvent,
                         LogLevel,
                         ModulePersistFlags,
                         PersistType,
                         PixelFormat,
                         TransportLayerType
                         )
        for enum in enums_to_test:
            for entry in enum:
                print(entry)
                self.assertIn(entry._name_, str(entry))
