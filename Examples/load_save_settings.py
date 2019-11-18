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
"""

import sys
from vimba import *


def abort(reason: str, return_code: int = 1):
    print(reason + '\n')
    sys.exit(return_code)


def main():
    with Vimba.get_instance() as vimba:
        # Store configuration of first detected Camera
        cams = vimba.get_all_cameras()

        if not cams:
            abort('No camera is connected. Abort.')

        # Access camera
        with cams[0] as cam:
            # Save camera settings to file.
            settings_file = '{}_settings.xml'.format(cam.get_id())
            cam.save_settings(settings_file, PersistType.All)

            # Restore settings to initial value.
            cam.get_feature_by_name('UserSetSelector').set('Default')
            cam.get_feature_by_name('UserSetLoad').run()

            # Load camera settings from file.
            cam.load_settings(settings_file, PersistType.All)


if __name__ == '__main__':
    main()
