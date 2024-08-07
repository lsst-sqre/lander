"""HTML landing page generator for LSST PDF documentation deployed from Git to
LSST the Docs.

https://github.com/lsst-sqre/lander
"""

__all__ = ["__version__"]

from importlib.metadata import PackageNotFoundError, version

__version__: str
"""The application version string of (PEP 440 / SemVer compatible)."""

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
