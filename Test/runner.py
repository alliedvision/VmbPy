import os
import sys
import unittest
import xmlrunner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import tests cases
import c_binding_api_test
import c_binding_types_test
import c_binding_util_test

import util_runtime_type_check_test


INDEPENDENT_TEST_MODS = [
    c_binding_api_test,
    c_binding_types_test,
    c_binding_util_test,
    util_runtime_type_check_test
]

FILETL_TEST_MODS = [
]

CAM_TEST_MODS = [
]


def usage(fail_msg):
    print(fail_msg, '\n')
    print('runner.py <TestSuite> <OutputFormat> [ReportDirectory]')
    print('Options:')
    print('    TestSuite - Either \'file_tl\', \'cam\', \'all\'')
    print('    OutputFormat - Either \'console\' or \'junit_xml\'')
    print('    ReportDirectory - Required if OutputFormat is junit_xml')

    sys.exit(1)


def parse_args():
    result = {}
    args = sys.argv[1:]

    if len(args) not in (2, 3):
       usage('runner.py invalid argument number. Abort.')

    arg = args[0]
    if arg not in ('file_tl', 'cam', 'all'):
        usage('Parameter \'TestSuite\' is not \'file_tl\', \'cam\' or \'all\'. Abort')

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


def main():
    args = parse_args()
    loader = unittest.TestLoader()

    # Select TestRunner
    if args['OutputFormat'] == 'console':
        runner = unittest.TextTestRunner(verbosity=1)

    else:
        runner = xmlrunner.XMLTestRunner(output=args['ReportDirectory'])

    # Prepare TestSuites
    suite_independent = unittest.TestSuite()
    for mod in INDEPENDENT_TEST_MODS:
        suite_independent.addTests(loader.loadTestsFromModule(mod))

    suite_file_tl = unittest.TestSuite()
    for mod in FILETL_TEST_MODS:
        suite_file_tl.addTests(loader.loadTestsFromModule(mod))

    suite_cam = unittest.TestSuite()
    for mod in CAM_TEST_MODS:
        suite_cam.addTests(loader.loadTestsFromModule(mod))

    # Execute TestSuites
    if args['TestSuite'] == 'file_tl':
        runner.run(suite_independent)
        runner.run(suite_file_tl)

    elif args['TestSuite'] == 'cam':
        runner.run(suite_independent)
        runner.run(suite_cam)

    elif args['TestSuite'] == 'all':
        runner.run(suite_independent)
        runner.run(suite_file_tl)
        runner.run(suite_cam)


if __name__ == '__main__':
    main()
