from __future__ import annotations

import logging
import shutil
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

import jinja2

from lander.ext.theme._jinjaloader import ThemeTemplateLoader
from lander.ext.theme.jinjafilters import (
    filter_paragraphify,
    filter_simple_date,
)

if TYPE_CHECKING:
    from lander.ext.parser import DocumentMetadata
    from lander.settings import BuildSettings


__all__ = ["ThemePlugin"]


class ThemePlugin(metaclass=ABCMeta):
    """Base class for landing page theme plugins.

    Parameters
    ----------
    metadata : `lander.ext.parser.DocumentMetadata`
        The document's metadata, typically created by the parsing plugin.
    """

    def __init__(
        self, *, metadata: DocumentMetadata, settings: BuildSettings
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self._base_theme: Optional[ThemePlugin] = None
        self._metadata = metadata
        self._settings = settings

        self._template_loader = self._init_template_loader()
        self._jinja_env = self.create_jinja_env()

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this theme."""
        raise NotImplementedError

    @property
    def metadata(self) -> DocumentMetadata:
        """The document metadata."""
        return self._metadata

    @property
    def settings(self) -> BuildSettings:
        """The build settings."""
        return self._settings

    @property
    def template_loader(self) -> ThemeTemplateLoader:
        """The Jinja template loader."""
        return self._template_loader

    @property
    def logger(self) -> logging.Logger:
        """Logger for use the theme plugin."""
        return self._logger

    @property
    def jinja_env(self) -> jinja2.Environment:
        """The Jinja environment."""
        return self._jinja_env

    @property
    def base_theme_name(self) -> Optional[str]:
        """Name of the base theme, or `None` if this theme does not inherit
        from another theme.
        """
        return None

    @property
    def base_theme(self) -> Optional[ThemePlugin]:
        """The base theme."""
        if self.base_theme_name is not None:
            if self._base_theme is None:
                from lander.plugins import themes

                self._base_theme = themes[self.base_theme_name](
                    metadata=self.metadata, settings=self.settings
                )
            return self._base_theme
        else:
            return None

    def build_site(self, output_dir: Optional[Path] = None) -> None:
        """Build the landing page site, including rendering templates and
        copying assets into the output directory.

        Parameters
        ----------
        output_dir : `pathlib.Path`, optional
            Directory where the landing page site is built. If the output
            directory is not set, the output directory is determined from
            the `ThemePlugin.settings`.
        """
        if output_dir is None:
            output_dir = self.settings.output_dir
        assert isinstance(output_dir, Path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copying and rendering content from the theme's site directory
        for path in self._site_dir_contents(self.site_dir):
            if path.suffix == ".jinja":
                self._render_path(path, output_dir)
            else:
                self._copy_path(path, output_dir)

        # Copy the PDF
        output_pdf_path = output_dir.joinpath(self.settings.pdf_path.name)
        shutil.copy(self.settings.pdf_path, output_pdf_path)

        # TODO write metadata file
        # TODO write metadata.jsonld file

    def _site_dir_contents(self, directory: Path) -> Iterator[Path]:
        """Iterate over the contents of a directory, including contents of
        subdirectories.

        Parameters
        ----------
        directory : `pathlib.Path`
            Root directory to find files.

        Yields
        ------
        path : `pathlib.Path`
            Path to a file inside ``directory``.
        """
        for path in directory.iterdir():
            if path.is_dir():
                yield from self._site_dir_contents(path)
            else:
                yield path

    def _copy_path(self, site_path: Path, output_dir: Path) -> None:
        """Copy a path in the theme's site directory into the same relative
        path in the output directory.
        """
        relative_path = site_path.relative_to(self.site_dir)
        output_path = output_dir.joinpath(relative_path)
        self.logger.debug("Copying %s to %s", relative_path, output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(site_path, output_path)

    def _render_path(self, site_path: Path, output_dir: Path) -> None:
        """Render a Jinja2 template and write it to the same relative path
        in the output directory.

        Notes
        -----
        The output path will be the same as the ``site_path``, but without
        the original ``.jinja`` extension.
        """
        # Relative path of template
        relative_path = site_path.relative_to(self.site_dir)
        # Relative path of the output (remove the .jinja extension)
        relative_output_path = relative_path.with_suffix("").with_suffix(
            "".join(site_path.suffixes[:-1])
        )
        # Remove the .jinja extension while also locating the rendered output
        # in the build directory.
        output_path = output_dir.joinpath(relative_output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        template_name = f"${self.name}/{relative_path!s}"
        self.logger.debug("Rendering templated file: %s", relative_output_path)
        jinja_template = self.jinja_env.get_template(template_name)
        context = self.create_jinja_context(
            path=relative_output_path, template_name=template_name
        )
        content = jinja_template.render(**context)

        output_path.write_text(content)

    def _init_template_loader(self) -> ThemeTemplateLoader:
        """Initialize the custom Jinja template loader."""
        return ThemeTemplateLoader(self)

    def create_jinja_env(self) -> jinja2.Environment:
        """Create a Jinja environment, with the template loader and filters
        set.
        """
        env = jinja2.Environment(
            loader=self.template_loader,
            autoescape=jinja2.select_autoescape(["html"]),
        )
        env.filters["simple_date"] = filter_simple_date
        env.filters["paragraphify"] = filter_paragraphify
        return env

    def create_jinja_context(
        self, *, path: Path, template_name: str
    ) -> Dict[str, Any]:
        """Create the context for rendering a Jinja template.

        This method can be implemented by themes to customize the Jinja
        context.

        Parameters
        ----------
        path : `pathlib.Path`
            The relative path of the templated context in the site.
        template_name: `str`
            Name of the Jinja template.

        Returns
        -------
        context : `dict`
            Dictionary used as the Jinja template rendering context. Keys
            are variable names in templates.
        """
        context: Dict[str, Any] = {
            "metadata": self.metadata,
            "settings": self.settings.template_vars,
            "pdf_path": self.settings.pdf_path.name,
        }
        return context

    @property
    @abstractmethod
    def site_dir(self) -> Path:
        """Site directory.

        This directory, which is part of the theme's package, contains the
        files and subdirectories that define the built site.

        Files that have a ``.jinja`` extension are treated as Jinja templates
        and their contents are rendered.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def templates_dir(self) -> Path:
        """Templates directory.

        This directory, which is part of the theme's package, contains Jinja
        templates that are included by either Jinja-templates files, or
        other templates.
        """
        raise NotImplementedError
