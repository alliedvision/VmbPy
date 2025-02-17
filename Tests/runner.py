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

from helpers import VmbPyTestCase, reset_default_user_set, load_default_user_set

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
        self.add_argument('--test_filter_file',
                          help='Optional file containing test filter rules')
        output_group = self.add_mutually_exclusive_group(required=True)
        output_group.add_argument('--console',
                                  help='log output to console',
                                  action='store_true')
        output_group.add_argument('--junit_xml',
                                  help='log output to junit compatible xml file. The file is '
                                       'placed inside report_dir',
                                  metavar='report_dir')


class CustomTestLoader(unittest.TestLoader):

    def _parse_file(file_path):
        with open(file_path, 'r') as file:
            lines = [line.split('#')[0].strip() for line in file if line.split('#')[0].strip()]
        return lines

    def __init__(self, test_filter_file: str = None):
        super().__init__()
        self.test_whitelist = None
        if test_filter_file:
            self.test_whitelist = CustomTestLoader._parse_file(test_filter_file)
            print(f"Found {len(self.test_whitelist)} tests in test_filter_file {test_filter_file}")

    def loadTestsFromModule(self, module):
        tests = super().loadTestsFromModule(module)
        if self.test_whitelist is None:
            return tests
        filtered_tests = []
        for test in tests:
            if isinstance(test, unittest.suite.TestSuite):
                for subtest in test:
                    if subtest.id() in self.test_whitelist:
                        filtered_tests.append(subtest)
        return unittest.TestSuite(filtered_tests)


def _blacklist_tests(test_suite, blacklist):
    for test in test_suite:
        # Process TestSuites recursively
        if isinstance(test, unittest.TestSuite):
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

    if not VmbPyTestCase.get_test_camera_id():
        # If no camera ID has been set so far, let the test class try to determine it automatically
        VmbPyTestCase.setUpClass()

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


if __name__ == '__main__':
    arg_parser = Parser()
    args = arg_parser.parse_args()
    loader = CustomTestLoader(args.test_filter_file)

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
    import basic_tests.util_vmb_enum_test
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
        basic_tests.util_runtime_type_check_test,
        basic_tests.util_tracer_test,
        basic_tests.util_context_decorator_test,
        basic_tests.util_vmb_enum_test,
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
        real_cam_tests.stream_test
    ]

    # Prepare TestSuite
    test_suite = unittest.TestSuite()
    if args.suite in ('basic', 'all'):
        for mod in BASIC_TEST_MODS:
            test_suite.addTests(_blacklist_tests(loader.loadTestsFromModule(mod), args.blacklist))

    if args.suite in ('real_cam', 'all'):
        for mod in REAL_CAM_TEST_MODS:
            test_suite.addTests(_blacklist_tests(loader.loadTestsFromModule(mod), args.blacklist))

    reset_default_user_set(VmbPyTestCase.get_test_camera_id())
    load_default_user_set(VmbPyTestCase.get_test_camera_id())
    result = runner.run(test_suite)
    reset_default_user_set(VmbPyTestCase.get_test_camera_id())
    load_default_user_set(VmbPyTestCase.get_test_camera_id())
    sys.exit(0 if result.wasSuccessful() else 1)
