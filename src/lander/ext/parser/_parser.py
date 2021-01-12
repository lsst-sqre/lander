from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional

from lander.ext.parser._cidata import CiMetadata
from lander.ext.parser._datamodel import DocumentMetadata
from lander.ext.parser._gitdata import GitRepository
from lander.ext.parser.texutils.extract import get_macros
from lander.ext.parser.texutils.normalize import read_tex_file, replace_macros

if TYPE_CHECKING:
    from pathlib import Path


__all__ = ["Parser"]


class Parser(metaclass=ABCMeta):
    """Base class for TeX document metadata parsing extensions.

    Parameters
    ----------
    tex_path
        Path to the root tex document.
    """

    def __init__(self, tex_path: Path) -> None:
        self._tex_path = tex_path

        _tex_source = read_tex_file(self.tex_path)
        self._tex_macros = get_macros(_tex_source)
        self._tex_source = self.normalize_source(_tex_source)

        try:
            self._git_repository: Optional[
                GitRepository
            ] = GitRepository.create(self._tex_path.parent)
        except Exception:
            self._git_repository = None

        self._ci_metadata = CiMetadata.create()

        self._metadata = self.extract_metadata(self.tex_source)

    @property
    def tex_path(self) -> Path:
        """"Path to the root TeX source file."""
        return self._tex_path

    @property
    def tex_source(self) -> str:
        """TeX source, which has been normalized."""
        return self._tex_source

    @property
    def tex_macros(self) -> Dict[str, str]:
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
        """Metadata from the CI environment

        This attribute is instantiate automatically and is available to the
        `extract_metadata` hook for use by parser implementations.
        """
        return self._ci_metadata

    @property
    def git_repository(self) -> Optional[GitRepository]:
        """Metadata from the local Git repository

        This attribute is instantiate automatically and is available to the
        `extract_metadata` hook for use by parser implementations.
        """
        return self._git_repository

    @property
    def metadata(self) -> DocumentMetadata:
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
    def extract_metadata(self, tex_source: str) -> DocumentMetadata:
        """Hook for implementing metadata extraction.

        Parameters
        ----------
        tex_source
            TeX source content.

        Returns
        -------
        metadata
            The metadata parsed from the document source.
        """
        raise NotImplementedError
