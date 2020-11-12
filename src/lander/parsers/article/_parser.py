from __future__ import annotations

from lander.ext.parser import DocumentMetadata, Parser
from lander.ext.parser.texutils.extract import (
    LaTeXCommand,
    LaTeXCommandElement,
)

__all__ = ["ArticleParser"]


class ArticleParser(Parser):
    """A parser for LaTeX article class documents."""

    def extract_metadata(self, tex_source: str) -> DocumentMetadata:
        """Extract meta from an article document (parser hook).

        Parameters
        ----------
        tex_source
            TeX source content.

        Returns
        -------
        metadata
            The metadata parsed from the document source.
        """
        return DocumentMetadata(title=self._parse_title(tex_source),)

    def _parse_title(self, tex_source: str) -> str:
        command = LaTeXCommand(
            "title",
            LaTeXCommandElement(
                name="short_title", required=False, bracket="["
            ),
            LaTeXCommandElement(name="long_title", required=True, bracket="{"),
        )
        titles = [t for t in command.parse(tex_source)]
        if len(titles) == 0:
            raise RuntimeError("Could not parse a title command.")
        return titles[-1]["long_title"]
