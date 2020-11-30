"""Test for the built-in (demo) article class document parser plugin."""

from __future__ import annotations

from pathlib import Path

from lander.ext.parser._discovery import ParsingPlugins


def test_article() -> None:
    """Test using the dataset at ``tests/data/article/article.tex``."""
    plugins = ParsingPlugins.load_plugins()
    ArticleParser = plugins["article"]

    tex_path = Path(__file__).parent / "data" / "article" / "article.tex"
    parser = ArticleParser(tex_path)

    md = parser.metadata
    assert md.title == "Example Article Document"
