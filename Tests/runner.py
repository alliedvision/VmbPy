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
import os
import sys
import unittest

# Add local directory to search path for test module import in this script.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from helpers import VmbPyTestCase

# Add VmbPy module at the start of the search path. The tests should run against the
# local vmbpy sources regardless of any existing installations.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs) -> None:
        description = 'vmbpy test runner'
        super().__init__(description=description, *args, **kwargs)
        self.add_argument('-s', '--suite',
                          help='Testsuite to execute. real_cam and all require a camera to run '
                               'tests against. Default: all',
                          choices=['basic', 'real_cam', 'all'],
                          default='all')
        self.add_argument('-c', '--camera_id',
                          help='Camera Id used while testing. If no ID is specified, the first '
                               'device that is found is used',
                          metavar='camera_id')
        self.add_argument('blacklist',
                          help='Optional sequence of unittest functions to skip',
                          nargs='*')
        output_group = self.add_mutually_exclusive_group(required=True)
        output_group.add_argument('--console',
                                  help='log output to console',
                                  action='store_true')
        output_group.add_argument('--junit_xml',
                                  help='log output to junit compatible xml file. The file is '
                                       'placed inside report_dir',
                                  metavar='report_dir')


def _blacklist_tests(test_suite, blacklist):
    for test in test_suite:
        # Process TestSuites recursively
        if type(test) == unittest.TestSuite:
            _blacklist_tests(test, blacklist)

        # Test is actually a TestCase. Add skip decorator to test
        # function if the test is blacklisted.
        else:
            name = test._testMethodName
            if name in blacklist:
                setattr(test, name, unittest.skip('Blacklisted')(getattr(test, name)))

    return test_suite


def print_test_execution_info():
    import vmbpy
    import platform
    import socket
    print('VmbPy test suite\n' + '*' * 80)
    alignment_width = 18

    def aligned_print(first, second):
        print(f'{first:<{alignment_width}}: {second}')
    aligned_print('API versions', vmbpy.VmbSystem.get_instance().get_version())
    aligned_print('Hostname', platform.node())
    try:
        aligned_print('IP Address:', socket.gethostbyname(socket.gethostname()))
    except:  # noqa E722
        # resolving host name may fail. Do not print IP in that case
        pass
    aligned_print('Operating System', platform.platform())
    aligned_print('Architecture', platform.machine())
    camera_id = VmbPyTestCase.get_test_camera_id()
    aligned_print('Camera ID', camera_id)
    if camera_id:
        with vmbpy.VmbSystem.get_instance() as vmb:
            try:
                with vmb.get_camera_by_id(camera_id) as cam:
                    try:
                        fw_version = cam.get_feature_by_name('DeviceFirmwareVersion').get()
                    except:  # noqa: E722
                        fw_version = ('Failed to read firmware version from '
                                      '\'DeviceFirmwareVersion\' feature')
                    try:
                        model_name = cam.get_feature_by_name('DeviceModelName').get()
                    except:  # noqa: E722
                        model_name = 'Failed to read model name from \'DeviceModelName\' feature'
            except:  # noqa: E722
                fw_version = 'Failed to open device'
                model_name = 'Failed to open device'
        aligned_print('Firmware version', fw_version)
        aligned_print('Model name', model_name)
    print('*' * 80)


def main():
    arg_parser = Parser()
    args = arg_parser.parse_args()
    loader = unittest.TestLoader()

    if args.camera_id:
        VmbPyTestCase.set_test_camera_id(args.camera_id)
    VmbPyTestCase.setUpClass()
    print_test_execution_info()

    # Select TestRunner
    if args.console:
        runner = unittest.TextTestRunner(verbosity=2)

    elif args.junit_xml:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(output=args.junit_xml)

    # Import tests cases
    import basic_tests.c_binding_test
    import basic_tests.frame_test
    import basic_tests.interface_test
    import basic_tests.persistable_feature_container_test
    import basic_tests.transport_layer_test
    import basic_tests.util_context_decorator_test
    import basic_tests.util_runtime_type_check_test
    import basic_tests.util_tracer_test
    import basic_tests.vimbax_common_test
    import basic_tests.vmbsystem_test
    import real_cam_tests.camera_test
    import real_cam_tests.chunk_access_test
    import real_cam_tests.feature_test
    import real_cam_tests.frame_test
    import real_cam_tests.local_device_test
    import real_cam_tests.persistable_feature_container_test
    import real_cam_tests.stream_test
    import real_cam_tests.vimbax_test

    # Assign test cases to test suites
    BASIC_TEST_MODS = [
        basic_tests.c_binding_test,
        basic_tests.frame_test,
        basic_tests.util_runtime_type_check_test,
        basic_tests.util_tracer_test,
        basic_tests.util_context_decorator_test,
        basic_tests.vimbax_common_test,
        basic_tests.vmbsystem_test,
        basic_tests.interface_test,
        basic_tests.transport_layer_test,
        basic_tests.persistable_feature_container_test
    ]

    REAL_CAM_TEST_MODS = [
        real_cam_tests.vimbax_test,
        real_cam_tests.feature_test,
        real_cam_tests.camera_test,
        real_cam_tests.frame_test,
        real_cam_tests.local_device_test,
        real_cam_tests.chunk_access_test,
        real_cam_tests.persistable_feature_container_test,
        real_cam_tests.stream_test,
        real_cam_tests.vimbax_test
    ]

    # Prepare TestSuites
    suite_basic = unittest.TestSuite()
    suite_cam = unittest.TestSuite()

    for mod in BASIC_TEST_MODS:
        suite_basic.addTests(_blacklist_tests(loader.loadTestsFromModule(mod), args.blacklist))

    for mod in REAL_CAM_TEST_MODS:
        suite_cam.addTests(_blacklist_tests(loader.loadTestsFromModule(mod), args.blacklist))

    # Execute TestSuites
    if args.suite == 'basic':
        runner.run(suite_basic)

    elif args.suite == 'real_cam':
        runner.run(suite_cam)

    elif args.suite == 'all':
        runner.run(suite_basic)
        runner.run(suite_cam)


if __name__ == '__main__':
    main()
