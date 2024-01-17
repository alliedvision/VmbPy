"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
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
from ctypes import byref, sizeof

from .c_binding import (ModulePersistFlags, PersistType, VmbFeaturePersistSettings,
                        _as_vmb_file_path, call_vmb_c, VmbHandle)
from .error import VmbFeatureError
from .feature import FeaturesTuple, FeatureTypes, FeatureTypeTypes, discover_features
from .shared import (attach_feature_accessors, filter_features_by_category, filter_features_by_name,
                     filter_features_by_type, filter_selected_features, remove_feature_accessors)
from .util import RuntimeTypeCheckEnable, TraceEnable

__all__ = [
    'FeatureContainer',
    'PersistableFeatureContainer',
    'PersistType',
    'ModulePersistFlags'
]


class FeatureContainer:
    """This class provides access to VmbC features available via self._handle

    Features discovery must be performed manually by calling ``_attach_feature_accessors``. This
    should be done when an appropriate classes context is entered.  This requires that the VmbHandle
    for the object is stored in ``self._handle``. Detected features are stored in ``self._feats``
    and attached as class members. Removing the attached features again is done via
    ``_remove_feature_accessors``. This should be done when the above mentioned context is left.
    """
    @TraceEnable()
    def __init__(self) -> None:
        self._feats: FeaturesTuple = ()
        self._handle = VmbHandle(0)
        self.__context_cnt: int = 0

    @TraceEnable()
    def _attach_feature_accessors(self):
        if not self.__context_cnt:
            self._feats = discover_features(self._handle)
            attach_feature_accessors(self, self._feats)

        self.__context_cnt += 1
        return self

    @TraceEnable()
    def _remove_feature_accessors(self):
        self.__context_cnt -= 1

        if not self.__context_cnt:
            remove_feature_accessors(self, self._feats)

    @TraceEnable()
    def get_all_features(self) -> FeaturesTuple:
        """Get access to all discovered features.

        Returns:
            A set of all currently detected Features.

        Raises:
            RuntimeError:
                If called outside of ``with`` context.
        """
        return self._feats

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features selected by a specific feature.

        Arguments:
            feat:
                Feature used to find features that are selected by ``feat``.

        Returns:
            A set of features selected by ``feat``.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside of ``with`` context.
            VmbFeatureError:
                If ``feat`` is not a valid feature.
        """
        return filter_selected_features(self._feats, feat)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypeTypes) -> FeaturesTuple:
        """Get all features of a specific feature type.

        Valid FeatureTypes are: ``IntFeature``, ``FloatFeature``, ``StringFeature``,
        ``BoolFeature``, ``EnumFeature``, ``CommandFeature``, ``RawFeature``

        Arguments:
            feat_type:
                FeatureType used to find features of that type.

        Returns:
            A set of features of type `feat_type``.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside of ``with`` context.
        """
        return filter_features_by_type(self._feats, feat_type)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_by_category(self, category: str) -> FeaturesTuple:
        """Get all features of a specific category.

        Arguments:
            category:
                Category that should be used for filtering.

        Returns:
            A set of features of category ``category``.

        Raises:
            TypeError
                If parameters do not match their type hint.
            RuntimeError
                If called outside of ``with`` context.
        """
        return filter_features_by_category(self._feats, category)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get a feature by its name.

        Arguments:
            feat_name:
                Name used to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside of ``with`` context.
            VmbFeatureError:
                If no feature is associated with ``feat_name``.
        """
        feat = filter_features_by_name(self._feats, feat_name)

        if not feat:
            raise VmbFeatureError('Feature \'{}\' not found.'.format(feat_name))

        return feat


class PersistableFeatureContainer(FeatureContainer):
    """Inheriting from this class adds load/save settings methods to the subclass"""
    @RuntimeTypeCheckEnable()
    def load_settings(self,
                      file_path: str,
                      persist_type: PersistType = PersistType.Streamable,
                      persist_flags: ModulePersistFlags = ModulePersistFlags.None_,
                      max_iterations: int = 0):
        """Load settings from XML file.

        Arguments:
            file_path:
                The location for loading current settings. The given file must be a file ending with
                ".xml".
            persist_type:
                Parameter specifying which setting types to load. For an overview of the possible
                values and their implication see the ``PersistType`` enum
            persist_flags:
                Flags specifying the modules to load. By default only features of the calling module
                itself are persisted. For an overview of available flags see the
                ``ModulePersistFlags`` type
            max_iterations:
                Number of iterations when storing settings. If 0 is given (default) the value found
                in the XML file is used

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If argument path is no ".xml" file.
         """
        if not file_path.endswith('.xml'):
            raise ValueError('Given file \'{}\' must end with \'.xml\''.format(file_path))

        if not os.path.exists(file_path):
            raise ValueError('Given file \'{}\' does not exist.'.format(file_path))

        settings = VmbFeaturePersistSettings()
        settings.persistType = persist_type
        settings.persistFlag = persist_flags
        settings.maxIterations = max_iterations

        call_vmb_c('VmbSettingsLoad',
                   self._handle,
                   _as_vmb_file_path(file_path),
                   byref(settings),
                   sizeof(settings))

    @RuntimeTypeCheckEnable()
    def save_settings(self,
                      file_path: str,
                      persist_type: PersistType = PersistType.Streamable,
                      persist_flags: ModulePersistFlags = ModulePersistFlags.None_,
                      max_iterations: int = 0):
        """Save settings to XML File.

        Arguments:
            file_path:
                The location for storing the current settings. The given file must be a file ending
                with ".xml".
            persist_type:
                Parameter specifying which setting types to store. For an overview of the possible
                values and their implication see the ``PersistType`` enum
            persist_flags:
                Flags specifying the modules to store. By default only features of the calling
                module itself are persisted. For an overview of available flags see the
                ``ModulePersistFlags`` type
            max_iterations:
                Number of iterations when loading settings. If ``0`` is given (default) the VmbC
                default is used

        Raises:
            TypeError:
                If parameters do not match their type hint.
            RuntimeError:
                If called outside ``with`` context.
            ValueError:
                If argument path is no ".xml"- File.
         """
        if not file_path.endswith('.xml'):
            raise ValueError('Given file \'{}\' must end with \'.xml\''.format(file_path))

        settings = VmbFeaturePersistSettings()
        settings.persistType = persist_type
        settings.modulePersistFlags = persist_flags
        settings.maxIterations = max_iterations

        call_vmb_c('VmbSettingsSave',
                   self._handle,
                   _as_vmb_file_path(file_path),
                   byref(settings),
                   sizeof(settings))
