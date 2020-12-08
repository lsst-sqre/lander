from __future__ import annotations

from pathlib import Path

from lander.ext.theme import ThemePlugin

__all__ = ["MinimalistTheme"]


class MinimalistTheme(ThemePlugin):
    """A minimalist-style landing page theme to demonstrate Lander."""

    @property
    def site_dir(self) -> Path:
        """Site directory containing assets and stub files to render."""
        return Path(__file__).parent.joinpath("site")
