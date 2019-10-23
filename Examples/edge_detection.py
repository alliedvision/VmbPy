# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)
import ctypes
import os
import sys
import time
import cv2
import numpy
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

class StreamHandler:
    def __init__(self):
        self.shutdown_event = threading.Event()

    def __call__(self, cam: Camera, frame: Frame):
        Log.get_instance().info('{} acquired {}'.format(cam, frame))

        # Test abort condition
        ESC_KEY_CODE = 27

        key = cv2.waitKey(1)
        if key == ESC_KEY_CODE:
            self.shutdown_event.set()
            return

        try:
            # Apply Edge Detection on Frame
            orig = frame.as_opencv_image()
            edge = cv2.Canny(orig, 50, 100)
            edge = edge[..., numpy.newaxis]
            edge = edge[..., [0] * len(orig[0][0])]

            # Merge and show images
            image = numpy.concatenate((orig, edge), axis=1)
            cv2.imshow('Original, Edge Detect: ESC=Quit', image)
            cam.queue_frame(frame)

        except Exception as e:
            # Log and shutdown on error
            log.error(str(e))
            self.shutdown_event.set()


def main():
    with Vimba.get_instance() as vimba:
        # Lookup first detected camera.
        cams = vimba.get_all_cameras()
        if cams:
            # Enter Camera context
            with cams[0] as cam:

                # Setup Camera
                cam.get_feature_by_name('ExposureAuto').set('Continuous')
                cam.get_feature_by_name('BalanceWhiteAuto').set('Continuous')
                cam.get_feature_by_name('PixelFormat').set('BGR8')
                cam.get_feature_by_name('Height').set(608)
                cam.get_feature_by_name('Width').set(608)

                # Enable Logging for capturing messages from the frame handler
                vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

                stream_handler = StreamHandler()

                # Start Streaming
                cam.start_streaming(stream_handler)

                stream_handler.shutdown_event.wait()

                cam.stop_streaming()

                vimba.disable_log()

if __name__ == '__main__':
    main()

