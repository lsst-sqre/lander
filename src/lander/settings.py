from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, FilePath, validator

from lander.plugins import parsers, themes

__all__ = ["BuildSettings"]


class BuildSettings(BaseModel):

    source_path: FilePath
    """Path to the source file for metadata discovery by the parsing plugin."""

    pdf_path: FilePath
    """Path to the PDF file to display on the landing page."""

    parser: str
    """Name of the parsing plugin."""

    theme: str
    """Name of the theme plugin."""

    output_dir: Path = Field(default_factory=lambda: Path("_build"))
    """Path to the output directory for the built site."""

    attachments: List[FilePath] = Field(default_factory=list)
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
        theme: Optional[str] = None,
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
        theme
            Name of the theme plugin (from the command-line).

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
        if theme:
            settings_data["theme"] = theme

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

    @validator("parser")
    def validate_parser_plugin(cls, v: str) -> str:
        if v not in parsers:
            raise ValueError(
                f"'{v}' is not a known parser plugin. Available parser "
                f"plugins are: {', '.join(parsers.names)}."
            )
        return v

    @validator("theme")
    def validate_theme_plugin(cls, v: str) -> str:
        if v not in themes:
            raise ValueError(
                f"'{v}' is not a known theme plugin. Available themes "
                f"are: {', '.join(themes.names)}."
            )
        return v
