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

1. Install Python: https://www.python.org/downloads/windows/
2. Ensure that the latest pip version is installed.
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

Open a terminal and navigate to the VimbaPython installation directory, 
for example, C:\Program Files\Allied Vision\Vimba_x.x\VimbaPython.

Users who want to change the API's sources can find them in the Vimba examples 
directory, for example:
C:\Users\Public\Documents\Allied Vision\Vimba_x.x\VimbaPython_Source

Please note that Allied Vision can offer only limited support if an application 
uses a modified version of the API. 


Basic Installation
---------------
Execute the following command:

      python -m pip install .


Installation with optional NumPy and OpenCV export
---------------
Execute the following command:

      python -m pip install .[numpy-export,opencv-export]

ARM users only: 
If installation of "opencv-export" fails, pip is not able to install
"opencv-python" for your ARM board. This is a known issue on ARM boards.
If you are affected by this, install VimbaPython without optional dependencies 
and try to install OpenCV in a different way (for example, with your operating system's packet manager). 
The OpenCV installation can be verified by running the example "Examples/asychronous_grab_opencv.py".
