"""Tests for the lander.config module."""

import pytest

from lsstprojectmeta.tex.lsstdoc import LsstLatexDoc

from lander.config import Configuration
from lander.exceptions import DocuShareError


@pytest.mark.skip(reason='Fails because ls.st+DocuShare is broken (2017-09-07')
def test_get_docushare_url():
    url = Configuration._get_docushare_url('LDM-151')
    assert url == 'https://ls.st/ldm-151*'


def test_get_docushare_url_bad_handle():
    with pytest.raises(DocuShareError):
        Configuration._get_docushare_url('FOOBAR-1')


@pytest.mark.skip(reason='Fails because ls.st+DocuShare is broken (2017-09-07')
@pytest.mark.parametrize(
    'doc_handle, expected_url',
    [('LDM-151', 'https://ls.st/ldm-151*'),
     ('FOOBAR-1', None)])
def test_docushare_url_config(doc_handle, expected_url):
    """Integrated testing of doc_handle computation."""
    config = Configuration(doc_handle=doc_handle, _validate_pdf=False)
    if expected_url is None:
        assert config['docushare_url'] is None
    else:
        assert config['docushare_url'] == expected_url


@pytest.mark.parametrize(
    'git_branch, docclass, expected',
    [('u/jonathansick/test', r'\documentclass[DM]{lsstdoc}', False),
     ('u/jonathansick/test', r'\documentclass[DM,lsstdraft]{lsstdoc}', True),
     ('master', r'\documentclass[DM]{lsstdoc}', False),
     # master is always considered released
     ('master', r'\documentclass[DM,lsstdraft]{lsstdoc}', False),
     ('docushare-v1', r'\documentclass[DM]{lsstdoc}', False),
     ('docushare-v1', r'\documentclass[DM,lsstdraft]{lsstdoc}', True)])
def test_determine_draft_status(git_branch, docclass, expected):
    lsstdoc = LsstLatexDoc(docclass)
    is_draft = Configuration._determine_draft_status(git_branch,
                                                     lsstdoc=lsstdoc)
    assert is_draft == expected


@pytest.mark.parametrize(
    'git_branch, expected',
    [('u/jonathansick/test', True),
     ('master', False),
     ('docushare-v1', True),
     ('docushare-v10', True),
     ('docushare-v10-test', True)])
def test_draft_status(git_branch, expected):
    """Integrated testing of is_draft_branch computation. LsstLatexDoc metadata
    is not available here, only branch information is used.
    """
    config = Configuration(git_branch=git_branch, _validate_pdf=False)
    assert config['is_draft_branch'] is expected
