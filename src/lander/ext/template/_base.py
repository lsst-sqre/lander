from __future__ import annotations

import shutil
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Optional

import jinja2

from lander.ext.template.jinjafilters import (
    filter_paragraphify,
    filter_simple_date,
)

if TYPE_CHECKING:
    from lander.ext.parser import DocumentMetadata
    from lander.settings import BuildSettings


__all__ = ["TemplatePlugin"]


class TemplatePlugin(metaclass=ABCMeta):
    """Base class for landing page template plugins.

    Parameters
    ----------
    metadata : `lander.ext.parser.DocumentMetadata`
        The document's metadata, typically created by the parsing plugin.
    """

    def __init__(
        self, *, metadata: DocumentMetadata, settings: BuildSettings
    ) -> None:
        self._metadata = metadata
        self._settings = settings
        self.jinja_env = self.create_jinja_env()

    @property
    def metadata(self) -> DocumentMetadata:
        """The document metadata."""
        return self._metadata

    @property
    def settings(self) -> BuildSettings:
        """The build settings."""
        return self._settings

    def build_site(self, output_dir: Optional[Path] = None) -> None:
        """Build the landing page site, including rendering templates and
        copying assets into the output directory.

        Parameters
        ----------
        output_dir : `pathlib.Path`, optional
            Directory where the landing page site is built. If the output
            directory is not set, the output directory is determined from
            the `TemplatePlugin.settings`.
        """
        if output_dir is None:
            output_dir = self.settings.output_dir
        assert isinstance(output_dir, Path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copying and rendering content from the template
        for path in self._template_dir_contents(self.template_dir):
            if path.suffix == ".jinja":
                self._render_path(path, output_dir)
            else:
                self._copy_path(path, output_dir)

        # Copy the PDF
        output_pdf_path = output_dir.joinpath(self.settings.pdf_path.name)
        shutil.copy(self.settings.pdf_path, output_pdf_path)

        # TODO write metadata file
        # TODO write metadata.jsonld file

    def _template_dir_contents(self, directory: Path) -> Iterator[Path]:
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
                yield from self._template_dir_contents(path)
            else:
                yield path

    def _copy_path(self, template_path: Path, output_dir: Path) -> None:
        """Copy a path in the templates directory into the same relative
        path in the output directory.
        """
        relative_path = template_path.relative_to(self.template_dir)
        output_path = output_dir.joinpath(relative_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(template_path, output_path)

    def _render_path(self, template_path: Path, output_dir: Path) -> None:
        """Render a Jinja2 template and write it to the same relative path
        in the output directory.

        Notes
        -----
        The output path will be the same as the ``template_path``, but without
        the original ``.jinja`` extension.
        """
        relative_path = template_path.relative_to(self.template_dir)
        # Remove the .jinja extension while also locating the rendered output
        # in the build directory.
        output_path = (
            output_dir.joinpath(relative_path)
            .with_suffix("")
            .with_suffix("".join(template_path.suffixes[:-1]))
        )
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.render_template(str(relative_path))
        output_path.write_text(content)

    def render_template(self, template_name: str) -> str:
        """Render a Jinja2 template given its path in the template directory.
        """
        # TODO add attachment information as well (include a dataclass with
        # information about file types for icons?)
        jinja_template = self.jinja_env.get_template(template_name)
        return jinja_template.render(
            metadata=self.metadata,
            settings=self.settings.template_vars,
            pdf_path=self.settings.pdf_path.name,
        )

    def create_jinja_env(self) -> jinja2.Environment:
        """Create a Jinja environment, with the template loader and filters
        set.
        """
        loader = jinja2.FileSystemLoader(str(self.template_dir))
        env = jinja2.Environment(
            loader=loader, autoescape=jinja2.select_autoescape(["html"]),
        )
        env.filters["simple_date"] = filter_simple_date
        env.filters["paragraphify"] = filter_paragraphify
        return env

    @property
    @abstractmethod
    def template_dir(self) -> Path:
        """Template directory."""
        raise NotImplementedError
