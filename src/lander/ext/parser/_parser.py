from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from lander.ext.parser._cidata import CiMetadata
from lander.ext.parser._datamodel import DocumentMetadata
from lander.ext.parser._gitdata import GitRepository
from lander.ext.parser.texutils.extract import get_macros
from lander.ext.parser.texutils.normalize import read_tex_file, replace_macros

if TYPE_CHECKING:
    from pathlib import Path

    from lander.settings import BuildSettings


__all__ = ["Parser", "MetadataContainer"]

#: Type variable of the DocumentMetadata Pydantic object being stored in Parser
MetadataContainer = TypeVar("MetadataContainer", bound=DocumentMetadata)


class Parser(Generic[MetadataContainer], metaclass=ABCMeta):
    """Base class for TeX document metadata parsing extensions.

    Parameters
    ----------
    settings : `lander.settings.BuildSettings`
        The build settings for this site, which includes command-line and YAML
        configuration overrides of metadata.
    """

    def __init__(self, *, settings: BuildSettings) -> None:
        self._settings = settings

        _tex_source = read_tex_file(self.tex_path)
        self._tex_macros = get_macros(_tex_source)
        self._tex_source = self.normalize_source(_tex_source)

        try:
            self._git_repository: GitRepository | None = GitRepository.create(
                self.tex_path.parent
            )
        except Exception:
            self._git_repository = None

        self._ci_metadata = CiMetadata.create()

        self._metadata = self.extract_metadata()

    @property
    def settings(self) -> BuildSettings:
        """The build settings."""
        return self._settings

    @property
    def tex_path(self) -> Path:
        """Path to the root TeX source file."""
        return self.settings.source_path

    @property
    def tex_source(self) -> str:
        """TeX source, which has been normalized."""
        return self._tex_source

    @property
    def tex_macros(self) -> dict[str, str]:
        """TeX macros detected by
        `lander.ext.parser.texutils.extract.get_macros`.

        Keys are command names (including the slash) and values are the values
        of those macros.

        This property is useful because the normalized source in `tex_source`
        typically has macro definitions clobbered.
        """
        return self._tex_macros

    @property
    def ci_metadata(self) -> CiMetadata:
        """Metadata from the CI environment.

        This attribute is instantiated automatically and is available to the
        `extract_metadata` hook for use by parser implementations.
        """
        return self._ci_metadata

    @property
    def git_repository(self) -> GitRepository | None:
        """Metadata from the local Git repository.

        This attribute is instantiated automatically and is available to the
        `extract_metadata` hook for use by parser implementations.
        """
        return self._git_repository

    @property
    def metadata(self) -> MetadataContainer:
        """Metadata about the document."""
        return self._metadata

    def normalize_source(self, tex_source: str) -> str:
        """Process the TeX source after it is read, but before metadata
        is extracted.

        Parameters
        ----------
        tex_source
            TeX source content.

        Returns
        -------
        tex_source
            Normalized TeX source content.
        """
        macros = get_macros(tex_source)
        return replace_macros(tex_source, macros)

    @abstractmethod
    def extract_metadata(self) -> MetadataContainer:
        """Extract metadata from the document.

        This method should be implemented by parser subclasses.

        Returns
        -------
        metadata
            The metadata parsed from the document source.
        """
        raise NotImplementedError
