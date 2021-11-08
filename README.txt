Vimba Python API
===============

Prerequisites
===============
To use Vimba Python API, you need Python version 3.7 or higher.


Installing Python - Windows
---------------
If your system requires multiple, coexisting Python versions, consider 
using pyenv-win to install and maintain multiple Python installations:
https://github.com/pyenv-win/pyenv-win

We recommend installing Python with admin rights. 

1. Install Python: https://www.python.org/downloads/windows/
2. If pip >21.2 is used, read the instructions for all operating systems below.
3. To verify the installation, open the command prompt and enter:

      python --version
      python -m pip --version

Please ensure that the Python version is 3.7 or higher and pip uses this Python version.


Installing Python - Linux
---------------
On Linux systems, the Python installation process depends heavily on the distribution. 
If python3.7 (or higher) is not available for your distribution or your system requires 
multiple python versions to coexist, use pyenv:
https://realpython.com/intro-to-pyenv/ 

1. Install or update python3.7 with the packet manager of your distribution.
2. Install or update pip with the packet manager of your distribution.
3. To verify the installation, open a console and enter:

      python --version
      python -m pip --version


Installing the Vimba Python API
===============
All operating systems:

Open a terminal and navigate to the VimbaPython installation directory that
you have admin privileges/write permission for, 
for example, C:\Users\Public\Documents\Allied Vision\Vimba_5.x\VimbaPython_Source

Users who want to change the API's sources can find them in the Vimba examples 
directory, for example:
C:\Users\Public\Documents\Allied Vision\Vimba_5.x\VimbaPython_Source

Please note that Allied Vision can offer only limited support if an application 
uses a modified version of the API. 

Troubleshooting: If you don't have write permisson for the above-mentioned directories:

Download VimbaPython (in the correct version needed for your Vimba installation) from 
https://github.com/alliedvision/VimbaPython and install it from that directory.

Or you can downgrade pip to a version <2.3 with, for example:

python -m pip install --upgrade pip==21.1.2

After the VimbaPython installation is complete, you can upgrade pip again to the latest version.


Basic Installation
---------------
Execute the following command:

      python -m pip install .


Installation with optional NumPy and OpenCV export
---------------
Execute the following command:

      python -m pip install .[numpy-export,opencv-export]


Helper scripts for Linux
---------------
For Linux systems helper scripts named `Install.sh` and `Uninstall.sh` to install and uninstall
VimbaPython are provided. They will automatically detect if there is a currently active virtual
environment. To install or uninstall VimbaPython for one of the system wide Python installations,
admin rights are required (use `sudo`). To get further details on why the scripts do not offer your
desired Python installation or to troubleshoot problems, a debug flag is provided (for example
`./Install.sh -d`).

ARM users only: 
If installation of "opencv-export" fails, pip is not able to install
"opencv-python" for your ARM board. This is a known issue on ARM boards.
If you are affected by this, install VimbaPython without optional dependencies 
and try to install OpenCV in a different way (for example, with your operating system's packet manager). 
The OpenCV installation can be verified by running the example "Examples/asychronous_grab_opencv.py".
