import os
import sys
import unittest

test_cam_id: str = ''

# Inject 'assertNotRaise' to default test module. Tests are derived from this class.
def _assertNoRaise(self, func, *args, **kwargs):
    try:
        func(*args, **kwargs)

    except BaseException as e:
      self.fail('Function raised: {}'.format(e))

# Inject shared test camera id into the base TestCase
def _get_test_camera_id(self) -> str:
    return unittest.TestCase.test_cam_id

def _set_test_camera_id(test_cam_id) -> str:
    unittest.TestCase.test_cam_id = test_cam_id

unittest.TestCase.assertNoRaise = _assertNoRaise
unittest.TestCase.set_test_camera_id = _set_test_camera_id
unittest.TestCase.get_test_camera_id = _get_test_camera_id

# Disable Vimba network discovery to speedup tests.
from vimba import Vimba
Vimba.get_instance().set_network_discovery(False)

# import tests cases
import tests.c_binding_test
import tests.util_runtime_type_check_test
import tests.util_tracer_test
import tests.vimba_test

import real_cam_tests.vimba_test
import real_cam_tests.feature_test
import real_cam_tests.camera_test
import real_cam_tests.frame_test

# Assign test cases to test suites
BASIC_TEST_MODS = [
    tests.c_binding_test,
    tests.util_runtime_type_check_test,
    tests.util_tracer_test,
    tests.vimba_test
]

REAL_CAM_TEST_MODS = [
    real_cam_tests.vimba_test,
    real_cam_tests.feature_test,
    real_cam_tests.camera_test,
    real_cam_tests.frame_test
]


def usage(fail_msg):
    print(fail_msg, '\n')
    print('runner.py <TestSuite> <OutputFormat> [ReportDirectory] [CameraId]')
    print('Options:')
    print('    TestSuite - Either \'basic\', \'real_cam\', \'all\'')
    print('    OutputFormat - Either \'console\' or \'junit_xml\'')
    print('    ReportDirectory - Required if OutputFormat is junit_xml')
    print('    CameraId - CameraId to use. If not given, FileTL cameras are used while testing.')

    sys.exit(1)


def parse_args():
    result = {'CameraId': 'DEV_Testimage1'}

    args = sys.argv[1:]

    if len(args) not in (2, 3, 4):
       usage('runner.py invalid argument number. Abort.')

    arg = args[0]
    if arg not in ('basic', 'real_cam', 'all'):
        usage('Parameter \'TestSuite\' is not \'basic\', \'real_cam\' or \'all\'. Abort')

    result['TestSuite'] = arg

    arg = args[1]
    if arg not in ('console', 'junit_xml'):
        usage('Parameter \'OutputFormat\' is not \'console\' or \'junit_xml\'. Abort')

    result['OutputFormat'] = arg

    if arg == 'junit_xml':
        if len(args) not in (3, 4):
            usage('Missing ReportDirectory. Abort.')

        result['ReportDirectory'] = args[2]

        if len(args) == 4:
            result['CameraId'] = args[3]

    else:
        # Try to use the last argument as CameraID
        if len(args) == 3:
            result['CameraId'] = args[2]

    return result

def setup_file_tl():
    if sys.platform != 'win32':
        raise Exception('Using FileTL on non-Windows Platform. Use real camera instead.')

    file_tl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'real_cam_data')

    # TODO: Might require so sanity checking for different Architectures and Operating Systems...
    tl_path = os.environ.get('GENICAM_GENTL64_PATH')

    if not tl_path:
        raise Exception('GENICAM_GENTL64_PATH variable is not set')

    # Append FileTL during tests
    os.environ['GENICAM_GENTL64_PATH'] = tl_path + ';' + file_tl_dir


def main():
    args = parse_args()
    loader = unittest.TestLoader()

    unittest.TestCase.set_test_camera_id(args['CameraId'])

    # Select TestRunner
    if args['OutputFormat'] == 'console':
        runner = unittest.TextTestRunner(verbosity=1)

    else:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(output=args['ReportDirectory'])

    # Prepare TestSuites
    suite_basic = unittest.TestSuite()
    for mod in BASIC_TEST_MODS:
        suite_basic.addTests(loader.loadTestsFromModule(mod))

    suite_real_cam = unittest.TestSuite()
    for mod in REAL_CAM_TEST_MODS:
        suite_real_cam.addTests(loader.loadTestsFromModule(mod))

    # Execute TestSuites
    if args['TestSuite'] == 'basic':
        runner.run(suite_basic)

    elif args['TestSuite'] == 'real_cam':
        if args['CameraId'] == 'DEV_Testimage1':
            setup_file_tl()

        runner.run(suite_real_cam)

    elif args['TestSuite'] == 'all':
        if args['CameraId'] == 'DEV_Testimage1':
            setup_file_tl()

        runner.run(suite_basic)
        runner.run(suite_real_cam)


if __name__ == '__main__':
    main()
