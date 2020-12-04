"""Access loadable plugins."""

from __future__ import annotations

from lander.ext.parser import ParsingPlugins
from lander.ext.template import TemplatePluginDirectory

__all__ = ["parsers", "templates"]


parsers = ParsingPlugins.load_plugins()
"""Parsing plugins directory."""

templates = TemplatePluginDirectory.load_plugins()
"""Template plugins directory."""
