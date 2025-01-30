# VmbPy [![python version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Python API of the [Vimba X SDK](https://www.alliedvision.com)

Vimba X is a fully GenICam compliant SDK and the successor of Vimba. VmbPy is the Python API that is
provided by this SDK. It provides access to the full functionality of Vimba X in a pythonic way,
allowing for rapid development of applications.

# Installation

To use VmbPy, Python >= 3.7 is required. A ready-to-install packaged `.whl` file of VmbPy can be
found as part of the Vimba X installation, or be downloaded from our [github release
page](https://github.com/alliedvision/VmbPy/releases). The `.whl` can be installed as usual via the
[`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/) command.

> [!NOTE]  
> Depending on the some systems the command might instead be called `pip3`. Check your systems
> Python documentation for details.

## Selecting the correct `.whl`

When selecting the correct `.whl` file for your project, you have two options. The recommended
approach is to use the `.whl` that includes the VmbC libs, as this provides all the required
libraries to get started with development right away. Note, however, that this `.whl` does not
include any Transport Layers or device drivers, which must be installed separately (for example, by
installing Vimba X). You can identify `.whl`s with included libs by the platform tag that is
included in their filename (for example, `win_amd64`).

Alternatively, you can use the `.whl` without the included VmbC libs (platform tag `any`), but this
requires a pre-existing Vimba X installation on your system, as VmbPy will attempt to load the
necessary libraries at import time.

> [!NOTE]  
> If a `.whl` with included VmbC libs is used, it is possible that binary dependencies of VmbC need
> to be installed separately. For example on windows the Visual C++ Redistributable is required.
> These dependencies will be automatically installed if Vimba X is installed on the system.

## Optional dependencies

For some functionality of VmbPy optional dependencies (also called "extras") are required. These
provide for example integration into numpy and OpenCV, as well as some additional code analysis
tools that are used in our full test suite. The following extras are defined for VmbPy:

- numpy: Enables conversion of `VmbPy.Frame` objects to numpy arrays
- opencv: Similar to above but ensures that the numpy arrays are valid OpenCV images
- test: Additional tools such as `flake8`, `mypy`, and `coverage` only necessary for executing
  `run_tests.py`

> [!NOTE]  
> Installing these extra dependencies is possible by defining them as part of the installation
> command like so (note the single quotes around the filename and extras):
> ```
> pip install '/path/to/vmbpy-X.Y.Z-py-none-any.whl[numpy,opencv]'
> ```

### Yocto on NXP i.MX8 and OpenCV

The GPU in i.MX8 systems requires using the system-wide opencv-python package. When you create the
Python environment, please use the `--system-site-packages` flag to include the system-wide OpenCV
package.

If you don't set up a separate environment, a warning is shown during the VmbPy installation. You
can ignore this warning.

# Differences to VimbaPython

VmbPy is the successor of VimbaPython. As such it shares many similarities, but in some places major
differences exist. An overview of the differences between VimbaPython and VmbPy can be found in the
migration guide, that is part of the Vimba X SDK documentation.

# Usage

Below is a minimal example demonstrating how to print all available cameras detected by VmbPy. It
highlights the general usage of VmbPy. More complete code examples can be found in the `Examples`
directory.

```python
import vmbpy

vmb = vmbpy.VmbSystem.get_instance()
with vmb:
    cams = vmb.get_all_cameras()
    for cam in cams:
        print(cam)
```

## General guidelines

VmbPy makes use of the Python context manager to perform setup and teardown tasks for the used
object instances. This ensures the correct call order for the underlying VmbC functions and
guarantees, that resources are made available and freed as expected even in cases where errors
occur. One example is shown in the example above, where the context of the `VmbSystem` object must
be entered to start the underlying VmbC API.

VmbPy is also designed to closely resemble VmbCPP. While VmbPy aims to be as performant as possible,
it might not be fast enough for performance critical applications. In that case the similar
structure of VmbPy and VmbCPP makes it easy to migrate an existing VmbPy code base to VmbCPP.

## Configuration of the underlying VmbC API

The underlying VmbC API used by VmbPy can be configured in various ways to suit your development
needs. Multiple configuration options are available, including the ability to enable logging of VmbC
calls and customize the loading behavior of transport layers. Configuration is achieved through the
`VmbC.xml` file, which by default loads Transport Layers from the `GENICAM_GENTL64_PATH` environment
variable. The location of this configuration file depends on the type of `.whl` installed: if you're
using the `.whl` with included libs, it can be found in `/site-packages/vmbpy/c_binding/lib`. If
you're using the `.whl` without included libs, it is located in the `/api/bin` directory of your
Vimba X installation.

Alternatively it is also possible for the user to provide a `VmbC.xml` configuration with the help
of `VmbSystem.set_path_configuration`.

## Running the test suite

VmbPy provides a number of unittest as part of the [Github
repository](https://github.com/alliedvision/VmbPy). The test suite can be run in two ways. Either by
using the test discovery mechanic of Python's `unittest` module, or via the provided `run_tests.py`.

### Unittest discovery

Python's unittest module can be used to discover the test cases of VimbaPython automatically. This
can be useful as it provides good integration into third party tools like test explorers. To execute
the entire test suite the following command can be run inside the `Tests` directory of this
repository:

```
python -m unittest discover -v -p *_test.py
```

This will open the first camera, that Vimba detects on the system. If multiple cameras are connected
to the system, an unexpected device may be selected. In this situation it is recommended to specify
the ID of the device that should be used for test case execution. This is done by setting the
environment variable `VMBPY_DEVICE_ID`. A convenient way to get the IDs of currently available
devices is running the `list_cameras.py` example.

Execute entire test suite using camera with ID `DEV_PLACEHOLDER`

<details><summary>Windows</summary>

```
set VMBPY_DEVICE_ID=DEV_PLACEHOLDER
python -m unittest discover -v -p *_test.py
```
</details>

<details><summary>Linux</summary>

```
export VMBPY_DEVICE_ID=DEV_PLACEHOLDER
python -m unittest discover -v -p *_test.py
```
</details>

### `run_tests.py`

The provided helper script `run_tests.py` may also be used to execute the test suite. In addition to
the test cases, it also executes `flake8`, `mypy`, and `coverage`. These additional tools need to be
installed in the used Python environment. For convenience they are grouped as an optional dependency
of VmbPy with the name `test` that can be added to the `pip install` command used to install VmbPy.

`run_tests.py` provides a helpful command line interface that can be used to configure which tests
to run and how the output should be structured. To get an overview of the available options the
following command can be executed to generate the usage description.

```
python run_tests.py -h
```

# Beta Disclaimer

Please be aware that all code revisions not explicitly listed in the Github Release section are
considered a **Beta Version**.

For Beta Versions, the following applies in addition to the BSD 2-Clause License:

THE SOFTWARE IS PRELIMINARY AND STILL IN TESTING AND VERIFICATION PHASE AND IS PROVIDED ON AN “AS
IS” AND “AS AVAILABLE” BASIS AND IS BELIEVED TO CONTAIN DEFECTS. THE PRIMARY PURPOSE OF THIS EARLY
ACCESS IS TO OBTAIN FEEDBACK ON PERFORMANCE AND THE IDENTIFICATION OF DEFECTS IN THE SOFTWARE,
HARDWARE AND DOCUMENTATION.
