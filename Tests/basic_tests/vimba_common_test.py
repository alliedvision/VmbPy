"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
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
import os
import sys

from vmbpy.c_binding import _select_vimbax_home
from vmbpy.error import VmbSystemError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class RankVimbaXHomeCandidatesTest(VmbPyTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_empty_gentl_path(self):
        candidates = []
        with self.assertRaises(VmbSystemError):
            _select_vimbax_home(candidates)

    def test_empty_string(self):
        candidates = ['']
        with self.assertRaises(VmbSystemError):
            _select_vimbax_home(candidates)

    def test_single_bad_vimbax_home_candidate(self):
        candidates = ['/some/path']
        with self.assertRaises(VmbSystemError):
            _select_vimbax_home(candidates)

    def test_single_good_vimbax_home_candidate(self):
        candidates = ['/opt/VimbaX_2022-1']
        expected = '/opt/VimbaX_2022-1'
        self.assertEqual(expected, _select_vimbax_home(candidates))

    def test_presorted_vimbax_home_candidates(self):
        candidates = ['/home/username/VimbaX_2022-1', '/opt/some/other/gentl/provider']
        expected = '/home/username/VimbaX_2022-1'
        self.assertEqual(expected, _select_vimbax_home(candidates))

    def test_unsorted_vimbax_home_candidates(self):
        candidates = ['/opt/some/other/gentl/provider', '/home/username/VimbaX_2022-1']
        expected = '/home/username/VimbaX_2022-1'
        self.assertEqual(expected, _select_vimbax_home(candidates))

    def test_many_vimbax_home_candidates(self):
        candidates = ['/some/random/path',
                      '/opt/some/gentl/provider',
                      '/opt/VimbaX_2022-1',  # This should be selected
                      '/opt/another/gentl/provider',
                      '/another/incorrect/path']
        expected = '/opt/VimbaX_2022-1'
        self.assertEqual(expected, _select_vimbax_home(candidates))

    def test_vimbax_and_vimba_installation(self):
        candidates = ['/opt/Vimba_4_0',  # Installation of Allied Vision Vimba
                      '/opt/VimbaX_2022-1']   # Installation of VimbaX. This should be selected
        expected = '/opt/VimbaX_2022-1'
        self.assertEqual(expected, _select_vimbax_home(candidates))

    def test_multiple_vimbax_home_directories(self):
        # If multiple VIMBAX_HOME directories are found an error should be raised
        candidates = ['/some/random/path',
                      '/opt/some/gentl/provider',
                      '/opt/VimbaX_2022-1',  # first installation
                      '/home/username/VimbaX_2023-1',  # second installation
                      '/opt/another/gentl/provider',
                      '/another/incorrect/path']
        with self.assertRaises(VmbSystemError):
            _select_vimbax_home(candidates)
