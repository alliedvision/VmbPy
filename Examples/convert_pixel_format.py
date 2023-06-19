import argparse
import sys
import textwrap
from typing import Any, List, Optional

import vmbpy

try:
    # Check if numpy is available. Not used directly by the example but necessary to create numpy
    # arrays that are used as `destination_buffer`s
    import numpy as np  # noqa: F401
except ImportError:
    print('This example requires numpy')
    sys.exit(1)


def print_preamble():
    print('//////////////////////////////////////////')
    print('/// VmbPy convert_pixel_format Example ///')
    print('//////////////////////////////////////////\n')
    print(flush=True)


def abort(reason: str, return_code: int = 1):
    print(reason + '\n')

    sys.exit(return_code)


def parse_args():
    description = '''\
    VmbPy `Frame.convert_pixel_format` Example

    Records frames in a user selected pixel format and converts them to a different user selected
    format. Optionally this transformation can use a pre allocated `destination_buffer` to reduce
    possible overhead from memory allocations and garbage collection.'''

    parser = argparse.ArgumentParser(description=textwrap.dedent(description),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('camera_id', default=None, nargs='?',
                        help='ID of the camera to use (using first camera if not specified)')
    parser.add_argument('-d', '--destination_buffer', action='store_true',
                        help='If this option is given, a `destination_buffer` will be used in '
                             'calls to `convert_pixel_format`')
    return parser.parse_args()


def get_camera(camera_id: Optional[str]) -> vmbpy.Camera:
    with vmbpy.VmbSystem.get_instance() as vmb:
        if camera_id:
            try:
                return vmb.get_camera_by_id(camera_id)

            except vmbpy.VmbCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vmb.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')

            return cams[0]


def user_select_from_list(options: List[Any], msg: str = '') -> Any:
    if not msg:
        msg = 'Please select one of the following:\n'
    padding_width = len(str(len(options)))
    for idx, element in enumerate(options):
        msg += f'  [{idx:{padding_width}d}] - {str(element)}\n'
    while True:
        user_input = input(msg)
        try:
            selected_index = int(user_input)
        except ValueError:
            # The user probably typed in the name of the pixel format. Try to find it in the list
            try:
                selected_index = tuple(map(str, options)).index(user_input)
            except ValueError:
                print(f'Could not find element "{user_input}" in the list of options.')
                continue
        try:
            selected = options[selected_index]
            break
        except IndexError:
            print(f'Selected index {selected_index} is not valid.')
    print(f'Selected option: {str(selected)}')
    return selected


class FrameProducer:
    def __init__(self, cam: vmbpy.Camera, use_destination_buffer):
        self.cam = cam
        self.use_destination_buffer = use_destination_buffer
        # This will later be our user supplied buffer to the convert_pixel_format function. We will
        # allocate it appropriately once we receive our first frame from the camera
        self.numpy_buffer = None

    def __call__(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        if self.use_destination_buffer:
            if self.numpy_buffer is None:
                # Let VmbPy allocate new memory for transformation on the first received frame
                # because we do not yet have a prepared buffer. It is recommended to do this by
                # performing the conversion once without a destination_buffer and reuse the result
                # of that call for future conversions.
                converted_frame = frame.convert_pixel_format(self.target_format)
                # The memory allocated by this conversion will be reused for all other
                # transformations. We save the numpy representation for future use. These steps make
                # sure that the numpy buffer has an appropriate data type and shape for our
                # conversions. The buffer may only be reused while the shape of the frame and target
                # pixel format remains unchanged
                self.numpy_buffer = converted_frame.as_numpy_ndarray()
            # Use same memory as self.numpy_buffer to store conversion result. Use the `data` field
            # of the numpy array as `destination_buffer` parameter
            converted_frame = frame.convert_pixel_format(self.target_format,
                                                         destination_buffer=self.numpy_buffer.data)
        else:
            # If no destination_buffer is given, VmbPy will allocate new memory for each conversion.
            # This might introduce additional overhead e.g. from the garbage collector
            converted_frame = frame.convert_pixel_format(self.target_format)
        print(f'Converted frame from {frame.get_pixel_format()} '
              f'to {converted_frame.get_pixel_format()}.\n'
              f'Conversion result: {converted_frame}')
        # Requeue the original frame for future frame transmissions
        stream.queue_frame(frame)

    def setup_camera(self):
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            stream = cam.get_streams()[0]
            stream.GVSPAdjustPacketSize.run()

            while not stream.GVSPAdjustPacketSize.is_done():
                pass

        except (AttributeError, vmbpy.VmbFeatureError):
            pass

    def run(self):
        with vmbpy.VmbSystem.get_instance():
            with self.cam:
                self.setup_camera()
                pixel_formats = self.cam.get_pixel_formats()
                record_format = user_select_from_list(pixel_formats,
                                                      'Select PixelFormat that should be used '
                                                      'to record frames:\n')
                self.cam.set_pixel_format(record_format)
                convertible_formats = record_format.get_convertible_formats()
                self.target_format = user_select_from_list(convertible_formats,
                                                           'Select PixelFormat that the recorded '
                                                           'frames should be converted to:\n')
                try:
                    self.cam.start_streaming(self)
                    input('Press <enter> to stop Frame acquisition.')
                finally:
                    self.cam.stop_streaming()


if __name__ == '__main__':
    print_preamble()
    args = parse_args()

    with vmbpy.VmbSystem.get_instance() as vmb:
        cam = get_camera(args.camera_id)
        producer = FrameProducer(cam, args.destination_buffer)
        producer.run()
