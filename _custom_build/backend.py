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


def copy_files(file_paths, target_dir):
    """
    Copy all files in `file_paths` to `target_dir` removing any common prefix shared among all files
    in `file_paths`

    Returns a list of `Path`s to the files that were copied.
    """
    # Find the common path prefix and ensure it ends with a path separator
    common_path = os.path.commonpath(file_paths)
    if os.path.isdir(common_path):
        common_path = os.path.join(common_path, '')

    copied_files = []
    for file_path in file_paths:
        # Remove the common prefix
        relative_path = os.path.relpath(file_path, common_path)

        # Construct the new file destination
        target_path = os.path.join(target_dir, relative_path)

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # Copy the file
        copied_files.append(Path(shutil.copy2(file_path, target_path)))
    return copied_files


def delete_files(file_paths):
    """
    Delete all files in `file_paths`

    If a path given in `file_paths` points to a directory, that directory is removed.
    """
    for file_path in file_paths:
        os.remove(file_path)

    # Remove now-empty directories (if any)
    for file_path in file_paths:
        dir_path = os.path.dirname(file_path)
        remove_empty_dirs(dir_path)


def remove_empty_dirs(directory):
    while True:
        try:
            if not os.listdir(directory):  # Check if the directory is empty
                os.rmdir(directory)
                # Move to the parent directory
                directory = os.path.dirname(directory)
            else:
                break
        except FileNotFoundError:
            break
        except OSError:
            break


@contextmanager
def add_vimba_x_libs(search_dir: Path, target_dir: Path):
    """
    Context manager that adds the compiled shared libraries from Vimba X that VmbPy requires to the
    given `target_dir` while the context is active. When the context is left, all files that were
    copied into `target_dir` are removed again. If `target_dir` does not exist it will be created
    """
    # TODO: update documentation to inform user about how to change XML config and what the default xml config is and how it might differ to that installed on Windows machines
    regex = r'.*(VmbC|VmbImageTransform|_AVT)(.dll|.so|.xml|.dylib)?$'
    to_copy = map(Path, filter(re.compile(regex).match, map(str, search_dir.glob('**/*'))))
    files_to_copy = [f for f in to_copy if f.is_file()]
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    files_to_delete = copy_files(files_to_copy, target_dir)
    yield
    delete_files(files_to_delete)


def build_sdist(sdist_directory, config_settings=None):
    if config_settings is None:
        config_settings = {}
    search_dir = config_settings.get('--vmb-dir')
    if search_dir is not None:
        search_dir = Path(search_dir)
        with add_vimba_x_libs(search_dir, Path(__file__).parent / "../vmbpy/c_binding/lib"):
            result = _orig.build_sdist(sdist_directory, config_settings)
    else:
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
    search_dir = config_settings.get('--vmb-dir', None)
    if plat_name_value is None:
        if search_dir is not None:
            raise ValueError(f'This build will contain platform specific binaries found in provided '
                            f'vmb-dir: {search_dir}. This means a platform-tag must also be '
                            f'specified via --plat-name=<some-tag>')
        else:
            plat_name_value = 'any'
    config_settings['--build-option'] = f'{plat_name_arg}={plat_name_value}'
    # if the user directly calls pip install, it will not build an sdist first. This means that even
    # during wheel build we should make sure the lb directory contains the needed files
    if search_dir is not None:
        search_dir = Path(search_dir)
        with add_vimba_x_libs(search_dir, Path(__file__).parent / "../vmbpy/c_binding/lib"):
            result = _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
    else:
        result = _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
    return result
