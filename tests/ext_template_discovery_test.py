"""Tests for the lander.ext.template._discovery.TemplatePluginDirectory."""

from lander.ext.template import TemplatePluginDirectory
from lander.templates.minimalist import MinimalistTemplate


def test_discovery() -> None:
    plugins = TemplatePluginDirectory.load_plugins()

    assert "minimalist" in plugins.names
    assert plugins["minimalist"] == MinimalistTemplate
