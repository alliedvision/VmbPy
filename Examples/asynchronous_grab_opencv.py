# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

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
