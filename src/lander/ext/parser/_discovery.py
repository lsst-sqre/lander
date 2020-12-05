from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Type

import pkg_resources

if TYPE_CHECKING:
    from lander.ext.parser import Parser


__all__ = ["ParsingPlugins"]


class ParsingPlugins:
    """A class for accessing loadable parsing plugins."""

    def __init__(self, plugins: Dict[str, Type[Parser]]) -> None:
        self.plugins = plugins

    @classmethod
    def load_plugins(cls) -> ParsingPlugins:
        """Load parsing plugins from the ``lander.parser`` setuptools
        entry_point metadata of installed packages.

        Notes
        -----
        Parsing plugins are declared by package's extry_points. This is an
        example fragment from a ``setup.cfg`` file::

        [options.entry_points]
        lander.parsers =
            article = lander.parsers.article:ArticleParser
        """
        discovered_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points(
                "lander.parsers"
            )
        }
        return cls(discovered_plugins)

    @property
    def names(self) -> List[str]:
        """The names of available parsing plugins."""
        return sorted(list(self.plugins.keys()))

    def __getitem__(self, key: str) -> Type[Parser]:
        """Get the plugin for the given name."""
        return self.plugins[key]

    def __contains__(self, key: str) -> bool:
        """Determine if the plugins is available, by name."""
        return key in self.plugins
