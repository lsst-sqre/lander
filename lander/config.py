"""Configuration facilities.
"""
import sys
import os

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
        self._config['title'] = 'Title'
        self._config['abstract'] = 'Abstract'

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
