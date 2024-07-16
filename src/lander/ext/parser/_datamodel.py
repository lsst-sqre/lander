from __future__ import annotations

import datetime
import re
from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import base32_lib as base32
import bleach
from pydantic import BaseConfig, BaseModel, EmailStr, Field, HttpUrl, validator
from pydantic.errors import UrlError
from pydantic.fields import ModelField

from lander.ext.parser.pandoc import convert_text
from lander.spdx import Licenses

if TYPE_CHECKING:
    from pydantic.typing import AnyCallable

    CallableGenerator = Generator[AnyCallable, None, None]


__all__ = [
    "FormattedString",
    "Person",
    "Contributor",
    "Orcid",
    "DocumentMetadata",
]

WHITESPACE_PATTERN = re.compile(r"\s+")

ORCID_PATTERN = re.compile(
    r"(?P<identifier>[0-9X]{4}-[0-9X]{4}-[0-9X]{4}-[0-9X]{4})"
)
"""Regular expression for matching the ORCiD identifier

Examples:

- 0000-0002-1825-0097
- 0000-0001-5109-3700
- 0000-0002-1694-233X

For more information, see
https://support.orcid.org/hc/en-us/articles/360006897674
"""

ROR_PATTERN = re.compile(
    r"https://ror.org"
    r"\/(?P<identifier>0[0-9abcdefghjkmpqrstuvwxyzabcdefghjkmpqrstuvwxyz]{8})",
    flags=re.IGNORECASE,
)


def collapse_whitespace(text: str) -> str:
    """Replace any whitespace character, or group, with a single space."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


class FormattedString(BaseModel):
    """A string with plain and HTML encodings."""

    html: str
    """HTML version of the string."""

    plain: str
    """Plain (unicode) version of the string."""

    latex: str | None
    """LaTeX version of the string, if available."""

    @classmethod
    def from_latex(
        cls, tex: str, *, fragment: bool = False
    ) -> FormattedString:
        """Create a FormattedString from LaTeX-encoded content.

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
    @classmethod
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
    @classmethod
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class OrcidError(UrlError):
    code = "orcid"
    msg_template = "invalid ORCiD"


class Orcid(HttpUrl):
    """An ORCiD type for Pydantic validation.

    The validator forces an ORCiD identifier to always be a URL for
    orcid.org, per https://support.orcid.org/hc/en-us/articles/360006897674.
    This validator implments the ISO 7064 11,2 checksum algorithm.
    """

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(
        cls, value: Any, field: ModelField, config: BaseConfig
    ) -> Orcid:
        if value.__class__ == cls:
            return value

        m = ORCID_PATTERN.search(value)
        if not m:
            raise OrcidError

        identifier = m["identifier"]
        if not cls.verify_checksum(identifier):
            raise OrcidError

        return HttpUrl.validate(
            f"https://orcid.org/{identifier}", field, config
        )

    @staticmethod
    def verify_checksum(identifier: str) -> bool:
        """Verify the checksum of an ORCiD identifier string (path component
        of the URL) given the ISO 7064 11,2 algorithm.
        """
        total: int = 0
        for digit in identifier:
            _digit = digit
            if _digit == "X":
                _digit = "10"
            if not _digit.isdigit():
                continue
            total = (total + int(_digit)) * 2
        remainder = total % 11
        result = (12 - remainder) % 11
        return result == 10


class RorError(UrlError):
    code = "ror"
    msg_template = "invalid ROR"


class Ror(HttpUrl):
    """A ROR (Research Organization Registry) type for Pydantic validation."""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(
        cls, value: Any, field: ModelField, config: BaseConfig
    ) -> Ror:
        if value.__class__ == cls:
            return value

        m = ROR_PATTERN.search(value)
        if not m:
            raise RorError

        identifier = m["identifier"]
        try:
            base32.decode(identifier, checksum=True)
        except ValueError as e:
            raise RorError from e

        return HttpUrl.validate(value, field, config)


class Organization(BaseModel):
    """Data about an organization (often used as an affiliation)."""

    name: str
    """The display name of the institution."""

    ror: Ror | None = None
    """The ROR identifier of the institution."""

    address: str | None = None
    """The address of the institution."""

    url: HttpUrl | None = None
    """The homepage of the institution."""


class Person(BaseModel):
    """Data about a person."""

    name: str
    """Display name of the person."""

    orcid: Orcid | None = None
    """The ORCiD of the person."""

    affiliations: list[Organization] | None = Field(default_factory=list)
    """The person's affiliations."""

    email: EmailStr | None = None
    """Email associated with the person."""

    @classmethod
    @validator("name")
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class Contributor(Person):
    """Data about a contributor.

    A ``Contributor`` is the same as a ``Person``, with the addition of the
    `role` attribute.
    """

    role: str | None = None
    """Description of the contributor's role."""


class DocumentMetadata(BaseModel):
    """A container for LaTeX document metadata."""

    title: str
    """Document title."""

    identifier: str | None = None
    """Document identifier."""

    abstract: FormattedString | None = None
    """Document abstract or summary."""

    authors: list[Contributor] = Field(default_factory=list)
    """Authors of the document."""

    date_modified: datetime.date | None = None
    """Date when the document was last modified."""

    version: str | None = None
    """Version of this document."""

    keywords: list[str] = Field(default_factory=list)
    """Keywords associated with the document."""

    repository_url: HttpUrl | None
    """URL of the document's source code repository."""

    copyright: str | None
    """Free-form copyright statement."""

    license_identifier: str | None
    """The license of the document, as an SPDX identifier.

    See https://spdx.org/licenses/ for a list of licenses.
    """

    full_text: FormattedString | None = None
    """The full text content document."""

    ci_url: HttpUrl | None = None
    """The URL of the continuous integration build for the document."""

    canonical_url: HttpUrl | None = None
    """The canonical URL where this document is published."""

    @classmethod
    @validator("title", "version", "keywords", "copyright", each_item=True)
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)

    @classmethod
    @validator("license_identifier")
    def validate_spdx(cls, v: str | None) -> str | None:
        if v is not None:
            licenses = Licenses.load()
            if v not in licenses:
                raise ValueError(
                    f"License ID '{v}' is not a valid SPDX license identifier."
                )
        return v

    def get_license_name(self) -> str | None:
        """Get the name of the license."""
        if self.license_identifier is not None:
            licenses = Licenses.load()
            spdx_license = licenses[self.license_identifier]
            return spdx_license.name
        else:
            return None
