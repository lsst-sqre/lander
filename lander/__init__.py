"""HTML landing page generator for LSST PDF documentation deployed from Git to
LSST the Docs.

https://github.com/lsst-sqre/lander
"""
import pkg_resources


__version__ = pkg_resources.get_distribution('lander').version
