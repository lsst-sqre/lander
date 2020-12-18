from __future__ import annotations

from typing import Optional

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
        try:
            date_modified: Optional[str] = self._parse_date(tex_source)
        except RuntimeError:
            date_modified = None

        return DocumentMetadata(
            title=self._parse_title(tex_source), date_modified=date_modified
        )

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

    def _parse_date(self, tex_source: str) -> str:
        command = LaTeXCommand(
            "date",
            LaTeXCommandElement(name="date", required=True, bracket="{"),
        )
        dates = [t for t in command.parse(tex_source)]
        if len(dates) == 0:
            raise RuntimeError("Could not parse a date command.")
        return dates[-1]["date"]
