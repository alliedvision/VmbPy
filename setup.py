"""VimbaPython setup script

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""

import setuptools
import vimba

name = 'VimbaPython'
version = vimba.__version__
author = 'Allied Vision Technologies GmbH'
description = 'Python Bindings for Allied Visions VimbaSDK'
long_description = 'TODO: Maybe read from a README.md'
license = 'TODO'
packages = [
    'vimba',
    'vimba.c_binding',
    'vimba.util'
]
python_requires = '>=3.7'
tests_require = [
    'xmlrunner',
    'flake8',
    'flake8-junit-report',
    'mypy',
    'coverage'
]
extras_require = {
    'numpy-export': ['numpy'],
    'opencv-export': ['opencv-python'],
    'test': tests_require
}

setuptools.setup(
    name=name,
    version=version,
    author=author,
    description=description,
    long_description=long_description,
    license=license,
    packages=packages,
    python_requires=python_requires,
    extras_require=extras_require
)

