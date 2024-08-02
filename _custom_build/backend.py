from setuptools import build_meta as _orig
from setuptools.build_meta import *


# Probably not needed to change logic of build_wheel. build_sdist should handle inclusion of
# libraries and wheel just packages them anyway
# def get_requires_for_build_wheel(config_settings=None):
#     print("build_wheel")
#     return _orig.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(config_settings=None):
    print("TODO: add logic to copy dll/so files to appropriate place")
    print(config_settings)
    # => {'--build-option': '--plat-name=win_amd64'}
    # Get build option value, split at = sign and have platform dependent logic called from there
    return _orig.get_requires_for_build_sdist(config_settings)