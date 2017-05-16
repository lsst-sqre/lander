"""Configuration facilities.
"""
import json
import sys
import os

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
        self._args = args
        self._configs = dict(config)

        # Validate configuration
        if self['pdf_path'] is None:
            self._logger.error('--pdf argument must be set')
            sys.exit(1)

        if not os.path.exists(self['pdf_path']):
            self._logger.error('Cannot find PDF ' + self['pdf_path'])
            sys.exit(1)

        # get metadata from the TeX source
        if self['lsstdoc_tex_path'] is not None:
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

        # Apply metadata overrides

        if self._args.title is not None:
            self['title'] = self._args.title

        if self._args.authors_json is not None:
            author_list = json.loads(self._args.authors)
            self['authors'] = author_list

        if self._args.doc_handle is not None:
            self['doc_handle'] = self._args.doc_handle
            self['series'] = self['doc_handle'].split('-', 1)[0]
            self['series_name'] = self._get_series_name(self['series'])

        if self._args.abstract is not None:
            self['abstract'] = self._args.abstract

        if self._args.repo_url is not None:
            self['repo_url'] = self._args.rep_url

        if self._args.repo_branch is not None:
            self['repo_branch'] = self._args.repo_branch

        if self._args.ltd_product is not None:
            self['ltd_product'] = self._args.ltd_product

    def __getitem__(self, key):
        """Access configurations, first from the explicitly set configurations,
        and secondarily from the command line arguments.
        """
        try:
            return self._configs[key]
        except KeyError:
            return getattr(self._args, key)

    def __setitem__(self, key, value):
        self._configs[key] = value

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
