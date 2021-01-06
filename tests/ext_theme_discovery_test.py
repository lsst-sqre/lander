"""Tests for the lander.ext.theme._discovery.ThemePluginDirectory."""

from lander.ext.theme import ThemePluginDirectory
from lander.themes.minimalist import MinimalistTheme


def test_discovery() -> None:
    plugins = ThemePluginDirectory.load_plugins()

    assert "minimalist" in plugins.names
    assert plugins["minimalist"] == MinimalistTheme
