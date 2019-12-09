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

from typing import Optional
from vimba import *


def print_preamble():
    print('////////////////////////////////////////////')
    print('/// Vimba API Multithreading Example ///////')
    print('////////////////////////////////////////////\n')
    print(flush=True)


def add_camera_id(frame: Frame, cam_id: str) -> Frame:
    text = 'Cam: {}'.format(cam_id)
    cv2.putText(frame.as_opencv_image(), text, org=(0, 30), fontScale=1, color=255, thickness=1,
                fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL)
    return frame


def create_dummy_frame() -> numpy.ndarray:
    HEIGHT = 50
    WIDTH = 640
    CHANNELS = 1
    TEXT = 'No Stream available. Please connect a Camera.'

    cv_frame = numpy.zeros((HEIGHT, WIDTH, CHANNELS), numpy.uint8)
    cv_frame[:] = 0

    cv2.putText(cv_frame, TEXT, org=(30, 30), fontScale=1, color=255, thickness=1,
                fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL)

    return cv_frame


def try_put_frame(q: queue.Queue, cam: Camera, frame: Optional[Frame]):
    try:
        q.put_nowait((cam.get_id(), frame))

    except queue.Full:
        pass


def set_feature(obj, feat_name: str, feat_value):
    try:
        obj.get_feature_by_name(feat_name).set(feat_value)

    except VimbaFeatureError as e:
        raise RuntimeError('Failed to set Feature \'{}\''.format(feat_name)) from e


# Thread Objects
class FrameProducer(threading.Thread):
    def __init__(self, cam: Camera, frame_queue: queue.Queue):
        threading.Thread.__init__(self)

        self.log = Log.get_instance()
        self.cam = cam
        self.frame_queue = frame_queue
        self.killswitch = threading.Event()

    def __call__(self, cam: Camera, frame: Frame):
        if frame.get_status() == FrameStatus.Complete:
            try_put_frame(self.frame_queue, cam, copy.deepcopy(frame))

        cam.queue_frame(frame)

    def stop(self):
        self.killswitch.set()

    def run(self):
        self.log.info('Thread \'FrameProducer({})\' started.'.format(self.cam.get_id()))

        try:
            with self.cam:
                set_feature(self.cam, 'Height', 640)
                set_feature(self.cam, 'Width', 640)
                set_feature(self.cam, 'ExposureAuto', 'Once')
                self.cam.set_pixel_format(PixelFormat.Mono8)

                try:
                    self.cam.start_streaming(self)
                    self.killswitch.wait()

                finally:
                    self.cam.stop_streaming()

        except VimbaCameraError:
            pass

        finally:
            try_put_frame(self.frame_queue, self.cam, None)

        self.log.info('Thread \'FrameProducer({})\' terminated.'.format(self.cam.get_id()))


class FrameConsumer(threading.Thread):
    def __init__(self, frame_queue: queue.Queue):
        threading.Thread.__init__(self)

        self.log = Log.get_instance()
        self.frame_queue = frame_queue

    def run(self):
        IMAGE_CAPTION = 'Multithreading Example: Press <Enter> to exit'
        KEY_CODE_ENTER = 13

        frames = {}
        alive = True

        self.log.info('Thread \'FrameConsumer\' started.')

        while alive:
            # Update State by dequeuing all currently available frames.
            frames_left = self.frame_queue.qsize()
            while frames_left:
                try:
                    cam_id, frame = self.frame_queue.get_nowait()

                except queue.Empty:
                    break

                # Add/Remove Frame from current state.
                if frame:
                    frames[cam_id] = add_camera_id(frame, cam_id)

                else:
                    frames.pop(cam_id, None)

                frames_left -= 1

            # If the current state contains any Frames, stitch the together and show them
            if frames:
                cv_images = [frames[cam_id].as_opencv_image() for cam_id in sorted(frames.keys())]
                cv2.imshow(IMAGE_CAPTION, numpy.concatenate(cv_images, axis=1))

            # If there are no Frames available, show dummy image
            else:
                cv2.imshow(IMAGE_CAPTION, create_dummy_frame())

            # Check for shutdown condition
            if KEY_CODE_ENTER == cv2.waitKey(10):
                cv2.destroyAllWindows()
                alive = False

        self.log.info('Thread \'FrameConsumer\' terminated.')


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.frame_queue = queue.Queue(maxsize=10)
        self.producers = {}
        self.producers_lock = threading.Lock()

    def __call__(self, cam: Camera, event: CameraEvent):
        if event == CameraEvent.Detected:
            # New Camera was detected. Create FrameProducer, add it to active FrameProducers
            with self.producers_lock:
                self.producers[cam.get_id()] = FrameProducer(cam, self.frame_queue)
                self.producers[cam.get_id()].start()

        elif event == CameraEvent.Missing:
            # An existing Camera was disconnected, stop associated FrameProducer.
            with self.producers_lock:
                producer = self.producers.pop(cam.get_id())
                producer.stop()
                producer.join()

    def run(self):
        log = Log.get_instance()
        consumer = FrameConsumer(self.frame_queue)

        vimba = Vimba.get_instance()
        vimba.enable_log(LOG_CONFIG_INFO_CONSOLE_ONLY)

        log.info('Thread \'MainThread\' started.')

        with vimba:
            # Construct FrameProducer Threads for all detected Cameras
            for cam in vimba.get_all_cameras():
                self.producers[cam.get_id()] = FrameProducer(cam, self.frame_queue)

            # Start FrameProducer Threads
            with self.producers_lock:
                for producer in self.producers.values():
                    producer.start()

            # Start and wait for consumer to terminate
            vimba.register_camera_change_handler(self)
            consumer.start()
            consumer.join()
            vimba.unregister_camera_change_handler(self)

            # Stop all FrameProducer Threads
            with self.producers_lock:
                # Initiate concurrent shutdown
                for producer in self.producers.values():
                    producer.stop()

                # Wait for shutdown to complete
                for producer in self.producers.values():
                    producer.join()

        log.info('Thread \'MainThread\' terminated.')

if __name__ == '__main__':
    print_preamble()
    main = MainThread()
    main.start()
    main.join()
