# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import ctypes
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *
from threading import Lock

class ChangeHandlerAsObj:
    def __init__(self, context):
        self._context = context

    def __call__(self, f):
        print('ChangeHandlerAsObj({}, Context={}, Value={})'.format(f, self._context, f.get()))


def ChangeHandlerAsFunc(f):
    print('ChangeHandlerAsFunc({}, Value={})'.format(f, f.get()))


change_handler_lambda = lambda f: print('change_handler_lambda({}, Value={})'.format(f, f.get()))

def handle_camera(cam):
    global change_handler_lambda

    with cam:
        # Changes on width should affect PayloadSize
        width = cam.get_feature_by_name('Width')
        payload_size = cam.get_feature_by_name('PayloadSize')

        # Register Object
        change_handler_obj = ChangeHandlerAsObj('With Context')
        payload_size.add_change_handler(change_handler_obj)

        # Register Function
        payload_size.add_change_handler(ChangeHandlerAsFunc)

        # Register lambda expression
        payload_size.add_change_handler(change_handler_lambda)

        # Changing Width affects PayloadSize. Width set must trigger change_handler Functor
        old_value = width.get()
        width.set(2000)
        width.set(old_value)

        payload_size.remove_change_handler(change_handler_obj)
        payload_size.remove_change_handler(ChangeHandlerAsFunc)
        payload_size.remove_change_handler(change_handler_lambda)


def main():
    #System.get_instance().enable_log(LOG_CONFIG_TRACE_CONSOLE_ONLY)

    with System.get_instance() as sys:
        for cam in sys.get_all_cameras():
            handle_camera(cam)

if __name__ == '__main__':
    main()

