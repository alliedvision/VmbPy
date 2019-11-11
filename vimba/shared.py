"""Shared Functions used by multiple entities.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import itertools

from .c_binding import VmbUint32, VmbHandle, VmbFeatureInfo
from .c_binding import call_vimba_c, byref, sizeof, create_string_buffer, VimbaCError
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
    """Read a byte sequence from a given memory address.

    Arguments:
        handle: Handle on entity that allows raw memory access.
        addr: Starting address to read from.
        max_bytes: Maximum number of bytes to read from addr.

    Returns:
        Read memory contents as bytes.

    Raises:
        ValueError if addr is negative
        ValueError if max_bytes is negative.
        ValueError if the memory access was invalid.
    """
    _verify_addr(addr)
    _verify_size(max_bytes)

    exc = None
    buf = create_string_buffer(max_bytes)
    bytesRead = VmbUint32()

    try:
        call_vimba_c('VmbMemoryRead', handle, addr, max_bytes, buf, byref(bytesRead))

    except VimbaCError as e:
        msg = 'Memory read access at {} failed with C-Error: {}.'
        exc = ValueError(msg.format(hex(addr), repr(e.get_error_code())))

    if exc:
        raise exc

    return buf.value[:bytesRead.value]


@TraceEnable()
def write_memory_impl(handle: VmbHandle, addr: int, data: bytes):
    """ Write a byte sequence to a given memory address.

    Arguments:
        handle: Handle on entity that allows raw memory access.
        addr: Address to write the content of 'data' too.
        data: Byte sequence to write at address 'addr'.

    Raises:
        ValueError if addr is negative.
    """
    _verify_addr(addr)

    exc = None
    bytesWrite = VmbUint32()

    try:
        call_vimba_c('VmbMemoryWrite', handle, addr, len(data), data, byref(bytesWrite))

    except VimbaCError as e:
        msg = 'Memory write access at {} failed with C-Error: {}.'
        exc = ValueError(msg.format(hex(addr), repr(e.get_error_code())))

    if exc:
        raise exc

@TraceEnable()
def read_registers_impl(handle: VmbHandle, addr: int, max_bytes: int) -> bytes:
    """Read a sequence of bytes from a given register address.

    Raises:
        ValueError if addr is negative
        ValueError if max_bytes is negative
    """
    _verify_addr(addr)
    _verify_size(max_bytes)

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


def _verify_addr(addr: int):
    if addr < 0:
        raise ValueError('Given Address {} is negative'.format(addr))


def _verify_size(size: int):
    if size < 0:
        raise ValueError('Given size {} is negative'.format(size))
