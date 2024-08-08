from contextlib import contextmanager
from pathlib import Path
from setuptools import build_meta as _orig
from setuptools.build_meta import *
from typing import Optional

import os
import re
import shutil
import sysconfig


def find_vimba_x_home() -> Path:
    """
    returns a `Path` instance to the Vimba X Home directory or raises an error if no Vimba X Home
    directory could be found
    """
    # First choice is always VIMBA_X_HOME environment variable
    vimba_x_home = os.getenv('VIMBA_X_HOME')
    if vimba_x_home is not None:
        return Path(vimba_x_home)
    # TODO: Try to find it from GENICAM_GENTL64_PATH
    raise FileNotFoundError('Could not find a Vimba X installation to get shared libraries from. '
                            'Install Vimba X or manually set a search path by adding the argument '
                            '`--config-setting=--vmb-dir=/path/to/vimbax/binary/directory`')


@contextmanager
def add_vimba_x_libs(search_dir: Optional[Path], target_dir: Path):
    """
    Context manager that adds the compiled shared libraries from Vimba X that VmbPy requires to the
    given `target_dir` while the context is active. When the context is left, all files that were
    copied into `target_dir` are removed again. If `target_dir` does not exist it will be created
    """
    if search_dir is None:
        search_dir = find_vimba_x_home() / 'api/bin'
    # TODO: update documentation to inform user about how to change XML config and what the default xml config is and how it might differ to that installed on Windows machines
    # TODO: Fix regex (and probably logic) to pick up genicam libs in genicam subdir on linux systems
    regex = r'.*(VmbC|VmbImageTransform|_AVT)\.(dll|so|xml)'
    files_to_copy = map(Path, filter(re.compile(regex).match, map(str, search_dir.iterdir())))
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    files_to_delete = []
    for f in files_to_copy:
        files_to_delete.append(Path(shutil.copy(f, target_dir)))
    yield
    for f in files_to_delete:
        if f.is_file():
            f.unlink()
        else:
            shutil.rmtree(f)


def build_sdist(sdist_directory, config_settings=None):
    if config_settings is None:
        config_settings = {}
    search_dir = config_settings.get('--vmb-dir')
    if search_dir is not None:
        search_dir = Path(search_dir)
    with add_vimba_x_libs(search_dir, Path(__file__).parent / "../vmbpy/c_binding/lib"):
        result = _orig.build_sdist(sdist_directory, config_settings)
    return result


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    if config_settings is None:
        config_settings = {}
    # Make sure that the plat-name option is passed down to setuptools correctly so it is added to
    # the whl filename. Needed because setuptools does not properly pass `config_settings` through:
    # https://github.com/pypa/setuptools/issues/2491
    plat_name_arg = '--plat-name'
    plat_name_value = config_settings.get(plat_name_arg, None)
    if plat_name_value is None:
        plat_name_value = sysconfig.get_platform()
    config_settings['--build-option'] = f'{plat_name_arg}={plat_name_value}'
    # if the user directly calls pip install, it will not build an sdist first. This means that even
    # during wheel build we should make sure the lb directory contains the needed files
    search_dir = config_settings.get('--vmb-dir', None)
    if search_dir is not None:
        search_dir = Path(search_dir)
    with add_vimba_x_libs(search_dir, Path(__file__).parent / "../vmbpy/c_binding/lib"):
        result = _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
    return result
