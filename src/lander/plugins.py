"""Access loadable plugins."""

from __future__ import annotations

from lander.ext.parser import ParsingPlugins
from lander.ext.theme import ThemePluginDirectory

__all__ = ["parsers", "themes"]


parsers = ParsingPlugins.load_plugins()
"""Parsing plugins directory."""

themes = ThemePluginDirectory.load_plugins()
"""Theme plugins directory."""
