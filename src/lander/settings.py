from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

__all__ = ["BuildSettings"]


class BuildSettings(BaseModel):

    source_path: Path
    """Path to the source file for metadata discovery by the parsing plugin."""

    pdf_path: Path
    """Path to the PDF file to display on the landing page."""

    parser: str
    """Name of the parsing plugin."""

    template: str
    """Name of the template plugin."""

    output_dir: Path = Field(default_factory=lambda: Path("_build"))
    """Path to the output directory for the built site."""

    attachments: List[Path] = Field(default_factory=list)
    """List of paths to attachments to include in the landing page for
    download.
    """

    metadata: Dict[str, Any] = Field(default_factory=dict)
    """Metadata that overrides any metadata discovered by the parsing plugin.
    """

    template_vars: Dict[str, Any] = Field(default_factory=list)
    """Additional variables that are available to the Jinja template
    environment.
    """

    @classmethod
    def load(
        cls,
        *,
        output_dir: Optional[Path] = None,
        source_path: Optional[Path] = None,
        pdf_path: Optional[Path] = None,
        parser: Optional[str] = None,
        template: Optional[str] = None,
    ) -> BuildSettings:
        """Create build settings by optionally loadings settings from a
        YAML configuration file and overriding settings from the command line.

        Parameters
        ----------
        output_dir
            Path to the directory where the generate landing page website
            is built (command-line override).
        source_path
            Path to the root source file for metadata extraction by the
            parsing plugin (from the command-line). Typically this is the root
            LaTeX file.
        pdf_path
            Path to the PDF to display on the landing page (from the
            command-line).
        parser
            Name of the parsing plugin (from the command-line).
        template
            Name of the template plugin (from the command-line).

        Returns
        -------
        settings
            The ``BuildSettings`` instance.
        """
        settings_path = BuildSettings._get_settings_path(source_path)
        if settings_path:
            settings_data: Dict[str, Any] = yaml.safe_load(
                settings_path.read_text()
            )
        else:
            settings_data = {}

        # Adding in command-line overrides
        if output_dir:
            settings_data["output_dir"] = output_dir
        if source_path:
            settings_data["source_path"] = source_path
        if pdf_path:
            settings_data["pdf_path"] = pdf_path
        if parser:
            settings_data["parser"] = parser
        if template:
            settings_data["template"] = template

        return cls.parse_obj(settings_data)

    @staticmethod
    def _get_settings_path(source_path: Optional[Path]) -> Optional[Path]:
        settings_path = Path.cwd().joinpath("lander.yaml")
        if settings_path.exists():
            return settings_path

        if source_path:
            settings_path = source_path.parent.joinpath("lander.yaml")
            if settings_path.exists():
                return settings_path

        return None
