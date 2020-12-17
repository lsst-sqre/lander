from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, FilePath, HttpUrl, validator

from lander.plugins import parsers, themes

__all__ = ["BuildSettings"]


class DownloadableFile(BaseModel):
    """Model for a file that's downloadable through the landing page, either
    the main PDF or an attachment.
    """

    file_path: FilePath
    """Path to the file on the filesystem (not the generated site)."""

    name: str
    """Name of the file."""

    mimetype: str
    """The mimetype of the file."""

    extension: str
    """The file's extension."""

    size: int
    """The file's size in bytes."""

    @classmethod
    def load(cls, path: Path) -> DownloadableFile:
        file_type, file_encoding = mimetypes.guess_type(
            str(path), strict=False
        )

        return cls(
            file_path=path,
            name=path.name,
            mimetype=file_type,
            extension=path.suffix,
            size=path.stat().st_size,
        )

    @property
    def human_size(self) -> str:
        """Humanized size label."""
        if self.size < 1000:
            return f"{self.size} B"
        elif self.size < 1000000:
            return f"{self.size / 1000:.0f} kB"
        elif self.size < 1000000000:
            return f"{self.size / 1000000.0:#.1f} MB"
        else:
            return f"{self.size / 1000000000.0:#.1f} GB"


class BuildSettings(BaseModel):

    source_path: FilePath
    """Path to the source file for metadata discovery by the parsing plugin."""

    pdf: DownloadableFile
    """The PDF file to display on the landing page."""

    parser: str
    """Name of the parsing plugin."""

    theme: str
    """Name of the theme plugin."""

    canonical_url: Optional[HttpUrl] = None
    """The canonical URL where the landing page is hosted."""

    output_dir: Path = Field(default_factory=lambda: Path("_build"))
    """Path to the output directory for the built site."""

    attachments: List[DownloadableFile] = Field(default_factory=list)
    """List of file attachments to include on the landing page for
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
        pdf: Optional[Path] = None,
        parser: Optional[str] = None,
        theme: Optional[str] = None,
        canonical_url: Optional[str] = None,
        attachments: Optional[List[Path]] = None,
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
        pdf
            Path to the PDF to display on the landing page (from the
            command-line).
        parser
            Name of the parsing plugin (from the command-line).
        theme
            Name of the theme plugin (from the command-line).
        canonical_url
            The caonical URL where the landing page is hosted.
        attachments
            List of paths to attachments (files) to be included for download
            on the landing page.

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

        # Modify the data to convert paths to DownloadableFile tile
        if "pdf" in settings_data:
            settings_data["pdf"] = DownloadableFile.load(
                Path(settings_data["pdf"])
            )
        if "attachments" in settings_data:
            settings_data["attachments"] = [
                DownloadableFile.load(Path(p))
                for p in settings_data["attachments"]
            ]

        # Adding in command-line overrides
        if output_dir:
            settings_data["output_dir"] = output_dir
        if source_path:
            settings_data["source_path"] = source_path
        if pdf:
            settings_data["pdf"] = DownloadableFile.load(pdf)
        if parser:
            settings_data["parser"] = parser
        if theme:
            settings_data["theme"] = theme
        if canonical_url:
            settings_data["canonical_url"] = canonical_url
        if attachments:
            settings_data["attachments"] = [
                DownloadableFile.load(p) for p in attachments
            ]

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
