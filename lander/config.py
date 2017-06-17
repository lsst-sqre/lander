"""Configuration facilities.
"""
import json
import sys
import os
from collections import ChainMap
import re
import datetime

from metasrc.tex.lsstdoc import LsstDoc
from metasrc.tex import texnormalizer
import structlog
import dateutil


# Detects a GitHub repo slug from a GitHub URL
GITHUB_SLUG_PATTERN = re.compile(
    r"https://github.com"
    r"/(?P<org>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
    r"/(?P<name>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
)


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

        # Configurations from environment variables
        self._envvars = self._get_environment_variables()

        # Configurations are merged in a ChainMap. Priority is
        # 1. Computed configurations.
        # 2. Command line variables.
        # 3. Environment variables.
        # 4. Defaults.
        self._chain = ChainMap(self._configs, self._args,
                               self._envvars, self._defaults)

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

            # Apply source normalization pipeline
            tex_source = texnormalizer.remove_comments(tex_source)
            tex_source = texnormalizer.remove_trailing_whitespace(tex_source)

            # Extract metadata from the LsstDoc document
            lsstdoc = LsstDoc(tex_source)
            self['title'] = lsstdoc.title
            if lsstdoc.abstract is not None:
                self['abstract'] = lsstdoc.abstract
            if lsstdoc.handle is not None:
                self['doc_handle'] = lsstdoc.handle
                self['series'] = lsstdoc.series
                self['series_name'] = self._get_series_name(self['series'])
            if lsstdoc.authors is not None:
                self['authors'] = lsstdoc.authors

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
            self['repo_url'] = self._args['repo_url']

            # extract github repo slug from repo_url
            match = GITHUB_SLUG_PATTERN.match(self['repo_url'])
            if match:
                self['github_slug'] = '/'.join((
                    match.group('org'),
                    match.group('name')))

        if 'extra_downloads' in self._args:
            self['extra_downloads'] = self._args['extra_downloads']

        if 'git_branch' in self._args:
            self['git_branch'] = self._args['git_branch']

        if 'build_datetime' in self._args:
            parsed_datetime = dateutil.parser.parse(
                self._args['build_datetime'])
            if parsed_datetime.tzinfo is None:
                parsed_datetime = parsed_datetime.replace(
                    tzinfo=dateutil.tz.tzutc())
            self['build_datetime'] = parsed_datetime

        # Post configuration validation
        if self['upload']:
            if self['ltd_product'] is None:
                message = '--ltd-product must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['aws_id'] is None:
                message = '--aws-id must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['aws_secret'] is None:
                message = '--aws-secret must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['keeper_url'] is None:
                message = '--keeper-url must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['keeper_user'] is None:
                message = '--keeper-user must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['keeper_password'] is None:
                message = '--keeper-password must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

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
            'build_datetime': datetime.datetime.now(dateutil.tz.tzutc()),
            'pdf_path': None,
            'extra_downloads': list(),
            'environment': None,
            'lsstdoc_tex_path': None,
            'title': None,
            'authors': None,
            'authors_json': list(),
            'series': None,
            'series_name': None,
            'abstract': None,
            'ltd_product': None,
            'docushare_url': None,
            'github_slug': None,
            'git_branch': 'master',  # so we default to the main LTD edition
            'git_commit': None,
            'git_tag': None,
            'travis_job_number': None,
            'aws_id': None,
            'aws_secret': None,
            'keeper_url': 'https://keeper.lsst.codes',
            'keeper_user': None,
            'keeper_password': None,
            'upload': False
        }
        return defaults

    def _get_environment_variables(self):
        var_keys = {
            'aws_id': 'LTD_AWS_ID',
            'aws_secret': 'LTD_AWS_SECRET',
            'keeper_url': 'LTD_KEEPER_URL',
            'keeper_user': 'LTD_KEEPER_USER',
            'keeper_password': 'LTD_KEEPER_PASSWORD',
        }
        env_configs = {}
        for config_key, var_name in var_keys.items():
            env_value = os.getenv(var_name)
            if env_value is not None:
                env_configs[config_key] = env_value
        return env_configs
