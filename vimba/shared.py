"""Shared Functions used by multiple entities.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import itertools

from .c_binding import VmbUint32, VmbHandle, VmbFeatureInfo
from .c_binding import call_vimba_c, byref, sizeof, create_string_buffer
from .feature import FeaturesTuple, FeatureTypes
from .error import VimbaFeatureError
from .util import TraceEnable

__all__ = [
    'filter_affected_features',
    'filter_selected_features',
    'filter_features_by_name',
    'filter_features_by_type',
    'read_memory_impl',
    'write_memory_impl',
    'read_registers_impl',
    'write_registers_impl'
]


@TraceEnable()
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
        call_vimba_c('VmbFeatureListAffected', feats_handle, feats_name, None, 0,
                     byref(feats_count), sizeof(VmbFeatureInfo))

        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vimba_c('VmbFeatureListAffected', feats_handle, feats_name, feats_infos, feats_count,
                     byref(feats_found), sizeof(VmbFeatureInfo))

        # Search affected features in given feature set
        for info, feature in itertools.product(feats_infos[:feats_found.value], feats):
            if info.name == feature._info.name:
                result.append(feature)

    return tuple(result)


@TraceEnable()
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
        call_vimba_c('VmbFeatureListSelected', feats_handle, feats_name, None, 0,
                     byref(feats_count), sizeof(VmbFeatureInfo))

        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vimba_c('VmbFeatureListSelected', feats_handle, feats_name, feats_infos, feats_count,
                     byref(feats_found), sizeof(VmbFeatureInfo))

        # Search selected features in given feature set
        for info, feature in itertools.product(feats_infos[:feats_found.value], feats):
            if info.name == feature._info.name:
                result.append(feature)

    return tuple(result)


@TraceEnable()
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

    if not filtered:
        raise VimbaFeatureError('Feature \'{}\' not found.'.format(feat_name))

    return filtered.pop()


@TraceEnable()
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


@TraceEnable()
def read_memory_impl(handle: VmbHandle, addr: int, max_bytes: int) -> bytes:
    """Read a sequence of bytes from a given address.

    Raises:
        ValueError if addr is negative
    """
    _verify_addr(addr)

    buf = create_string_buffer(max_bytes)
    bytesRead = VmbUint32()

    # TODO: Try/catch
    call_vimba_c('VmbMemoryRead', handle, addr, max_bytes, buf, byref(bytesRead))

    return buf.value[:bytesRead.value]


@TraceEnable()
def write_memory_impl(handle: VmbHandle, addr: int, data: bytes):
    """ TODO: Document me """
    _verify_addr(addr)

    bytesWrite = VmbUint32()

    # TODO: Try/catch
    call_vimba_c('VmbMemoryWrite', handle, addr, len(data), data, byref(bytesWrite))


@TraceEnable()
def read_registers_impl(handle: VmbHandle, addr: int, max_bytes: int) -> bytes:
    """ TODO: Document me """
    _verify_addr(addr)

    #  VmbRegistersRead ( const VmbHandle_t   handle,
    #                     VmbUint32_t         readCount,
    #                     const VmbUint64_t*  pAddressArray,
    #                     VmbUint64_t*        pDataArray,
    #                     VmbUint32_t*        pNumCompleteReads );

    raise NotImplementedError('impl me')


@TraceEnable()
def write_registers_impl(handle: VmbHandle, addr: int, data: bytes):
    """ TODO: Document me """
    _verify_addr(addr)

    #  VmbRegistersWrite ( const VmbHandle_t   handle,
    #                      VmbUint32_t         writeCount,
    #                      const VmbUint64_t*  pAddressArray,
    #                      const VmbUint64_t*  pDataArray,
    #                      VmbUint32_t*        pNumCompleteWrites );

    raise NotImplementedError('impl me')


def _verify_addr(addr):
    if addr < 0:
        raise ValueError('Given Address {} is negative'.format(addr))
