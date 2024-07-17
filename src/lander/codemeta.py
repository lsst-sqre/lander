"""Support for generating metadata.jsonld files from parsed
document metadata.

This metadata format is considered legacy for compatibility with the orignal
versions of Lander (versions 0.x).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

__all__ = ["CodemetaPerson", "CodemetaData"]

if TYPE_CHECKING:
    from lander.ext.parser import DocumentMetadata


class CodemetaPerson(BaseModel):
    """A JSON-LD presentation of a person (typically an author)."""

    name: str

    at__type: str = Field("Person", alias="@type")
    model_config = ConfigDict(populate_by_name=True)


class CodemetaData(BaseModel):
    """A Codemeta/JSON-LD version of document metadata.

    This data model is compatible with the ``metadata.jsonld`` files produced
    by the early versions of Lander (0.x).
    """

    at__id: str = Field("", alias="@id")

    at__context: list[str] = Field(
        alias="@context",
        default_factory=lambda: [
            "https://raw.githubusercontent.com/codemeta/codemeta/2.0-rc/"
            "codemeta.jsonld",
            "http://schema.org",
        ],
    )

    at__type: list[str] = Field(
        alias="@type", default_factory=lambda: ["Report", "SoftwareSourceCode"]
    )

    language: str = "TeX"

    report_number: str | None = Field(None, alias="reportNumber")

    name: str | None = None

    description: str | None = None

    author: list[CodemetaPerson] | None = Field(default_factory=list)

    date_modified: datetime.datetime | None = Field(None, alias="dateModified")

    article_body: str | None = Field(None, alias="articleBody")

    file_format: str = Field("text/plain", alias="fileFormat")

    url: HttpUrl | None = None

    code_repository: HttpUrl | None = Field(None, alias="codeRepository")

    cont_integration: HttpUrl | None = Field(None, alias="contIntegration")

    readme: HttpUrl | None = None

    license_id: str | None = None
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_document_metadata(
        cls,
        *,
        metadata: DocumentMetadata,
        url: str,
        ci_url: str | None = None,  # noqa: ARG003
    ) -> CodemetaData:
        """Create a CodemetaData from a `lander.ext.parser.DocumentMetadata`
        instance.
        """
        if metadata.full_text:
            full_text: str | None = metadata.full_text.plain
        else:
            full_text = None

        return cls.parse_obj(
            {
                "@id": url,
                "@type": ["Report", "SoftwareSourceCode"],
                "reportNumber": metadata.identifier,
                "name": metadata.title,
                "description": metadata.abstract,
                "author": [
                    {"name": a.name, "@type": "Person"}
                    for a in metadata.authors
                ],
                "dateModified": metadata.date_modified,
                "articleBody": full_text,
                "url": url,
                "codeRepository": metadata.repository_url,
                "contIntegration": metadata.ci_url,
            }
        )

    def jsonld(self) -> str:
        """Export to JSON-LD content."""
        return self.json(by_alias=True)
