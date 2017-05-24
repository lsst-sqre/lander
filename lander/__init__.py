"""HTML landing page generator for LSST PDF documentation deployed from Git to
LSST the Docs.

https://github.com/lsst-sqre/lander
"""
from ._version import get_versions


# Get version string from versioneer
# https://github.com/warner/python-versioneer
__version__ = get_versions()['version']
del get_versions
