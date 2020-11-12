"""Tests for the lander.ext.parser.datamodel module."""

from __future__ import annotations

import pytest

from lander.ext.parser._datamodel import FormattedString, collapse_whitespace


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
