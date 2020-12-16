"""Tests for the lander.ext.parser.datamodel module."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from lander.ext.parser._datamodel import (
    FormattedString,
    Orcid,
    Ror,
    collapse_whitespace,
)


def test_formattedstring_sanitize_html() -> None:
    html_input = '<h1>Hello <a href="https://example.com">world</a></h1>'
    plain_input = "Hello world"

    fs = FormattedString(html=html_input, plain=plain_input)

    assert fs.plain == plain_input
    # The H1 tag should be stripped, but the link is ok.
    assert fs.html == 'Hello <a href="https://example.com">world</a>'


def test_formattedstring_from_latex() -> None:
    fs = FormattedString.from_latex(r"Hello \emph{world}", fragment=True)
    assert fs.html == "Hello <em>world</em>"
    assert fs.plain == "Hello world"


def test_formattedstring_from_latex_paragraph() -> None:
    fs = FormattedString.from_latex(r"Hello \emph{world}", fragment=False)
    assert fs.html == "<p>Hello <em>world</em></p>"
    assert fs.plain == "Hello world"
    assert fs.latex == r"Hello \emph{world}"


@pytest.mark.parametrize(
    "text,expected",
    [
        (" Jonathan   Sick ", "Jonathan Sick"),
        ("Jonathan\nSick", "Jonathan Sick"),
    ],
)
def test_collapse_whitespace(text: str, expected: str) -> None:
    assert collapse_whitespace(text) == expected


@pytest.mark.parametrize(
    "identifier,sample",
    [
        ("0000-0002-1825-0097", "0000-0002-1825-0097"),
        ("0000-0001-5109-3700", "hello 0000-0001-5109-3700 world"),
        ("0000-0002-1694-233X", "0000-0002-1694-233X"),
        ("0000-0002-1825-0097", "https://orcid.org/0000-0002-1825-0097"),
        ("0000-0001-5109-3700", "http://0000-0001-5109-3700"),
        ("0000-0002-1694-233X", "https://0000-0002-1694-233X"),
    ],
)
def test_orcid(identifier: str, sample: str) -> None:
    class Model(BaseModel):
        orcid: Orcid

    m = Model(orcid=sample)

    assert m.orcid == f"https://orcid.org/{identifier}"
    assert m.orcid.path == f"/{identifier}"
    assert m.orcid.host == "orcid.org"
    assert m.orcid.scheme == "https"


@pytest.mark.parametrize("sample", ["0000-0002-1825-0099", "0001-5109-3700"])
def test_orcid_fail(sample: str) -> None:
    """Test mal-formed ORCiD (wrong checksum or wrong pattern)."""

    class Model(BaseModel):
        orcid: Orcid

    with pytest.raises(ValidationError):
        Model(orcid=sample)


def test_ror() -> None:
    class Model(BaseModel):
        ror: Ror

    sample = "https://ror.org/02y72wh86"
    m = Model(ror=sample)
    assert m.ror == sample


@pytest.mark.parametrize(
    "sample",
    [
        "02y72wh86",  # not a URL
        "https://ror.org/02y72wh87",  # checksum should fail
        "https://roar.org/02y72wh86",  # wrong domain
    ],
)
def test_ror_fail(sample: str) -> None:
    class Model(BaseModel):
        ror: Ror

    with pytest.raises(ValidationError):
        Model(ror=sample)
