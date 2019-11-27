"""BSD 2-Clause License

Copyright (c) 2019, Allied Vision Technologies GmbH
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

THE SOFTWARE IS PRELIMINARY AND STILL IN TESTING AND VERIFICATION PHASE AND
IS PROVIDED ON AN “AS IS” AND “AS AVAILABLE” BASIS AND IS BELIEVED TO CONTAIN DEFECTS.
A PRIMARY PURPOSE OF THIS EARLY ACCESS IS TO OBTAIN FEEDBACK ON PERFORMANCE AND
THE IDENTIFICATION OF DEFECT SOFTWARE, HARDWARE AND DOCUMENTATION.
"""

import unittest

from vimba import *

class AncillaryDataTest(unittest.TestCase):
    def setUp(self):
        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        try:
            self.cam = self.vimba.get_camera_by_id(self.get_test_camera_id())

        except VimbaCameraError as e:
            self.vimba._shutdown()
            raise Exception('Failed to lookup Camera.') from e

        try:
            self.cam._open()

        except VimbaCameraError as e:
            self.vimba._shutdown()
            raise Exception('Failed to open Camera.') from e

        try:
            self.chunk_mode = self.cam.get_feature_by_name('ChunkModeActive')

        except VimbaFeatureError:
            self.cam._close()
            self.vimba._shutdown()
            self.skipTest('Required Feature \'ChunkModeActive\' not available.')

    def tearDown(self):
        self.cam._close()
        self.vimba._shutdown()

    def test_ancillary_data_access(self):
        """Expectation: Ancillary Data is None if ChunkMode is disable.
        If ChunkMode is enabled Ancillary Data shall not be None.
        """
        pass

    def test_ancillary_data_context_sensitity(self):
        """Expectation: Feature related methods are only don't raise within Context."""
        pass


