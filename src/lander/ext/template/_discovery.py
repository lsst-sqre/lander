from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Type

import pkg_resources

if TYPE_CHECKING:
    from lander.ext.template import TemplatePlugin

__all__ = ["TemplatePluginDirectory"]


class TemplatePluginDirectory:
    """A class for accessing template plugins."""

    def __init__(self, plugins: Dict[str, Type[TemplatePlugin]]) -> None:
        self.plugins = plugins

    @classmethod
    def load_plugins(cls) -> TemplatePluginDirectory:
        """Load template plugins from the ``lander.template`` setuptools
        entry_point metadata.
        """
        discovered_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points(
                "lander.templates"
            )
        }
        return cls(discovered_plugins)

    @property
    def names(self) -> List[str]:
        """The names of available parsing plugins."""
        return list(self.plugins.keys())

    def __getitem__(self, key: str) -> Type[TemplatePlugin]:
        """Get the plugin for the given name."""
        return self.plugins[key]
