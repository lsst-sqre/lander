from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from lander.ext.parser._datamodel import DocumentMetadata
from lander.ext.parser.texutils.normalize import read_tex_file

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
        self._tex_source = read_tex_file(self.tex_path)

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

    @abstractmethod
    def extract_metadata(self, tex_source: str) -> DocumentMetadata:
        """Hook for implementing metadata extraction."""
        raise NotImplementedError
