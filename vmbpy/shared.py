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
import itertools

from .c_binding import (VmbCError, VmbFeatureInfo, VmbHandle, VmbUint32, byref, call_vmb_c,
                        create_string_buffer, sizeof)
from .error import VmbFeatureError
from .feature import FeaturesTuple, FeatureTypes, FeatureTypeTypes
from .util import TraceEnable

__all__ = [
    'filter_selected_features',
    'filter_features_by_name',
    'filter_features_by_type',
    'filter_features_by_category',
    'attach_feature_accessors',
    'remove_feature_accessors',
    'read_memory',
    'write_memory'
]


@TraceEnable()
def filter_selected_features(feats: FeaturesTuple, feat: FeatureTypes) -> FeaturesTuple:
    """Search for all Features selected by a given feature within a feature set.

    Arguments:
        feats:
            Feature set to search in.
        feat:
            Feature that might select Features within 'feats'.

    Returns:
        A set of all features that are selected by 'feat'.

    Raises:
        VmbFeatureError:
            If 'feat' is not stored within 'feats'.
    """
    if feat not in feats:
        raise VmbFeatureError('Feature \'{}\' not in given Features'.format(feat.get_name()))

    result = []

    if feat.has_selected_features():
        feats_count = VmbUint32()
        feats_handle = feat._handle
        feats_name = feat._info.name

        # Query selected features from given feature
        call_vmb_c('VmbFeatureListSelected', feats_handle, feats_name, None, 0,
                   byref(feats_count), sizeof(VmbFeatureInfo))

        feats_found = VmbUint32(0)
        feats_infos = (VmbFeatureInfo * feats_count.value)()

        call_vmb_c('VmbFeatureListSelected', feats_handle, feats_name, feats_infos, feats_count,
                   byref(feats_found), sizeof(VmbFeatureInfo))

        # Search selected features in given feature set
        for info, feature in itertools.product(feats_infos[:feats_found.value], feats):
            if info.name == feature._info.name:
                result.append(feature)

    return tuple(result)


@TraceEnable()
def filter_features_by_name(feats: FeaturesTuple, feat_name: str):
    """Search for a feature with a specific name within a feature set.

    Arguments:
        feats:
            Feature set to search in.
        feat_name:
            Feature name to look for.

    Returns:
        The Feature with the name ``feat_name`` or ``None`` if lookup failed
    """
    filtered = [feat for feat in feats if feat_name == feat.get_name()]
    return filtered.pop() if filtered else None


@TraceEnable()
def filter_features_by_type(feats: FeaturesTuple, feat_type: FeatureTypeTypes) -> FeaturesTuple:
    """Search for all features with a specific type within a given feature set.

    Arguments:
        feats:
            Feature set to search in.
        feat_type:
            Feature Type to search for

    Returns:
        A set of all features of type ``feat_type`` in ``feats``. If no matching type is found an
        empty set is returned.
    """
    return tuple([feat for feat in feats if isinstance(feat, feat_type)])


@TraceEnable()
def filter_features_by_category(feats: FeaturesTuple, category: str) -> FeaturesTuple:
    """Search for all features of a given category.

    Arguments:
        feats:
            Feature set to search in.
        category:
            Category to filter for

    Returns:
        A set of all features of category ``category`` in ``feats``. If no matching type is found an
        empty set is returned.
    """
    return tuple([feat for feat in feats if feat.get_category() == category])


@TraceEnable()
def attach_feature_accessors(obj, feats: FeaturesTuple):
    """Attach all Features in feats to obj under the feature name.

    Arguments:
        obj:
            Object feats should be attached on.
        feats:
            Features to attach.
    """
    BLACKLIST = (
        'PixelFormat',   # PixelFormats have special access methods.
    )

    for feat in feats:
        feat_name = feat.get_name()
        if feat_name not in BLACKLIST:
            setattr(obj, feat_name, feat)


@TraceEnable()
def remove_feature_accessors(obj, feats: FeaturesTuple):
    """Remove all Features in feats from obj.

    Arguments:
        obj:
            Object, feats should be removed from.
        feats:
            Features to remove.
    """
    for feat in feats:
        try:
            delattr(obj, feat.get_name())

        except AttributeError:
            pass


@TraceEnable()
def read_memory(handle: VmbHandle, addr: int, max_bytes: int) -> bytes:  # coverage: skip
    """Read a byte sequence from a given memory address.

    Arguments:
        handle:
            Handle on entity that allows raw memory access.
        addr:
            Starting address to read from.
        max_bytes:
            Maximum number of bytes to read from addr.

    Returns:
        Read memory contents as bytes.

    Raises:
        ValueError:
            If addr is negative
        ValueError:
            If max_bytes is negative.
        ValueError:
            If the memory access was invalid.
    """
    # Note: Coverage is skipped. Function is untestable in a generic way.
    _verify_addr(addr)
    _verify_size(max_bytes)

    buf = create_string_buffer(max_bytes)
    bytesRead = VmbUint32()

    try:
        call_vmb_c('VmbMemoryRead', handle, addr, max_bytes, buf, byref(bytesRead))

    except VmbCError as e:
        msg = 'Memory read access at {} failed with C-Error: {}.'
        raise ValueError(msg.format(hex(addr), repr(e.get_error_code()))) from e

    return buf.raw[:bytesRead.value]


@TraceEnable()
def write_memory(handle: VmbHandle, addr: int, data: bytes):  # coverage: skip
    """ Write a byte sequence to a given memory address.

    Arguments:
        handle:
            Handle on entity that allows raw memory access.
        addr:
            Address to write the content of 'data' too.
        data:
            Byte sequence to write at address 'addr'.

    Raises:
        ValueError:
            If addr is negative.
        ValueError:
            If the memory access was invalid.
    """
    # Note: Coverage is skipped. Function is untestable in a generic way.
    _verify_addr(addr)

    bytesWrite = VmbUint32()

    try:
        call_vmb_c('VmbMemoryWrite', handle, addr, len(data), data, byref(bytesWrite))

    except VmbCError as e:
        msg = 'Memory write access at {} failed with C-Error: {}.'
        raise ValueError(msg.format(hex(addr), repr(e.get_error_code()))) from e


def _verify_addr(addr: int):  # coverage: skip
    # Note: Coverage is skipped. Function is untestable in a generic way.
    if addr < 0:
        raise ValueError('Given Address {} is negative'.format(addr))


def _verify_size(size: int):  # coverage: skip
    # Note: Coverage is skipped. Function is untestable in a generic way.
    if size < 0:
        raise ValueError('Given size {} is negative'.format(size))
