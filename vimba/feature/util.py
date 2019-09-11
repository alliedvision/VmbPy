# TODO: Add License
# TODO: Add Copywrite Note
# TODO: Add Contact Info (clarify if this is required...)
# TODO: Add docstring to public entities
# TODO: Add repr and str

from itertools import product
from typing import Union, Tuple
from vimba.c_binding import call_vimba_c_func, byref, sizeof
from vimba.c_binding import VmbFeatureInfo, VmbFeatureData, VmbHandle, VmbUint32
from vimba.feature.base_feature import BaseFeature
from vimba.feature.int_feature import IntFeature
from vimba.feature.float_feature import FloatFeature
from vimba.feature.string_feature import StringFeature
from vimba.feature.bool_feature import BoolFeature
from vimba.feature.enum_feature import EnumFeature
from vimba.feature.command_feature import CommandFeature
from vimba.feature.raw_feature import RawFeature


FeatureTypes = Union[BaseFeature, IntFeature, FloatFeature, StringFeature, BoolFeature, EnumFeature,
                     CommandFeature, RawFeature]

FeaturesTuple = Tuple[FeatureTypes, ...]

_MAP_FEAT_DATA_TO_TYPE = {
    VmbFeatureData.Int: IntFeature,
    VmbFeatureData.Float: FloatFeature,
    VmbFeatureData.String: StringFeature,
    VmbFeatureData.Bool: BoolFeature,
    VmbFeatureData.Enum: EnumFeature,
    VmbFeatureData.Command: CommandFeature,
    VmbFeatureData.Raw: RawFeature
}


def _build_feature(handle: VmbHandle, info: VmbFeatureInfo) -> FeatureTypes:
    feat_type = _MAP_FEAT_DATA_TO_TYPE[(VmbFeatureData(info.featureDataType))]
    return feat_type(handle, info)


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
    # TODO: Better Exception
    assert feat in feats

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
    # TODO: Better Exception
    assert feat in feats

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
        raise Exception('Unknown Feature')

    return filtered.pop()


def filter_features_by_type(feats: FeaturesTuple, feat_type: FeatureTypes) -> FeaturesTuple:
    return tuple([feat for feat in feats if type(feat) == feat_type])
