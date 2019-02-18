"""Configuration facilities.
"""
import json
import sys
import os
from collections import ChainMap
import re
import datetime
import urllib.parse

from lsstprojectmeta.tex.lsstdoc import LsstLatexDoc
import structlog
import dateutil
import requests

from .exceptions import DocuShareError


# Detects a GitHub repo slug from a GitHub URL
GITHUB_SLUG_PATTERN = re.compile(
    r"https://github.com"
    r"/(?P<org>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
    r"/(?P<name>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
)


# Regular expression that matches docushare release tags
# E.g. docushare-v1
DOCUSHARE_TAG_PATTERN = re.compile(
    r"^docushare-v(?P<number>\d+$)"
)


class Configuration(object):
    """lander configuration container and validator.

    Parameters
    ----------
    args : `argparse.Namespace`
        An argument parser Namespace. This is made by the
        `argparse.ArgumentParser.parse_args` method.
    _validate_pdf : `bool`, optional
        Validate that the PDF exists. Default is `True`.
    **config : keyword arguments
        Additional keyword arguments that override configurations from the
        ``args``.
    """

    def __init__(self, args=None, _validate_pdf=True, **config):
        super().__init__()
        self._logger = structlog.get_logger(__name__)

        # Make dict from argparse namespace
        if args is not None:
            self._args = {k: v for k, v in vars(args).items() if v}
        else:
            self._args = {}

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
        if _validate_pdf:
            self._validate_pdf_file()

        # Get metadata from the TeX source
        self.lsstdoc = None
        if self['lsstdoc_tex_path'] is not None:
            if not os.path.exists(self['lsstdoc_tex_path']):
                self._logger.error('Cannot find {0}'.format(
                    self['lsstdoc_tex_path']))
                sys.exit(1)

            # Extract metadata from the LsstLatexDoc document
            self.lsstdoc = LsstLatexDoc.read(self['lsstdoc_tex_path'])
            self['title'] = self.lsstdoc.title
            self['title_html'] = self.lsstdoc.html_title
            self['title_plain'] = self.lsstdoc.plain_title
            self['build_datetime'] = self.lsstdoc.revision_datetime
            if self.lsstdoc.abstract is not None:
                self['abstract'] = self.lsstdoc.abstract
                self['abstract_html'] = self.lsstdoc.html_abstract
                self['abstract_plain'] = self.lsstdoc.plain_abstract
            if self.lsstdoc.handle is not None:
                self['doc_handle'] = self.lsstdoc.handle
                self['series'] = self.lsstdoc.series
                self['series_name'] = self._get_series_name(self['series'])
            if self.lsstdoc.authors is not None:
                self['authors'] = self.lsstdoc.authors
                self['authors_html'] = self.lsstdoc.html_authors
                self['authors_plain'] = self.lsstdoc.plain_authors

        # Get metadata from Travis environment
        if self['environment'] is not None:
            self['git_commit'] = os.getenv('TRAVIS_COMMIT')
            self['git_branch'] = os.getenv('TRAVIS_BRANCH')
            self['git_tag'] = os.getenv('TRAVIS_TAG')
            self['github_slug'] = os.getenv('TRAVIS_REPO_SLUG')
            self['travis_job_number'] = os.getenv('TRAVIS_JOB_NUMBER')
            self['travis_build_web_url'] = os.getenv('TRAVIS_BUILD_WEB_URL')
            if os.getenv('TRAVIS_PULL_REQUEST').lower() == 'false':
                self['is_travis_pull_request'] = False
            else:
                self['is_travis_pull_request'] = True

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

        # Get the DocuShare URL if not set already
        if self['doc_handle'] is not None and self['docushare_url'] is None:
            try:
                self['docushare_url'] = self._get_docushare_url(
                    self['doc_handle'], validate=True)
            except DocuShareError as e:
                message = 'Could not compute DocuShare URL for {0}'.format(
                    self['doc_handle'])
                self._logger.warning(message)
                self._logger.warning(str(e))

        self['is_draft_branch'] = self._determine_draft_status(
            self['git_branch'],
            lsstdoc=self.lsstdoc)

        # Post configuration validation
        if self['upload']:
            if self['ltd_product'] is None:
                message = '--ltd-product must be set for uploads'
                self._logger.error(message)
                sys.exit(1)

            if self['environment'] == 'travis' and self['aws_secret'] is None:
                self._logger.info('Skipping build from fork or PR.')
                sys.exit(0)

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

    def _validate_pdf_file(self):
        """Validate that the pdf_path configuration is set and the referenced
        file exists.

        Exits the program with status 1 if validation fails.
        """
        if self['pdf_path'] is None:
            self._logger.error('--pdf argument must be set')
            sys.exit(1)
        if not os.path.exists(self['pdf_path']):
            self._logger.error('Cannot find PDF ' + self['pdf_path'])
            sys.exit(1)

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

    @staticmethod
    def _get_docushare_url(handle, validate=True):
        """Get a docushare URL given document's handle.

        Parameters
        ----------
        handle : `str`
            Handle name, such as ``'LDM-151'``.
        validate : `bool`, optional
            Set to `True` to request that the link resolves by performing
            a HEAD request over the network. `False` disables this testing.
            Default is `True`.

        Returns
        -------
        docushare_url : `str`
            Shortened DocuShare URL for the document corresponding to the
            handle.

        Raises
        ------
        lander.exceptions.DocuShareError
            Raised for any error related to validating the DocuShare URL.
        """
        logger = structlog.get_logger(__name__)
        logger.debug('Using Configuration._get_docushare_url')

        # Make a short link to the DocuShare version page since
        # a) It doesn't immediately trigger a PDF download,
        # b) It gives the user extra information about the document before
        #    downloading it.
        url = 'https://ls.st/{handle}*'.format(handle=handle.lower())

        if validate:
            # Test that the short link successfully resolves to DocuShare
            logger.debug('Validating {0}'.format(url))
            try:
                response = requests.head(url, allow_redirects=True, timeout=30)
            except requests.exceptions.RequestException as e:
                raise DocuShareError(str(e))

            error_message = 'URL {0} does not resolve to DocuShare'.format(url)
            if response.status_code != 200:
                logger.warning('HEAD {0} status: {1:d}'.format(
                    url, response.status_code))
                raise DocuShareError(error_message)
            redirect_url_parts = urllib.parse.urlsplit(response.url)
            if redirect_url_parts.netloc != 'docushare.lsst.org':
                logger.warning('{0} resolved to {1}'.format(url, response.url))
                raise DocuShareError(error_message)

        return url

    @staticmethod
    def _determine_draft_status(git_branch, lsstdoc=None):
        """Determine if the document build is considered a draft based on
        DM's policies given the Git branch or draft status in the lsstdoc-class
        LaTeX document.

        Parameters
        ----------
        git_branch : `str`
            Git branch or tag name.
        lsstdoc : `lsstprojectmeta.tex.lsstdoc.LsstLatexDoc`
            `~lsstprojectmeta.tex.lsstdoc.LsstLatexDoc` instance where, if the
            ``is_draft`` argument is `True`, the draft status is True.

        Returns
        -------
        is_draft : `bool`
            Returns `True` if the build is a draft, and `False` if it is
            not a draft.

        Notes
        -----
        The document **is not** considered a draft if:

        - Branch is ``master``
        - If ``lsstdoc`` is provided and ``lsstdoc.is_draft == False``,
          meaning that the ``lsstdoc`` option is not included in the document's
          class options.
        """
        if git_branch == 'master':
            return False

        if lsstdoc is not None:
            return lsstdoc.is_draft

        return True

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
            'title_plain': "",
            'authors': None,
            'authors_json': list(),
            'doc_handle': None,
            'series': None,
            'series_name': None,
            'abstract': None,
            'abstract_plain': "",
            'ltd_product': None,
            'docushare_url': None,
            'github_slug': None,
            'git_branch': 'master',  # so we default to the main LTD edition
            'git_commit': None,
            'git_tag': None,
            'travis_job_number': None,
            'is_travis_pull_request': False,  # If not on Travis, not a PR
            'is_draft_branch': True,
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
