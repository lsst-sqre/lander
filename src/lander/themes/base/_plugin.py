from __future__ import annotations

from pathlib import Path

from lander.ext.theme import ThemePlugin

__all__ = ["BaseTheme"]


class BaseTheme(ThemePlugin):
    """The base landing page theme that other themes are built on."""

    @property
    def name(self) -> str:
        """Name of this theme."""
        return "base"

    @property
    def site_dir(self) -> Path:
        """Site directory containing assets and stub files to render."""
        return Path(__file__).parent.joinpath("site")

    @property
    def templates_dir(self) -> Path:
        """Directory containing Jinja templates included by Jinja-templated
        files in the site.
        """
        return Path(__file__).parent.joinpath("templates")
