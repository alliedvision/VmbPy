from .error import VmbFeatureError
from .feature import FeaturesTuple, FeatureTypes, FeatureTypeTypes, discover_features
from .shared import filter_features_by_name, filter_features_by_type, filter_selected_features, \
                    filter_features_by_category, attach_feature_accessors, remove_feature_accessors
from .util import TraceEnable, RuntimeTypeCheckEnable


__all__ = [
    'FeatureContainer',
    'PersistableFeatureContainer'
]


class FeatureContainer:
    """This class provides access to VmbC features available via self._handle

    Features discovery must be performed manually by calling `_attach_feature_accessors`. This
    should be done when an appropriate classes context is entered.  This requires that the VmbHandle
    for the object is stored in self._handle. Detected features are stored in self._feats and
    attached as class members. Removing the attached features again is done via
    `_remove_feature_accessors`. This should be done when the above mentioned context is left.
    """
    @TraceEnable()
    def __init__(self) -> None:
        self._feats: FeaturesTuple = ()

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
        """Get access to all discovered system features:

        Returns:
            A set of all currently detected Features.

        Raises:
            RuntimeError then called outside of "with" - statement.
        """
        return self._feats

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all system features selected by a specific system feature.

        Arguments:
            feat - Feature used find features that are selected by feat.

        Returns:
            A set of features selected by 'feat'.

        Raises:
            TypeError if parameters do not match their type hint.
            RuntimeError then called outside of "with" - statement.
            VmbFeatureError if 'feat' is not a system feature.
        """
        return filter_selected_features(self._feats, feat)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypeTypes) -> FeaturesTuple:
        """Get all system features of a specific feature type.

        Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
        EnumFeature, CommandFeature, RawFeature

        Arguments:
            feat_type - FeatureType used find features of that type.

        Returns:
            A set of features of type 'feat_type'.

        Raises:
            TypeError if parameters do not match their type hint.
            RuntimeError then called outside of "with" - statement.
        """
        return filter_features_by_type(self._feats, feat_type)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_features_by_category(self, category: str) -> FeaturesTuple:
        """Get all system features of a specific category.

        Arguments:
            category - Category that should be used for filtering.

        Returns:
            A set of features of category 'category'.

        Returns:
            TypeError if parameters do not match their type hint.
            RuntimeError then called outside of "with" - statement.
        """
        return filter_features_by_category(self._feats, category)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get a system feature by its name.

        Arguments:
            feat_name - Name used to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError if parameters do not match their type hint.
            RuntimeError then called outside of "with" - statement.
            VmbFeatureError if no feature is associated with 'feat_name'.
        """
        feat = filter_features_by_name(self._feats, feat_name)

        if not feat:
            raise VmbFeatureError('Feature \'{}\' not found.'.format(feat_name))

        return feat


class PersistableFeatureContainer(FeatureContainer):
    """Inheriting from this class adds load/save settings methods to the subclass
    """
    def load_settings(self):
        pass

    def save_settings(self):
        pass
