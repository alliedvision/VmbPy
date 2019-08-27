# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ctypes import byref, sizeof
from vimba.c_binding.api import call_vimba_c_func
from vimba.c_binding.types import VmbVersionInfo, VmbCameraInfo, VmbUint32, \
                                  VmbBool, G_VIMBA_HANDLE


def get_version():
    version = VmbVersionInfo()
    call_vimba_c_func('VmbVersionQuery', byref(version), sizeof(version))
    return str(version)


def discover_gige_cameras():
    is_gige = VmbBool(False)
    call_vimba_c_func('VmbFeatureBoolGet', G_VIMBA_HANDLE, b'GeVTLIsPresent', byref(is_gige))

    if is_gige.value :
        call_vimba_c_func('VmbFeatureIntSet', G_VIMBA_HANDLE, b'GeVDiscoveryAllDuration', 250)
        call_vimba_c_func('VmbFeatureCommandRun', G_VIMBA_HANDLE, b'GeVDiscoveryAllOnce')


def list_cameras():
    discover_gige_cameras()

    cam_count = VmbUint32(0)

    call_vimba_c_func('VmbCamerasList', None, 0, byref(cam_count), 0)

    if cam_count:
        cams = (VmbCameraInfo * cam_count.value) ()
        cams_found = VmbUint32(0)

        call_vimba_c_func('VmbCamerasList', cams, cam_count, byref(cams_found), sizeof(VmbCameraInfo))

        print('List all detected cameras:')
        for cam in cams[:cams_found.value]:
            print(cam)


def main():
    print("VimbaPython List Camera Example (Prototype C-API.{}):".format(get_version()))

    call_vimba_c_func('VmbStartup')

    try:
        list_cameras()

    finally:
        call_vimba_c_func('VmbShutdown')

if __name__ == '__main__':
    main()
