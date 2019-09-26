import os
import sys
import unittest
import xmlrunner

# Add relative location to vimba to search path.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Inject 'assertNotRaise' to default test module. Tests are derived from this class.
def _assertNoRaise(self, func, *args, **kwargs):
    try:
        func(*args, **kwargs)

    except:
      self.fail('Function raised')

unittest.TestCase.assertNoRaise = _assertNoRaise

# Disable Vimba network discovery to speedup tests.
from vimba import Vimba
Vimba.get_instance().set_network_discovery(False)

# import tests cases
import tests.c_binding_api_test
import tests.c_binding_types_test
import tests.c_binding_util_test
import tests.util_runtime_type_check_test
import tests.util_tracer_test
import tests.vimba_test

import file_tl_tests.vimba_test
import file_tl_tests.feature_test

# Assign test cases to test suites
BASIC_TEST_MODS = [
    tests.c_binding_api_test,
    tests.c_binding_types_test,
    tests.c_binding_util_test,
    tests.util_runtime_type_check_test,
    tests.util_tracer_test,
    tests.vimba_test
]

FILETL_TEST_MODS = [
    file_tl_tests.vimba_test,
    file_tl_tests.feature_test
]


def usage(fail_msg):
    print(fail_msg, '\n')
    print('runner.py <TestSuite> <OutputFormat> [ReportDirectory]')
    print('Options:')
    print('    TestSuite - Either \'basic\', \'file_tl\', \'all\'')
    print('    OutputFormat - Either \'console\' or \'junit_xml\'')
    print('    ReportDirectory - Required if OutputFormat is junit_xml')

    sys.exit(1)


def parse_args():
    result = {}
    args = sys.argv[1:]

    if len(args) not in (2, 3):
       usage('runner.py invalid argument number. Abort.')

    arg = args[0]
    if arg not in ('basic', 'file_tl', 'all'):
        usage('Parameter \'TestSuite\' is not \'basic\', \'file_tl\' or \'all\'. Abort')

    result['TestSuite'] = arg

    arg = args[1]
    if arg not in ('console', 'junit_xml'):
        usage('Parameter \'OutputFormat\' is not \'console\' or \'junit_xml\'. Abort')

    result['OutputFormat'] = arg

    if arg == 'junit_xml':
        if len(args) != 3:
            usage('Missing ReportDirectory. Abort.')

        result['ReportDirectory'] = args[2]

    return result

def setup_file_tl():
    file_tl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_tl_data')

    # TODO: Might require so sanity checking for different Architectures and Operating Systems...
    tl_path = os.environ.get('GENICAM_GENTL64_PATH')

    if not tl_path:
        raise Exception('GENICAM_GENTL64_PATH variable is not set')

    # Append FileTL during tests
    os.environ['GENICAM_GENTL64_PATH'] = tl_path + ";" + file_tl_dir


def main():
    args = parse_args()
    loader = unittest.TestLoader()

    # Select TestRunner
    if args['OutputFormat'] == 'console':
        runner = unittest.TextTestRunner(verbosity=1)

    else:
        runner = xmlrunner.XMLTestRunner(output=args['ReportDirectory'])

    # Prepare TestSuites
    suite_basic = unittest.TestSuite()
    for mod in BASIC_TEST_MODS:
        suite_basic.addTests(loader.loadTestsFromModule(mod))

    suite_file_tl = unittest.TestSuite()
    for mod in FILETL_TEST_MODS:
        suite_file_tl.addTests(loader.loadTestsFromModule(mod))

    # Execute TestSuites
    if args['TestSuite'] == 'basic':
        runner.run(suite_basic)

    elif args['TestSuite'] == 'file_tl':
        setup_file_tl()

        runner.run(suite_file_tl)

    elif args['TestSuite'] == 'all':
        setup_file_tl()

        runner.run(suite_basic)
        runner.run(suite_file_tl)


if __name__ == '__main__':
    main()
