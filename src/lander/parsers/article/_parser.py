from __future__ import annotations

from typing import Any, Dict

from lander.ext.parser import DocumentMetadata, Parser
from lander.ext.parser.texutils.extract import (
    LaTeXCommand,
    LaTeXCommandElement,
)

__all__ = ["ArticleParser"]


class ArticleParser(Parser):
    """A parser for LaTeX article class documents."""

    def extract_metadata(self) -> DocumentMetadata:
        """Extract meta from an article document (parser hook).

        Returns
        -------
        metadata
            The metadata parsed from the document source.
        """
        metadata: Dict[str, Any] = {}
        try:
            metadata["date_modified"] = self._parse_date(self.tex_source)
        except RuntimeError:
            pass
        metadata["title"] = self._parse_title(self.tex_source)

        # Apply canonical URL setting, if available
        if self.settings.canonical_url:
            metadata["canonical_url"] = self.settings.canonical_url

        # Override metadata from YAML or CLI as available
        metadata.update(self.settings.metadata)

        return DocumentMetadata(**metadata)

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
