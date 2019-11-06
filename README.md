## VimbaPython
#### Prerequisites
1) Install python version 3.7 or above and configure it as default python interpreter.
On Linux platforms, the default python interpreter might be some python 2 version.
If this is the case use 'python3' command instead of 'python'. Verify the interpreter version by executing:

```
python --version
```

2) Install pip. On Windows, ensure that pip was installed along with the python interpreter.
On Linux install pip via the distributions packet manager. On Linux systems with different
coexisting python version, pip for the installed python3 interpreter is often executed by
calling 'pip3'. If this is the case on your system, use the 'pip3' command instead of 'pip'.

3) Install VimbaSDK. On Windows install a Vimba including ImageTransform. On Linux install at
least a single TransportLayer (this sets the GENICAM Environment Variables that is required to
locate Vimba).

### Installation via pip
VimbaPython has several, optional dependencies. All installations start by opening a terminal
and navigating to the VimbyPython root directory (containing setup.py).

For a minimal installation, execute:

```
pip install .
```

For a installation with OpenCV/Numpy - support, execute:

```
pip install .[numpy-export,opencv-export]
```

For a installation with Unittest - support, execute:

```
pip install .[test]
```

If you want to execute the unittests, ensure that binaries installed by pip can be
called from the terminal directly. On some systems pip installs to locations that are not
covered by Environments 'PATH' - variable, ensure that tools like 'coverage' can be called from
the command line.

### Running examples
After installing VimbaPython all examples can be directly executed. The
following example prints basic information on all currently detected cameras:

```
python Examples/list_cameras.py
```

### Running tests
VimbaPythons tests are divided into unit and static tests. The tests are configured and executed by
execution of the script 'run_tests.py'. Executing

```
python run_tests.py test
```

executes all static tests (flake8, mypy) and executes all unit tests. The output is printed to
command line. Executing

```
python run_tests.py test_junit
```

executes all tests as well but the output of each tool export in junit-format to the
Test_Reports - Directory.

The unit tests are divided into tests that work without a connected camera and tests
that require a camera. By editing 'UNITTEST_SUITE' in 'run_tests.py', the test suite
can be selected ('basic', 'real_cam', 'all' are valid options). In addition the Camera Id, that
should be used for testing can be specified by setting 'UNITTEST_CAMERA'. In case a Camera is
specified, it is only used if 'UNITTEST_SUITE' is 'real_cam' or 'all'.
