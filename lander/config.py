"""Configuration facilities.
"""
import sys
import os
import re

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

        # Defaults for testing
        self['title'] = 'Title'
        self['abstract'] = 'Abstract'
        self['doc_handle'] = 'LDM-000'

        self['series'] = self._get_series(self['doc_handle'])
        self['series_name'] = self._get_series_name(self['series'])

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

    def _get_series(self, doc_handle):
        pattern = re.compile('^(sqr|dmtn|smtn|ldm|lse|lpm)-[0-9]+$')
        print(doc_handle)
        match = pattern.search(doc_handle.lower())
        return match.group(1).upper()

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
