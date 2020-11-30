"""Test the lander.ext.parser.discovery module."""

from lander.ext.parser._discovery import ParsingPlugins
from lander.parsers.article import ArticleParser


def test_discovery() -> None:
    plugins = ParsingPlugins.load_plugins()

    assert "article" in plugins.names
    assert plugins["article"] == ArticleParser
