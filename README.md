## VimbaPython
#### Prerequisites
1) Install python version 3.7 or above and use it as default python interpreter. On linux platforms
the default python interpreter might be some python 2 version, if this is the case use the
'python3' instead of the 'python' command. Verify the interpreter version by executing:

```
python --version
```

2) Install pip. On windows, ensure that pip was installed along the python interpreter.
On Linux install pip via the operating systems packet manager. On linux systems where different
python versions coexist, pip for the installed python3 interpreter is often executed by
calling 'pip3'. If this is the case on your system use 'pip3' during the installation.

3) Install VimbaSDK. On Windows install a Vimba with ImageTransform support. On Linux install at
least a single TransportLayer (Sets the GENICAM Environment Variables that are required to
locate Vimba).

### Installation via pip
VimbaPython has serveral, optional dependencies. All installations start by opening a terminal
and navigating to the VimbyPython root directory (contains setup.py).

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
called from the terminal directly. On some systems pip installed to locations that are not
part of the PATH Environment variable.

### Running examples
After installing VimbaPython all shipped examples can be directly executed. The
following example prints basic information on all currently detected cameras:

```
python Examples/list_cameras.py
```

### Tests and Unittests
The supplied tests offer a small commandline interface to control test execution and output
formats. Executing

```
python Test/runner.py
```

shows all available options for running the commandline interface. In addition the unittests
and static test tools are tied together with a python script. By executing

```
python run_tests.py test
```

all tests are executed any the test results are printed to the commandline. If you execute

```
python run_tests.py test_junit
```

instead the unit tests and static tests generate test results in the junit format.
