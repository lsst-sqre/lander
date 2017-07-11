"""Tests for the lander.config module."""

import pytest

from lander.config import Configuration
from lander.exceptions import DocuShareError


def test_get_docushare_url():
    url = Configuration._get_docushare_url('LDM-151')
    assert url == 'https://ls.st/ldm-151*'


def test_get_docushare_url_bad_handle():
    with pytest.raises(DocuShareError):
        Configuration._get_docushare_url('FOOBAR-1')


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
    'git_branch, expected',
    [('u/jonathansick/test', True),
     ('master', False),
     ('docushare-v1', False),
     ('docushare-v10', False),
     ('docushare-v10-test', True)])
def test_determine_draft_status(git_branch, expected):
    assert Configuration._determine_draft_status(git_branch) is expected


@pytest.mark.parametrize(
    'git_branch, expected',
    [('u/jonathansick/test', True),
     ('master', False),
     ('docushare-v1', False),
     ('docushare-v10', False),
     ('docushare-v10-test', True)])
def test_draft_status(git_branch, expected):
    """Integrated testing of is_draft_branch computation."""
    config = Configuration(git_branch=git_branch, _validate_pdf=False)
    assert config['is_draft_branch'] is expected
