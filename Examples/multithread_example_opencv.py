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

import copy
import cv2
import threading
import queue
import numpy
import functools

from vimba import *

class FrameProducer(threading.Thread):
    def __init__(self, cam: Camera, frame_queue: queue.Queue, teardown: threading.Event):
        threading.Thread.__init__(self)

        self.log = Log.get_instance()
        self.cam = cam
        self.frame_queue = frame_queue
        self.teardown = teardown

    def __call__(self, cam: Camera, frame: Frame):
        if frame.get_status() == FrameStatus.Complete:
            # Construct Item to send to FrameConsumer (camera id + acquired frame)
            queue_item = (cam.get_id(), copy.deepcopy(frame))

            try:
                self.frame_queue.put(queue_item, timeout=1)

            except queue.Full:
                pass

        # Reuse original Frame
        cam.queue_frame(frame)

    def run(self):
        self.log.info('Thread \'FrameProducer({})\' started.'.format(self.cam.get_id()))

        with self.cam:
            self.setup_camera()

            try:
                self.cam.start_streaming(self)
                self.teardown.wait()

            finally:
                self.cam.stop_streaming()

        self.log.info('Thread \'FrameProducer({})\' terminated.'.format(self.cam.get_id()))

    def setup_camera(self):
        with self.cam:
            try:
                self.cam.get_feature_by_name('Height').set(640)

            except VimbaFeatureError as e:
                raise RuntimeError('Failed to set feature Height') from e

            try:
                self.cam.get_feature_by_name('Width').set(640)

            except VimbaFeatureError as e:
                raise RuntimeError('Failed to set feature Width') from e

            try:
                self.cam.get_feature_by_name('ExposureAuto').set('Once')

            except VimbaFeatureError as e:
                raise RuntimeError('Failed to set feature ExposureAuto') from e

            try:
                self.cam.set_pixel_format(PixelFormat.Mono8)

            except VimbaFeatureError as e:
                raise RuntimeError('Failed to set PixelFormat') from e


class FrameConsumer(threading.Thread):
    def __init__(self, frame_queue: queue.Queue, teardown: threading.Event):
        threading.Thread.__init__(self)

        self.log = Log.get_instance()
        self.frame_queue = frame_queue
        self.teardown = teardown

    def run(self):
        KEY_CODE_ENTER = 13
        IMAGE_CAPTION = 'Multithreading Example: Press <Enter> to exit'

        # Set Defaults to cv2.putText
        putText = functools.partial(cv2.putText, org=(0, 30), fontScale=1, color=255, thickness=1,
                                    fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL)

        state = {}
        self.log.info('Thread \'FrameConsumer\' started.')

        while self.teardown.is_set() == False:
            try:
                item = self.frame_queue.get(timeout=1)

            except queue.Empty:
                continue

            cam_id, frame = item
            self.log.info('Received Frame {} from Camera {}.'.format(frame.get_id(), cam_id))

            # Write Camera ID into acquired image
            opencv_image = frame.as_opencv_image()
            putText(opencv_image, 'Cam: {}'.format(cam_id))

            # Add Frame to current state chart
            state[cam_id] = (frame, opencv_image)

            # Sort Frames by Camera ID and stitch all frames together.
            opencv_images = [state[key][1] for key in sorted(state.keys())]

            # Show Image and check for shutdown condition.
            cv2.imshow(IMAGE_CAPTION, numpy.concatenate(opencv_images, axis=1))

            if cv2.waitKey(10) == KEY_CODE_ENTER:
                self.teardown.set()

        self.log.info('Thread \'FrameConsumer\' terminated.')


def main():
    # Setup synchronization methods
    frame_queue = queue.Queue(10)
    teardown = threading.Event()

    with Vimba.get_instance() as vimba:
        vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

        producers = [FrameProducer(cam, frame_queue, teardown) for cam in vimba.get_all_cameras()]
        consumer = FrameConsumer(frame_queue, teardown)

        # Start Threads
        consumer.start()
        for producer in producers:
            producer.start()

        # Wait on Event for synchronized tear down
        teardown.wait()

        for producer in producers:
            producer.join()

        consumer.join()


if __name__ == '__main__':
    main()

