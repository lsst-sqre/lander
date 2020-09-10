"""Tests for the "deparagraph" pandoc filter.

The filter is implemented in lander.ext.parser.pandoc.filters.deparagraph, but
we test it through the lander-deparagraph entrypoint.
"""

from __future__ import annotations

import pypandoc
import pytest


@pytest.mark.parametrize(
    "sample,expected",
    [
        # Should strip <p> tag from single paragraph.
        ("Hello world!", "Hello world!\n"),
        # Should leave <p> tags for multiple paragraphs.
        ("Hello.\n\nWorld!", "<p>Hello.</p>\n<p>World!</p>\n"),
    ],
)
def test_deparagraph(sample: str, expected: str) -> None:
    output = pypandoc.convert_text(
        sample,
        "html5",
        format="latex",
        extra_args=["--filter=lander-deparagraph"],
    )
    assert output == expected
