from __future__ import annotations

from importlib.metadata import entry_points
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lander.ext.theme import ThemePlugin

__all__ = ["ThemePluginDirectory"]


class ThemePluginDirectory:
    """A class for accessing theme plugins."""

    def __init__(self, plugins: dict[str, type[ThemePlugin]]) -> None:
        self.plugins = plugins

    @classmethod
    def load_plugins(cls) -> ThemePluginDirectory:
        """Load theme plugins from the ``lander.themes`` setuptools
        entry_point metadata.
        """
        discovered_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in entry_points(group="lander.themes")
        }
        return cls(discovered_plugins)

    @property
    def names(self) -> list[str]:
        """The names of available parsing plugins."""
        return sorted(list(self.plugins.keys()))

    def __getitem__(self, key: str) -> type[ThemePlugin]:
        """Get the plugin for the given name."""
        return self.plugins[key]

    def __contains__(self, key: str) -> bool:
        """Determine if the plugins is available, by name."""
        return key in self.plugins
