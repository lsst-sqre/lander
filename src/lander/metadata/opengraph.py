"""OpenGraph metadata formatter for social media."""

from datetime import timezone
from typing import TYPE_CHECKING, List, Optional

from .base import MetaTagFormatterBase

if TYPE_CHECKING:
    from lander.config import Configuration


class OpenGraphMetadata(MetaTagFormatterBase):
    """Format Lander metadata as OpenGraph tags for social media.

    OpenGraph metadata enables rich link previews in social media
    platforms and messaging applications.
    """

    def __init__(self, config: "Configuration") -> None:
        self.config = config

    @property
    def tag_attributes(self) -> List[str]:
        """The names of class properties that create tags."""
        return [
            "title",
            "description",
            "url",
            "og_type",
            "authors",
            "dates",
        ]

    @property
    def title(self) -> str:
        """The og:title tag."""
        title = self.config.title.plain or self.config.title.html or ""
        return (
            f'<meta property="og:title" '  # noqa: E231
            f'content="{self._escape(title)}">'
        )

    @property
    def description(self) -> Optional[str]:
        """The og:description tag from the abstract."""
        if self.config.abstract:
            abstract = (
                self.config.abstract.plain or self.config.abstract.html or ""
            )
            return (
                f'<meta property="og:description" '  # noqa: E231
                f'content="{self._escape(abstract)}">'
            )
        return None

    @property
    def url(self) -> Optional[str]:
        """The og:url canonical URL tag."""
        if self.config.canonical_url:
            return (  # noqa: E231
                f'<meta property="og:url" '  # noqa: E231
                f'content="{self.config.canonical_url}">'
            )
        return None

    @property
    def og_type(self) -> str:
        """The og:type tag (always 'article' for documents)."""
        return '<meta property="og:type" content="article">'

    @property
    def authors(self) -> List[str]:
        """The og:article:author tags."""
        if not self.config.authors:
            return []

        tags = []
        for author in self.config.authors:
            name = author.plain or author.html or ""
            tags.append(
                f'<meta property="og:article:author" '  # noqa: E231
                f'content="{self._escape(name)}">'
            )
        return tags

    @property
    def dates(self) -> List[str]:
        """Publication and modification time tags.

        Format: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
        """
        tags = []
        if self.config.build_datetime:
            # Ensure datetime has timezone info
            dt = self.config.build_datetime
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            tags.append(
                f'<meta property="og:article:published_time" '  # noqa: E231
                f'content="{dt_str}">'
            )
            # Also use as modified time since we don't track separate
            # modification dates
            tags.append(
                f'<meta property="og:article:modified_time" '  # noqa: E231
                f'content="{dt_str}">'
            )

        return tags

    @staticmethod
    def _escape(value: str) -> str:
        """Escape HTML attribute content."""
        return value.replace('"', "&quot;").replace("'", "&#39;")
