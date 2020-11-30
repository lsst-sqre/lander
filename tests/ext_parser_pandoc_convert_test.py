"""Tests for the lander.ext.parser.pandoc module's format conversion
functionality.
"""

from __future__ import annotations

from lander.ext.parser.pandoc import convert_text


def test_convert() -> None:
    source = r"Hello \emph{world}"
    expected = "Hello world\n"

    assert expected == convert_text(
        content=source, source_fmt="latex", output_fmt="plain"
    )
