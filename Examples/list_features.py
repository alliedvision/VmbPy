"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
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
import argparse
import sys

from vmbpy import *


def print_preamble():
    print('///////////////////////////////////')
    print('/// VmbPy List Features Example ///')
    print('///////////////////////////////////\n')


def abort(reason: str, return_code: int = 1):
    print(reason + '\n')

    sys.exit(return_code)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        type=str,
                        help='The maximum visibility level of features that should be printed '
                             '(default = %(default)s)',
                        # Allow all visibility levels except 'Unknown'
                        choices=list(map(lambda x: x.name,
                                         filter(lambda x: x != FeatureVisibility.Unknown,
                                                FeatureVisibility))),
                        default=FeatureVisibility.Guru.name)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t',
                       type=int,
                       metavar='TransportLayerIndex',
                       help='Show transport layer features')
    group.add_argument('-i',
                       type=int,
                       metavar='InterfaceIndex',
                       help='Show interface features')
    group.add_argument('-c',
                       type=str,
                       default='0',
                       metavar='(CameraIndex | CameraId)',
                       help='Show the remote device features of the specified camera')
    group.add_argument('-l',
                       type=str,
                       metavar='(CameraIndex | CameraId)',
                       help='Show the local device features of the specified camera')
    group.add_argument('-s',
                       type=str,
                       nargs=2,
                       metavar=('(CameraIndex | CameraId)', 'StreamIndex'),
                       help='Show the features of a stream for the specified camera')

    return parser.parse_args()


def print_all_features(module: FeatureContainer, max_visibility_level: FeatureVisibility):
    for feat in module.get_all_features():
        if feat.get_visibility() <= max_visibility_level:
            print_feature(feat)


def print_feature(feature: FeatureTypes):
    try:
        value = feature.get()

    except (AttributeError, VmbFeatureError):
        value = None

    print('/// Feature name   : {}'.format(feature.get_name()))
    print('/// Display name   : {}'.format(feature.get_display_name()))
    print('/// Tooltip        : {}'.format(feature.get_tooltip()))
    print('/// Description    : {}'.format(feature.get_description()))
    print('/// SFNC Namespace : {}'.format(feature.get_sfnc_namespace()))
    print('/// Value          : {}\n'.format(str(value)))


def get_transport_layer(index: int) -> TransportLayer:
    with VmbSystem.get_instance() as vmb:
        try:
            return vmb.get_all_transport_layers()[index]
        except IndexError:
            abort('Could not find transport layer at index \'{}\'. '
                  'Only found \'{}\' transport layer(s)'
                  ''.format(index, len(vmb.get_all_transport_layers())))


def get_interface(index: int) -> Interface:
    with VmbSystem.get_instance() as vmb:
        try:
            return vmb.get_all_interfaces()[index]
        except IndexError:
            abort('Could not find interface at index \'{}\'. Only found \'{}\' interface(s)'
                  ''.format(index, len(vmb.get_all_interfaces())))


def get_camera(camera_id_or_index: str) -> Camera:
    camera_index = None
    camera_id = None
    try:
        camera_index = int(camera_id_or_index)
    except ValueError:
        # Could not parse `camera_id_or_index` to an integer. It is probably a device ID
        camera_id = camera_id_or_index

    with VmbSystem.get_instance() as vmb:
        if camera_index is not None:
            cams = vmb.get_all_cameras()
            if not cams:
                abort('No cameras accessible. Abort.')
            try:
                return cams[camera_index]
            except IndexError:
                abort('Could not find camera at index \'{}\'. Only found \'{}\' camera(s)'
                      ''.format(camera_index, len(cams)))

        else:
            try:
                return vmb.get_camera_by_id(camera_id)

            except VmbCameraError:
                abort('Failed to access camera \'{}\'. Abort.'.format(camera_id))


def main():
    print_preamble()
    args = parse_args()
    visibility_level = FeatureVisibility[args.v]

    with VmbSystem.get_instance():
        if args.t is not None:
            tl = get_transport_layer(args.t)
            print_all_features(tl, visibility_level)
        elif args.i is not None:
            inter = get_interface(args.i)
            print_all_features(inter, visibility_level)
        elif args.l is not None:
            cam = get_camera(args.l)
            with cam:
                local_device = cam.get_local_device()
                print_all_features(local_device, visibility_level)
        elif args.s is not None:
            cam = get_camera(args.s[0])
            with cam:
                try:
                    stream_index = int(args.s[1])
                except ValueError:
                    abort('Could not parse \'{}\' to a stream index integer'.format(args.s[1]))
                try:
                    stream = cam.get_streams()[stream_index]
                    print_all_features(stream, visibility_level)
                except IndexError:
                    abort('Could not get stream at index \'{}\'. Camera provides only \'{}\' '
                          'stream(s)'.format(stream_index, len(cam.get_streams())))
        else:
            cam = get_camera(args.c)
            with cam:
                print_all_features(cam, visibility_level)


if __name__ == '__main__':
    main()
