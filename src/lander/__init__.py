"""HTML landing page generator for LSST PDF documentation deployed from Git to
LSST the Docs.

https://github.com/lsst-sqre/lander
"""
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution("lander").version
except DistributionNotFound:
    # package is not installed
    pass
