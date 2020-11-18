"""This modules deals with generating metadata.jsonld files from parsed
document metadata.

This metadata format is considered legacy for compatibility with the orignal
versions of Lander (versions 0.x).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field, HttpUrl

__all__ = ["CodemetaPerson", "CodemetaData"]

if TYPE_CHECKING:
    from lander.ext.parser import DocumentMetadata


class CodemetaPerson(BaseModel):
    """A JSON-LD presentation of a person (typically an author)."""

    name: str

    at__type: str = Field("Person", alias="@type")


class CodemetaData(BaseModel):
    """A Codemeta/JSON-LD version of document metadata.

    This data model is compatible with the ``metadata.jsonld`` files produced
    by the early versions of Lander (0.x).
    """

    at__id: str = Field("", alias="@id")

    at__context: List[str] = Field(
        alias="@context",
        default_factory=lambda: [
            "https://raw.githubusercontent.com/codemeta/codemeta/2.0-rc/"
            "codemeta.jsonld",
            "http://schema.org",
        ],
    )

    at__type: List[str] = Field(
        alias="@type", default_factory=lambda: ["Report", "SoftwareSourceCode"]
    )

    language: str = "TeX"

    reportNumber: Optional[str] = None

    name: Optional[str] = None

    description: Optional[str] = None

    author: Optional[List[CodemetaPerson]] = Field(default_factory=lambda: [])

    dateModified: Optional[datetime.datetime] = None

    articleBody: Optional[str] = None

    fileFormat: str = "text/plain"

    url: Optional[HttpUrl] = None

    codeRepository: Optional[HttpUrl] = None

    contIntegration: Optional[HttpUrl] = None

    readme: Optional[HttpUrl] = None

    license_id: Optional[str] = None

    @classmethod
    def from_document_metadata(
        cls,
        *,
        metadata: DocumentMetadata,
        url: str,
        ci_url: Optional[str] = None,
    ) -> CodemetaData:
        """Create a CodemetaData from a `lander.ext.parser.DocumentMetadata`
        instance.
        """
        if metadata.full_text:
            full_text: Optional[str] = metadata.full_text.plain
        else:
            full_text = None

        instance = cls(
            at__id=url,
            reportNumber=metadata.identifier,
            name=metadata.title,
            description=metadata.abstract,
            author=[CodemetaPerson(name=a.name) for a in metadata.authors],
            dateModified=metadata.date_modified,
            articleBody=full_text,
            url=url,
            codeRepository=metadata.repository_url,
            contIntegration=metadata.ci_url,
        )
        instance.at__id = url
        return instance

    def jsonld(self) -> str:
        """Export to JSON-LD content."""
        return self.json(by_alias=True)
