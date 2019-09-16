"""Various utility functions for Feature discovery and handling.

<Detailed Module description>

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

from itertools import product
from typing import Union, Tuple
from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbFeatureInfo, VmbFeatureData, VmbHandle, VmbUint32
from vimba.error import VimbaFeatureError
from .int_feature import IntFeature
from .float_feature import FloatFeature
from .string_feature import StringFeature
from .bool_feature import BoolFeature
from .enum_feature import EnumFeature
from .command_feature import CommandFeature
from .raw_feature import RawFeature

__all__ = [
    'FeatureTypes',
    'FeaturesTuple',
    'discover_features',
    'discover_feature',
    'filter_affected_features',
    'filter_selected_features',
    'filter_features_by_name',
    'filter_features_by_type'
]

FeatureTypes = Union[IntFeature, FloatFeature, StringFeature, BoolFeature, EnumFeature,
                     CommandFeature, RawFeature]

FeaturesTuple = Tuple[FeatureTypes, ...]


def _build_feature(handle: VmbHandle, info: VmbFeatureInfo) -> FeatureTypes:
    feat_value = VmbFeatureData(info.featureDataType)

    if VmbFeatureData.Int == feat_value:
        return IntFeature(handle, info)

    elif VmbFeatureData.Float == feat_value:
        return FloatFeature(handle, info)

    elif VmbFeatureData.String == feat_value:
        return StringFeature(handle, info)

    elif VmbFeatureData.Bool == feat_value:
        return BoolFeature(handle, info)

    elif VmbFeatureData.Enum == feat_value:
        return EnumFeature(handle, info)

    elif VmbFeatureData.Command == feat_value:
        return CommandFeature(handle, info)

    elif VmbFeatureData.Raw == feat_value:
        return RawFeature(handle, info)

    # This should never happen because all possible types are handled.
    # However the static type checker will not accept None as an return.
    raise VimbaFeatureError('Unhandled feature type.')


def discover_features(handle: VmbHandle) -> FeaturesTuple:
    """Discover all features associated with the given handle.

    Arguments:
        handle - Vimba entity used to find the associated features.

    Returns:
        A set of all discovered Features associated with handle.
    """
    result = []

    feats_count = VmbUint32(0)

    call_vimba_c_func('VmbFeaturesList', handle, None, 0, byref(feats_count),
                      sizeof(VmbFeatureInfo))

    if feats_count:
        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vimba_c_func('VmbFeaturesList', handle, feats_infos, feats_count,
                          byref(feats_found), sizeof(VmbFeatureInfo))

        for info in feats_infos[:feats_found.value]:
            result.append(_build_feature(handle, info))

    return tuple(result)


def discover_feature(handle: VmbHandle, feat_name: str) -> FeatureTypes:
    """Discover a singe feature associated with the given handle.

    Arguments:
        handle     - Vimba entity used to find the associated feature.
        feat_name: - Name of the Feature that should be searched.

    Returns:
        The Feature associated with 'handle' by the name of 'feat_name'
    """
    info = VmbFeatureInfo()

    call_vimba_c_func('VmbFeatureInfoQuery', handle, feat_name.encode('utf-8'),
                      byref(info), sizeof(VmbFeatureInfo))

    return _build_feature(handle, info)


def filter_affected_features(feats: FeaturesTuple, feat: FeatureTypes) -> FeaturesTuple:
    """Search for all Features affected by a given feature within a feature set.

    Arguments:
        feats: Feature set to search in.
        feat: Feature that might affect Features within 'feats'.

    Returns:
        A set of all features that are affected by 'feat'.

    Raises:
        VimbaFeatureError if 'feat' is not stored within 'feats'.
    """

    if feat not in feats:
        raise VimbaFeatureError('Feature \'{}\' not in given Features'.format(feat.get_name()))

    result = []

    if feat.has_affected_features():
        feats_count = VmbUint32()
        feats_handle = feat._handle
        feats_name = feat._info.name

        # Query affected features from given Feature
        call_vimba_c_func('VmbFeatureListAffected', feats_handle, feats_name,
                          None, 0, byref(feats_count), sizeof(VmbFeatureInfo))

        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vimba_c_func('VmbFeatureListAffected', feats_handle, feats_name,
                          feats_infos, feats_count, byref(feats_found),
                          sizeof(VmbFeatureInfo))

        # Search affected features in given feature set
        for info, feature in product(feats_infos[:feats_found.value], feats):
            if info.name == feature._info.name:
                result.append(feature)

    return tuple(result)


def filter_selected_features(feats: FeaturesTuple, feat: FeatureTypes) -> FeaturesTuple:
    """Search for all Features selected by a given feature within a feature set.

    Arguments:
        feats: Feature set to search in.
        feat: Feature that might select Features within 'feats'.

    Returns:
        A set of all features that are selected by 'feat'.

    Raises:
        VimbaFeatureError if 'feat' is not stored within 'feats'.
    """
    if feat not in feats:
        raise VimbaFeatureError('Feature \'{}\' not in given Features'.format(feat.get_name()))

    result = []

    if feat.has_selected_features():
        feats_count = VmbUint32()
        feats_handle = feat._handle
        feats_name = feat._info.name

        # Query selected features from given feature
        call_vimba_c_func('VmbFeatureListSelected', feats_handle, feats_name, None, 0,
                          byref(feats_count), sizeof(VmbFeatureInfo))

        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vimba_c_func('VmbFeatureListSelected', feats_handle, feats_name, feats_infos,
                          feats_count, byref(feats_found), sizeof(VmbFeatureInfo))

        # Search selected features in given feature set
        for info, feature in product(feats_infos[:feats_found.value], feats):
            if info.name == feature._info.name:
                result.append(feature)

    return tuple(result)


def filter_features_by_name(feats: FeaturesTuple, feat_name: str) -> FeatureTypes:
    """Search for a feature with a specific name within a feature set.

    Arguments:
        feats: Feature set to search in.
        feat_name: Feature name to look for.

    Returns:
        The Feature with the name 'feat_name'

    Raises:
        VimbaFeatureError if feature with name 'feat_name' can't be found in 'feats'.
    """
    filtered = [feat for feat in feats if feat_name == feat.get_name()]

    if len(filtered) == 0:
        raise VimbaFeatureError('Feature \'{}\' not found.'.format(feat_name))

    return filtered.pop()


def filter_features_by_type(feats: FeaturesTuple, feat_type: FeatureTypes) -> FeaturesTuple:
    """Search for all features with a specific type within a given feature set.

    Arguments:
        feats: Feature set to search in.
        feat_type: Feature Type to search for

    Returns:
        A set of all features of type 'feat_type' in 'feats'. If no matching type is found an
        empty set is returned.
    """
    return tuple([feat for feat in feats if type(feat) == feat_type])
