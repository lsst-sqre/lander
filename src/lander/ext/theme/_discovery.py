from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Type

import pkg_resources

if TYPE_CHECKING:
    from lander.ext.theme import ThemePlugin

__all__ = ["ThemePluginDirectory"]


class ThemePluginDirectory:
    """A class for accessing theme plugins."""

    def __init__(self, plugins: Dict[str, Type[ThemePlugin]]) -> None:
        self.plugins = plugins

    @classmethod
    def load_plugins(cls) -> ThemePluginDirectory:
        """Load theme plugins from the ``lander.themes`` setuptools
        entry_point metadata.
        """
        discovered_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points("lander.themes")
        }
        return cls(discovered_plugins)

    @property
    def names(self) -> List[str]:
        """The names of available parsing plugins."""
        return sorted(list(self.plugins.keys()))

    def __getitem__(self, key: str) -> Type[ThemePlugin]:
        """Get the plugin for the given name."""
        return self.plugins[key]

    def __contains__(self, key: str) -> bool:
        """Determine if the plugins is available, by name."""
        return key in self.plugins
