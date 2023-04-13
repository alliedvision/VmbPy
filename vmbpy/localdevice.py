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

from .c_binding import VmbHandle
from .featurecontainer import PersistableFeatureContainer
from .util import EnterContextOnCall, LeaveContextOnCall, RaiseIfOutsideContext

__all__ = [
    'LocalDevice'
]


class LocalDevice(PersistableFeatureContainer):
    """This class provides access to the Local Device of a Camera.
    """
    def __init__(self, handle: VmbHandle) -> None:
        super().__init__()
        self._handle: VmbHandle = handle
        self._open()

    @EnterContextOnCall()
    def _open(self):
        self._attach_feature_accessors()

    @LeaveContextOnCall()
    def _close(self):
        self._remove_feature_accessors()

    __msg = 'Called \'{}()\' outside of Cameras \'with\' context.'
    get_all_features = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_all_features)                  # noqa: E501
    get_features_selected_by = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_selected_by)  # noqa: E501
    get_features_by_type = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_by_type)          # noqa: E501
    get_features_by_category = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_features_by_category)  # noqa: E501
    get_feature_by_name = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.get_feature_by_name)            # noqa: E501
    load_settings = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.load_settings)
    save_settings = RaiseIfOutsideContext(msg=__msg)(PersistableFeatureContainer.save_settings)
