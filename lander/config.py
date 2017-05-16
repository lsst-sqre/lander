"""Configuration facilities.
"""
import json
import sys
import os
from collections import ChainMap

from metaget.tex.lsstdoc import LsstDoc
import structlog


class Configuration(object):
    """lander configuration container and validator.

    Parameters
    ----------
    args : `argparse.Namespace`
        An argument parser Namespace. This is made by the
        `argparse.ArgumentParser.parse_args` method.
    **config : keyword arguments
        Additional keyword arguments that override configurations from the
        ``args``.
    """

    def __init__(self, args=None, **config):
        super().__init__()
        self._logger = structlog.get_logger(__name__)

        # Make dict from argparse namespace
        self._args = {k: v for k, v in vars(args).items() if v}

        # Holds configuration overrides and computed configurations
        self._configs = dict(config)

        # Default configurations
        self._defaults = self._init_defaults()

        # Configurations are merged in a ChainMap. Priority is for computed
        # configurations. Then values fdirectly from command line arguments.
        # Then defaults.
        self._chain = ChainMap(self._configs, self._args, self._defaults)

        # Validate inputs
        if self['pdf_path'] is None:
            self._logger.error('--pdf argument must be set')
            sys.exit(1)
        if not os.path.exists(self['pdf_path']):
            self._logger.error('Cannot find PDF ' + self['pdf_path'])
            sys.exit(1)

        # Get metadata from the TeX source
        if self['lsstdoc_tex_path'] is not None:
            if not os.path.exists(self['lsstdoc_tex_path']):
                self._logger.error('Cannot find {0}'.format(
                    self['lsstdoc_tex_path']))
                sys.exit(1)
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

        # Get metadata from Travis environment
        if self['environment'] is not None:
            self['git_commit'] = os.getenv('TRAVIS_COMMIT')
            self['git_branch'] = os.getenv('TRAVIS_BRANCH')
            self['git_tag'] = os.getenv('TRAVIS_TAG')
            self['github_slug'] = os.getenv('TRAVIS_REPO_SLUG')
            self['travis_job_number'] = os.getenv('TRAVIS_JOB_NUMBER')

        # Apply metadata overrides

        if 'title' in self._args:
            self['title'] = self._args['title']

        if 'authors_json' in self._args:
            author_list = json.loads(self._args['authors_json'])
            self['authors'] = author_list

        if 'doc_handle' in self._args:
            self['doc_handle'] = self._args['doc_handle']
            self['series'] = self['doc_handle'].split('-', 1)[0]
            self['series_name'] = self._get_series_name(self['series'])

        if 'abstract' in self._args:
            self['abstract'] = self._args['abstract']

        if 'repo_url' in self._args:
            self['repo_url'] = self._args['rep_url']

        if 'git_branch' in self._args:
            self['git_branch'] = self._args['git_branch']

        if 'ltd_product' in self._args:
            self['ltd_product'] = self._args['ltd_product']

    def __getitem__(self, key):
        """Access configurations, first from the explicitly set configurations,
        and secondarily from the command line arguments.
        """
        return self._chain[key]

    def __setitem__(self, key, value):
        self._chain[key] = value

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

    def _init_defaults(self):
        """Create a `dict` of default configurations."""
        defaults = {
            'build_dir': None,
            'pdf_path': None,
            'environment': None,
            'lsstdoc_tex_path': None,
            'title': None,
            'authors': None,
            'authors_json': list(),
            'series': None,
            'series_name': None,
            'abstract': None,
            'ltd_product': None,
            'github_slug': None,
            'git_branch': None,
            'git_commit': None,
            'git_tag': None,
            'travis_job_number': None
        }
        return defaults
