# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

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
    info = VmbFeatureInfo()

    call_vimba_c_func('VmbFeatureInfoQuery', handle, feat_name.encode('utf-8'),
                      byref(info), sizeof(VmbFeatureInfo))

    return _build_feature(handle, info)


def filter_affected_features(feats: FeaturesTuple, feat: FeatureTypes) -> FeaturesTuple:
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
    filtered = [feat for feat in feats if feat_name == feat.get_name()]

    if len(filtered) == 0:
        raise VimbaFeatureError('Feature \'{}\' not found.'.format(feat_name))

    return filtered.pop()


def filter_features_by_type(feats: FeaturesTuple, feat_type: FeatureTypes) -> FeaturesTuple:
    return tuple([feat for feat in feats if type(feat) == feat_type])
