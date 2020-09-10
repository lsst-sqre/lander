from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from lander.ext.parser._datamodel import DocumentMetadata
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
        self._tex_source = self.normalize_source(read_tex_file(self.tex_path))

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
