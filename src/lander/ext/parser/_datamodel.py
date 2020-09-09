from __future__ import annotations

import datetime
import re
from typing import List, Optional

import bleach
from pydantic import BaseModel, EmailStr, HttpUrl, validator

__all__ = ["EncodedString", "Person", "DocumentMetadata"]

WHITESPACE_PATTERN = re.compile(r"\s+")


def collapse_whitespace(text: str) -> str:
    """Replace any whitespace character, or group, with a single space."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


class EncodedString(BaseModel):
    """A string with plain and HTML encodings."""

    html: str
    """HTML version of the string."""

    plain: str
    """Plain (unicode) version of the string."""

    @validator("html")
    def santize_html(cls, v: str) -> str:
        """Ensure that the HTML is safe for injecting into templates."""
        return bleach.clean(v, strip=True)

    @validator("*")
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class Person(BaseModel):
    """Data about a person."""

    name: str
    """Display name of the person."""

    orcid: Optional[str]
    """The ORCiD of the person."""

    affiliations: Optional[List[str]]
    """Names of the person's affiliations."""

    email: Optional[EmailStr]
    """Email associated with the person."""

    @validator("name", "affiliations", each_item=True)
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class DocumentMetadata(BaseModel):
    """A container for LaTeX document metadata."""

    title: str
    """Document title."""

    identifier: Optional[str]
    """Document identifier."""

    abstract: Optional[EncodedString]
    """Document abstract or summary."""

    authors: Optional[List[Person]]
    """Authors of the document."""

    date_modified: Optional[datetime.datetime]
    """Time when the document was last modified."""

    version: Optional[str]
    """Version of this document."""

    keywords: Optional[List[str]]
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
