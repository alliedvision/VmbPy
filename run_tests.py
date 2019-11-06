"""VimbaPython setup script

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import os
import sys
import shutil
import subprocess

UNITTEST_SUITE = 'all'
UNITTEST_CAMERA = ''
REPORT_DIR = 'Test_Reports'

def fprint(line):
    print(line, flush=True)


def stringify_list(l):
    list_str = ''
    for e in l:
        list_str += e + ' '

    return list_str

def static_test():
    fprint('Execute Static Test: flake8')
    subprocess.run(['flake8', 'vimba'], shell=True)
    fprint('')

    fprint('Execute Static Test: mypy')
    subprocess.run(['mypy', 'vimba'], shell=True)
    fprint('')


def unit_test():
    global UNITTEST_SUITE
    global UNITTEST_CAMERA

    fprint('Execute Unit tests and measure coverage:')
    cmd = ['coverage', 'run', 'Test/runner.py', UNITTEST_SUITE, 'console', UNITTEST_CAMERA]
    subprocess.run(cmd, shell=True)
    fprint('')

    fprint('Coverage during test execution:')
    subprocess.run(['coverage', 'report', '-m'], shell=True)
    fprint('')

    coverage_file = '.coverage'
    if os.path.exists(coverage_file):
        os.remove(coverage_file)


def setup_junit():
    global REPORT_DIR

    if os.path.exists(REPORT_DIR):
        shutil.rmtree(REPORT_DIR, ignore_errors=True)

    os.mkdir(REPORT_DIR)



def static_test_junit():
    global REPORT_DIR

    fprint('Execute Static Test: flake8')
    cmd = ['flake8', 'vimba', '--output-file=' + REPORT_DIR + '/flake8.txt']
    subprocess.run(cmd, shell=True)
    cmd = ['flake8_junit', REPORT_DIR + '/flake8.txt', REPORT_DIR + '/flake8_junit.xml']
    subprocess.run(cmd, shell=True)
    fprint('')

    fprint('Execute Static Test: mypy')
    cmd = ['mypy', 'vimba', '--junit-xml', REPORT_DIR + '/mypy_junit.xml']
    subprocess.run(cmd, shell=True)
    fprint('')


def unit_test_junit():
    global REPORT_DIR
    global UNITTEST_SUITE
    global UNITTEST_CAMERA

    fprint('Execute Unit tests and measure coverage:')
    cmd = ['coverage', 'run', 'Test/runner.py', UNITTEST_SUITE, 'junit_xml', REPORT_DIR, UNITTEST_CAMERA]
    subprocess.run(cmd, shell=True)
    fprint('')

    fprint('Generate Coverage reports:')
    subprocess.run(['coverage', 'xml', '-o', REPORT_DIR + '/coverage.xml'], shell=True)
    subprocess.run(['coverage', 'html', '-d', REPORT_DIR + '/coverage_html'], shell=True)
    fprint('')

    coverage_file = '.coverage'
    if os.path.exists(coverage_file):
        os.remove(coverage_file)


def test():
    static_test()
    unit_test()


def test_junit():
    setup_junit()
    static_test_junit()
    unit_test_junit()


def main():
    arg_to_func = {
        'static_test': static_test,
        'unit_test': unit_test,
        'test': test,
        'setup_junit': setup_junit,
        'static_test_junit': static_test_junit,
        'unit_test_junit': unit_test_junit,
        'test_junit': test_junit
    }

    args = sys.argv[1:]

    if not args:
        msg = 'No arguments supplied. Available arguments are: {}'
        raise Exception(msg.format(stringify_list(arg_to_func.keys())))

    for arg in args:

        func = arg_to_func.get(arg)

        if func:
            func()

        else:
            msg = 'Invalid argument supplied. Available arguments are: {}'
            raise Exception(msg.format(stringify_list(arg_to_func.keys())))


if __name__ == '__main__':
    main()
