VimbaPython - a python wrapper for AlliedVisions VimbaSDK
===============
At first, a word of caution. This early release of VimbaPython is considered a beta version, published to get
customer feedback early on. Although the API is relatively stable, it should not to be used in production
code until the official release of VimbaPython.

Aside to the VimbaPython source code, we publish our tests as well. If you encounter any issues
while using VimbaPython, feel free to run the tests and send us the test results. This helps us
to improve out software.

We would like to invite you to try VimbaPython and to give us feedback. Feel free to contact us
<INSERT CONTACT INFO> if you have any ideas on improving VimbaPython.

Requirements
===============
In general, VimbaPython requires python3.7, pip, VimbaC and VimbaImageTransform. Fulfilling the
requirements is highly platform specific, please refer to the matching installation instructions.

Requirements for Windows
---------------
The following instructions describe how to install/update python on Windows. If your system requires
multiple, coexisting python installations, consider using [pyenv-win](https://github.com/pyenv-win/pyenv-win)
to install and maintain multiple python installations.

1. Download the latest python release from [python.org](https://www.python.org/downloads/windows/)
2. Execute the downloaded installer, ensure that pip is installed. After installation verify the installation
   by typing the following commands into the window command line:

        python --version
        python -m pip --version

    The python version must be above 3.7 and pip must use the python version.

3. Download the latest [VimbaSDK](https://www.alliedvision.com/de/produkte/software.html) for Windows.
4. Execute the downloaded Vimba installer. Ensure that VimbaC, VimbaImageTransform and at least one
   TransportLayer is installed.

Requirements for Linux
---------------
On Linux, the python installation process depends heavily on the distribution in use. If python3.7
is not available for your distribution or your system requires multiple python versions
to coexist, use [pyenv](https://realpython.com/intro-to-pyenv/) instead.

1. Install/Update python3.7 with the packet manager of your distribution.
2. Install/Update pip with the packet manager of your distribution.
   Verify your python installation by opening a terminal and entering:

        python --version
        python -m pip --version

3. Download the latest [VimbaSDK](https://www.alliedvision.com/de/produkte/software.html) for
   the underlaying architecture of your host system.
4. Install at least one TransportLayer by executing the TransportLayers "Install.sh" (this sets the
   GENICAM_GENTLXX_PATH Variables required to locate VimbaC and VimbaImageTransport). After executing
   Install.sh, reboot your system to finish the Vimba installation.

Installation
===============
After fulfilling the requirements, the installation process of VimbaPython is the same for
all operating systems:

1. Download the latest version of [VimbaPython](https://ADD_LINK_TO_REPO).
2. Open a terminal and navigate to the download location of VimbaPython (contains setup.py)

Basic Installation
---------------
Execute the following command:

        python -m pip install .


Installation with optional Numpy/OpenCV export
---------------
Execute the following command:

        python -m pip install .[numpy-export,opencv-export]

For ARM users only: If installation of "opencv-export" fails, pip is not able to install
"opencv-python" for ARM - Platforms. This is a known issue on embedded ARM-Boards.
If you are affected by this, install VimbaPython without optional dependencies and try to install
OpenCV in a different way (e.g. with your operating systems packet manager). The OpenCV installation
can be verified by running the example "Examples/asychronous_grab_opencv.py".

Installation with optional test support.
---------------
Execute the following command:

        python -m pip install .[test]

Running Examples
===============
After installing VimbaPython all examples can be directly executed. The
following example prints basic information on all connected cameras:

        python Examples/list_cameras.py

Running Tests
===============
VimbaPythons tests are divided into unittests and multiple static test tools.
These tests are configured and executed by the script 'run_tests.py' in the VimbaPython root
directory.

The unittests are divided into three testsuites:
1. The testsuite 'basic' does not require a connected camera. It can be run on any system.
2. The testsuite 'real_cam' contains tests that require a connected camera.
   To execute these tests a camera id must be specified. The Vimbaviewer can be used to obtain
   the Camera Id of any connected camera.
3. The testsuite 'all' contains all tests from 'basic' and 'real_cam'. Since 'real_cam' is used,
   a camera id must be specified.

The test results are either printed to the command line or can be exported in junit format.
If the test results are exported in junit format, the results are stored in 'Test_Reports'
after test execution. The following examples show to run all possible test configurations.

Running testssuite 'basic' with console output:

        python run_tests.py test -s basic

Running testssuite 'basic' with junit export:

        python run_tests.py test_junit -s basic

Running testssuite 'real_cam' with console output:

        python run_tests.py test -s real_cam -c <CAMERA_ID>

Running testssuite 'real_cam' with junit export:

        python run_tests.py test_junit -s real_cam -c <CAMERA_ID>

Running testssuite 'all' with console output:

        python run_tests.py test -s all -c <CAMERA_ID>

Running testssuite 'all' with junit export:

        python run_tests.py test_junit -s all -c <CAMERA_ID>
