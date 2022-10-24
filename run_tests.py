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
import os
import shutil
import subprocess

from Tests.runner import Parser


def fprint(line):
    print(line, flush=True)


def stringify_list(l):
    list_str = ''
    for e in l:
        list_str += e + ' '

    return list_str


def static_test():
    fprint('Execute Static Test: flake8')
    subprocess.run('flake8 vmbpy', shell=True)
    subprocess.run('flake8 Examples --ignore=F405,F403', shell=True)
    subprocess.run('flake8 Tests --ignore=F405,F403,E402', shell=True)
    fprint('')

    fprint('Execute Static Test: mypy')
    subprocess.run('mypy vmbpy', shell=True, check=True)
    fprint('')


def unit_test(testsuite, testcamera, blacklist):
    blacklist = " ".join(blacklist)

    fprint('Execute Unit tests and measure coverage:')
    if testsuite == 'basic':
        cmd = 'coverage run Tests/runner.py -s basic --console {}'.format(blacklist)

    else:
        cmd = 'coverage run Tests/runner.py -s {} --console {}'
        cmd = cmd.format(testsuite, blacklist)
        if testcamera:
            cmd += ' -c {}'.format(testcamera)

    subprocess.run(cmd, shell=True, check=True)
    fprint('')

    fprint('Coverage during test execution:')
    subprocess.run('coverage report -m', shell=True, check=True)
    fprint('')

    coverage_file = '.coverage'
    if os.path.exists(coverage_file):
        os.remove(coverage_file)


def setup_junit(report_dir):
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir, ignore_errors=True)

    os.mkdir(report_dir)


def static_test_junit(report_dir):
    fprint('Execute Static Test: flake8')
    cmd = 'flake8 vmbpy --output-file=' + report_dir + '/flake8.txt'
    subprocess.run(cmd, shell=True, check=True)

    cmd = 'flake8_junit ' + report_dir + '/flake8.txt ' + report_dir + '/flake8_junit.xml'
    subprocess.run(cmd, shell=True, check=True)
    fprint('')

    fprint('Execute Static Test: mypy')
    cmd = 'mypy vmbpy --junit-xml ' + report_dir + '/mypy_junit.xml'
    subprocess.run(cmd, shell=True, check=True)
    fprint('')


def unit_test_junit(report_dir, testsuite, testcamera, blacklist):
    fprint('Execute Unit tests and measure coverage:')

    blacklist = " ".join(blacklist)
    if testsuite == 'basic':
        cmd = 'coverage run --branch Tests/runner.py -s basic --junit_xml {} {}'
        cmd = cmd.format(report_dir, blacklist)

    else:
        cmd = 'coverage run --branch Tests/runner.py -s {} --junit_xml {}'
        cmd = cmd.format(testsuite, report_dir,)
        if testcamera:
            cmd += ' -c {}'.format(testcamera)
        cmd += ' {}'.format(blacklist)

    subprocess.run(cmd, shell=True, check=True)
    fprint('')

    fprint('Generate Coverage reports:')
    subprocess.run('coverage report -m', shell=True, check=True)
    subprocess.run('coverage xml -o ' + report_dir + '/coverage.xml', shell=True, check=True)
    fprint('')

    coverage_file = '.coverage'
    if os.path.exists(coverage_file):
        os.remove(coverage_file)


def test(testsuite, testcamera, blacklist):
    static_test()
    unit_test(testsuite, testcamera, blacklist)


def test_junit(report_dir, testsuite, testcamera, blacklist):
    setup_junit(report_dir)
    static_test_junit(report_dir)
    unit_test_junit(report_dir, testsuite, testcamera, blacklist)


def main():
    arg_parser = Parser()
    args = arg_parser.parse_args()

    if args.console:
        test(args.suite, args.camera_id, args.blacklist)

    elif args.junit_xml:
        test_junit(args.junit_xml, args.suite, args.camera_id, args.blacklist)


if __name__ == '__main__':
    main()
