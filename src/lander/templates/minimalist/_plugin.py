from __future__ import annotations

from pathlib import Path

from lander.ext.template import TemplatePlugin

__all__ = ["MinimalistTemplate"]


class MinimalistTemplate(TemplatePlugin):
    """A minimalist-style landing page template to demonstrate Lander."""

    @property
    def template_dir(self) -> Path:
        """Template directory."""
        return Path(__file__).parent.joinpath("assets")
