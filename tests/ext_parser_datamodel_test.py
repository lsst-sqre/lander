"""Tests for the lander.ext.parser.datamodel module."""

from __future__ import annotations

from lander.ext.parser._datamodel import EncodedString


def test_encodedstring_sanitize_html() -> None:
    html_input = '<h1>Hello <a href="https://example.com">world</a></h1>'
    plain_input = "Hello world"

    es = EncodedString(html=html_input, plain=plain_input)

    assert es.plain == plain_input
    # The H1 tag should be stripped, but the link is ok.
    assert es.html == 'Hello <a href="https://example.com">world</a>'
