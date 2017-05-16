"""Configuration facilities.
"""
import sys
import os

from metaget.tex.lsstdoc import LsstDoc
import structlog


class Configuration(object):
    """lander configuration container and validator.
    """

    def __init__(self, args=None, **config):
        super().__init__()
        self._logger = structlog.get_logger(__name__)
        self._args = args
        self._config = dict(config)

        # Validate configuration
        if self['pdf_path'] is None:
            self._logger.error('--pdf argument must be set')
            sys.exit(1)

        if not os.path.exists(self['pdf_path']):
            self._logger.error('Cannot find PDF ' + self['pdf_path'])
            sys.exit(1)

        if self['lsstdoc_tex_path'] is not None:
            # get metadata from the document
            with open(self['lsstdoc_tex_path']) as f:
                tex_source = f.read()
                lsstdoc = LsstDoc(tex_source)
                self['title'] = lsstdoc.title
                if lsstdoc.abstract is not None:
                    self['abstract'] = lsstdoc.abstract
                if lsstdoc.handle is not None:
                    self['doc_handle'] = lsstdoc.handle
                    self['series'] = lsstdoc.series
                    self['series_name'] = self._get_series_name(self['series'])
        else:
            # Fallback for template
            self['title'] = None
            self['doc_handle'] = None
            self['series'] = None
            self['series_name'] = None
            self['abstract'] = None

    def __getitem__(self, key):
        """Access configurations, first from the explicitly set configurations,
        and secondarily from the command line arguments.
        """
        try:
            return self._config[key]
        except KeyError:
            return getattr(self._args, key)

    def __setitem__(self, key, value):
        self._config[key] = value

    def _get_series_name(self, series):
        series_names = {
            'sqr': 'SQuaRE Technical Note',
            'dmtn': 'Data Management Technical Note',
            'smtn': 'Simulations Technical Note',
            'ldm': 'LSST Data Management',
            'lse': 'LSST Systems Engineering',
            'lpm': 'LSST Project Management',
        }
        return series_names.get(series.lower(), '')
