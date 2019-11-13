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

import time
import cv2
from vimba import *


def frame_handler(cam: Camera, frame: Frame):
    log = Log.get_instance()
    log.info('{} acquired {}'.format(cam, frame))

    cv2.imshow('Stream from \'{}\''.format(cam.get_name()), frame.as_opencv_image())
    cv2.waitKey(1)

    cam.queue_frame(frame)


def setup_camera(cam):
    # Enable auto exposure time setting if camera supports it
    try:
        cam.get_feature_by_name('ExposureAuto').set('Continuous')

    except VimbaFeatureError:
        pass

    # Enable white balancing if camera supports it
    try:
        cam.get_feature_by_name('BalanceWhiteAuto').set('Continuous')

    except VimbaFeatureError:
        pass

    # Query available, open_cv compatible pixel formats
    # prefer color formats over monochrome formats
    cv_fmts = intersect_pixel_formats(cam.get_pixel_formats(), OPENCV_PIXEL_FORMATS)
    color_fmts = intersect_pixel_formats(cv_fmts, COLOR_PIXEL_FORMATS)

    if color_fmts:
        cam.set_pixel_format(color_fmts[0])

    else:
        mono_fmts = intersect_pixel_formats(cv_fmts, MONO_PIXEL_FORMATS)

        if mono_fmts:
            cam.set_pixel_format(mono_fmts[0])

        else:
            raise Exception('Camera does not support a OpenCV compatible format natively.')


def main():
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()

        # Use first detected camera
        if cams:
            with cams[0] as cam:
                # Enable Logging for capturing messages from the frame handler
                vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

                # Start Streaming, wait for five seconds, stop streaming
                setup_camera(cam)
                cam.start_streaming(frame_handler)
                time.sleep(5)
                cam.stop_streaming()

                # Disable Logging
                vimba.disable_log()

        else:
            print('No Cameras detected')


if __name__ == '__main__':
    main()
