# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import ctypes
from multiprocessing import Lock
from ctypes import byref, sizeof
from vimba.c_binding.api import call_vimba_c_func
from vimba.c_binding.types import VmbUint32, VmbCameraInfo, VmbAccessMode, \
                                  VmbHandle, VmbFrame, VmbInt64, \
                                  VmbFrameCallback \

g_camera_handle = VmbHandle()
g_frames = []
g_buffers = []
g_lock = Lock()

def process_frame(camera_handle, p_frame):
    global g_lock

    with g_lock:
        print('In callback: {}\n'.format(p_frame.contents))


g_callback = VmbFrameCallback(process_frame)


def get_camera_id():
    # Get all existing cameras:
    cam_count = VmbUint32(0)

    call_vimba_c_func('VmbCamerasList', None, 0, byref(cam_count), 0)

    if cam_count:
        cams = (VmbCameraInfo * cam_count.value) ()
        cams_found = VmbUint32(0)

        call_vimba_c_func('VmbCamerasList', cams, cam_count,
                          byref(cams_found), sizeof(VmbCameraInfo))

        if cams_found.value != 0:
            return cams[0].cameraIdString

    raise Exception('No cameras detected')


def open_camera(cam_id):
    access_mode = VmbAccessMode.Full
    camera_handle = VmbHandle()

    call_vimba_c_func('VmbCameraOpen', cam_id, access_mode,
                      byref(camera_handle))

    return camera_handle


def start_image_acquisition(frames=10):
    global g_camera_handle
    global g_frames
    global g_buffers
    global g_callback

    g_camera_handle = open_camera(get_camera_id())
    payload_size = VmbInt64(0)

    call_vimba_c_func('VmbFeatureIntGet', g_camera_handle, b'PayloadSize',
                      byref(payload_size))

    # Allocate Image Buffer and VmbFrame
    for i in range(frames):
        g_buffers.append(ctypes.create_string_buffer(b'', payload_size.value))
        g_frames.append(VmbFrame())

    # Allocate Memory and announce frames to Vimba
    for i in range(len(g_frames)):
        g_frames[i].buffer = ctypes.cast(g_buffers[i], ctypes.c_void_p)
        g_frames[i].bufferSize = payload_size.value

        call_vimba_c_func('VmbFrameAnnounce', g_camera_handle,
                          byref(g_frames[i]), sizeof(VmbFrame))

    call_vimba_c_func('VmbCaptureStart', g_camera_handle)

    for i in range(len(g_frames)):
        call_vimba_c_func('VmbCaptureFrameQueue', g_camera_handle,
                          byref(g_frames[i]), g_callback)

    call_vimba_c_func('VmbFeatureCommandRun', g_camera_handle,
                      b'AcquisitionStart')


def stop_image_acquisition():
    global g_camera_handle
    global g_frames
    global g_lock

    call_vimba_c_func('VmbFeatureCommandRun', g_camera_handle,
                      b'AcquisitionStop')
    call_vimba_c_func('VmbCaptureEnd', g_camera_handle)

    with g_lock:
        for frame in g_frames:
            call_vimba_c_func('VmbFrameRevoke', g_camera_handle, byref(frame))

    call_vimba_c_func('VmbCameraClose', g_camera_handle)


def main():
    call_vimba_c_func('VmbStartup')

    try:
        start_image_acquisition(10)
        time.sleep(3)
        stop_image_acquisition()

    finally:
        call_vimba_c_func('VmbShutdown')


if __name__ == '__main__':
    main()
