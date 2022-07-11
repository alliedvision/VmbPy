from .error import VmbFeatureError
from .feature import FeaturesTuple, FeatureTypes, FeatureTypeTypes
from .shared import filter_features_by_name, filter_features_by_type, filter_selected_features, \
                    filter_features_by_category
from .util import TraceEnable, RuntimeTypeCheckEnable


__all__ = [
    'FeatureContainer',
    'PersistableFeatureContainer'
]


class FeatureContainer:
    def __init__(self) -> None:
        self._feats: FeaturesTuple = ()

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
    def load_settings(self):
        pass

    def save_settings(self):
        pass
