"""Highwire Press metadata formatter for Google Scholar."""

from typing import TYPE_CHECKING, List, Optional

from .base import MetaTagFormatterBase

if TYPE_CHECKING:
    from lander.config import Configuration


class HighwireMetadata(MetaTagFormatterBase):
    """Format Lander metadata as Highwire Press tags for Google Scholar.

    Highwire Press metadata tags are used by Google Scholar to index
    academic and technical documents.
    """

    def __init__(self, config: "Configuration") -> None:
        self.config = config

    @property
    def tag_attributes(self) -> List[str]:
        """The names of class properties that create tags."""
        return [
            "title",
            "authors",
            "date",
            "technical_report_number",
            "pdf_url",
            "fulltext_html_url",
        ]

    @property
    def title(self) -> str:
        """The document title tag."""
        title = self.config.title.plain or self.config.title.html or ""
        return f'<meta name="citation_title" content="{self._escape(title)}">'

    @property
    def authors(self) -> List[str]:
        """Author metadata tags.

        Each author generates multiple tags:
        - citation_author
        - citation_author_institution (if available)
        - citation_author_email (if available)
        - citation_author_orcid (if available)
        """
        if not self.config.authors:
            return []

        tags = []
        for author in self.config.authors:
            name = author.plain or author.html or ""
            tags.append(
                f'<meta name="citation_author" content="{self._escape(name)}">'
            )
            # Note: Institution, email, ORCID not currently in Lander config
            # but included here for future extension
        return tags

    @property
    def date(self) -> Optional[str]:
        """The publication date tag.

        Format: YYYY/MM/DD (Highwire requires slash separators)
        """
        if self.config.build_datetime:
            date_str = self.config.build_datetime.strftime("%Y/%m/%d")
            return f'<meta name="citation_date" content="{date_str}">'
        return None

    @property
    def technical_report_number(self) -> Optional[str]:
        """The technical report number (document handle)."""
        if self.config.handle:
            return (
                f'<meta name="citation_technical_report_number" '
                f'content="{self._escape(self.config.handle)}">'
            )
        return None

    @property
    def pdf_url(self) -> Optional[str]:
        """The PDF download URL."""
        if self.config.canonical_url and self.config.pdf_path:
            pdf_url = (
                f"{self.config.canonical_url}/"
                f"{self.config.relative_pdf_path}"
            )
            return f'<meta name="citation_pdf_url" content="{pdf_url}">'
        return None

    @property
    def fulltext_html_url(self) -> Optional[str]:
        """The canonical HTML URL of the document."""
        if self.config.canonical_url:
            return (
                f'<meta name="citation_fulltext_html_url" '
                f'content="{self.config.canonical_url}">'
            )
        return None

    @staticmethod
    def _escape(value: str) -> str:
        """Escape HTML attribute content."""
        return value.replace('"', "&quot;").replace("'", "&#39;")
