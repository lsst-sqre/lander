from __future__ import annotations

import datetime
import re
from typing import List, Optional

import bleach
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

from lander.ext.parser.pandoc import convert_text

__all__ = ["FormattedString", "Person", "DocumentMetadata"]

WHITESPACE_PATTERN = re.compile(r"\s+")


def collapse_whitespace(text: str) -> str:
    """Replace any whitespace character, or group, with a single space."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


class FormattedString(BaseModel):
    """A string with plain and HTML encodings."""

    html: str
    """HTML version of the string."""

    plain: str
    """Plain (unicode) version of the string."""

    latex: Optional[str]
    """LaTeX version of the string, if available."""

    @classmethod
    def from_latex(cls, tex: str, fragment: bool = False) -> FormattedString:
        """Created a FormattedString from LaTeX-encoded content.

        The LaTeX content is transformed to HTML and plain encodings
        via pandoc.
        """
        try:
            plain = convert_text(
                content=tex,
                source_fmt="latex",
                output_fmt="plain",
                deparagraph=fragment,
            )
        except Exception:
            plain = tex  # fallback in case conversion didn't work

        try:
            html = convert_text(
                content=tex,
                source_fmt="latex",
                output_fmt="html",
                deparagraph=fragment,
            )
        except Exception:
            html = tex  # fallback in case conversion didn't work

        return cls(html=html, plain=plain, latex=tex)

    @validator("html")
    def santize_html(cls, v: str) -> str:
        """Ensure that the HTML is safe for injecting into templates."""
        # Add <p> to the default list of allowed tags, which is useful for
        # abstracts.
        return bleach.clean(
            v,
            strip=True,
            tags=[
                "p",
                "a",
                "abbr",
                "acronym",
                "b",
                "blockquote",
                "code",
                "em",
                "i",
                "li",
                "ol",
                "strong",
                "ul",
            ],
        )

    @validator("*")
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class Person(BaseModel):
    """Data about a person."""

    name: str
    """Display name of the person."""

    orcid: Optional[str] = None
    """The ORCiD of the person."""

    affiliations: Optional[List[str]] = Field(default_factory=lambda: [])
    """Names of the person's affiliations."""

    email: Optional[EmailStr] = None
    """Email associated with the person."""

    @validator("name", "affiliations", each_item=True)
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class DocumentMetadata(BaseModel):
    """A container for LaTeX document metadata."""

    title: str
    """Document title."""

    identifier: Optional[str] = None
    """Document identifier."""

    abstract: Optional[FormattedString] = None
    """Document abstract or summary."""

    authors: List[Person] = Field(default_factory=lambda: [])
    """Authors of the document."""

    date_modified: Optional[datetime.datetime] = None
    """Time when the document was last modified."""

    version: Optional[str] = None
    """Version of this document."""

    keywords: List[str] = Field(default_factory=lambda: [])
    """Keywords associated with the document."""

    repository_url: Optional[HttpUrl]
    """URL of the document's source code repository."""

    copyright: Optional[str]
    """Free-form copyright statement."""

    license_identifier: Optional[str]
    """The license of the document, as an SPDX identifier.

    See https://spdx.org/licenses/ for a list of licenses.
    """

    @validator("title", "version", "keywords", "copyright", each_item=True)
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)
