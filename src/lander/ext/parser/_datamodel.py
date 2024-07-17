from __future__ import annotations

import datetime
import re
from collections.abc import Generator
from typing import TYPE_CHECKING, Annotated

import base32_lib as base32
import bleach
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator

from lander.ext.parser.pandoc import convert_text
from lander.spdx import Licenses

if TYPE_CHECKING:
    from pydantic.typing import AnyCallable

    CallableGenerator = Generator[AnyCallable, None, None]


__all__ = [
    "FormattedString",
    "Person",
    "Contributor",
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


CollapsedWhitespaceStr = Annotated[str, AfterValidator(collapse_whitespace)]
"""Custom Pydantic string type that collapses whitespace.

Any whitespace character, or continuous group of whitespace characters, is
replaced with a single space. Preceding and trailing whitespace is also
removed.
"""


def validate_orcid_url(value: HttpUrl) -> HttpUrl:
    """Check an ORCiD URL for validity.

    Raises
    ------
    ValueError
        Raised if the URL is not a valid ROR URL.
    """
    m = ORCID_PATTERN.search(str(value))
    if not m:
        raise ValueError(f"Expected ORCiD URL, received: {value}")

    identifier = m["identifier"]
    if not verify_orcid_checksum(identifier):
        raise ValueError(f"ORCiD identifier checksum failed ({value})")

    return HttpUrl(url=f"https://orcid.org/{identifier}")


def verify_orcid_checksum(identifier: str) -> bool:
    """Verify the checksum of an ORCiD identifier string (path component
    of the URL) given the ISO 7064 11,2 algorithm.
    """
    total: int = 0
    for digit in identifier:
        numeric_digit = "10" if digit == "X" else digit
        if not numeric_digit.isdigit():
            continue
        total = (total + int(numeric_digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return result == 10


def format_orcid_url(value: str) -> str:
    """Format a bare ORCiD identifier as a URL."""
    if value.startswith(("http://oricid", "https://orcid")):
        return value
    if verify_orcid_checksum(value):
        return f"https://orcid.org/{value}"
    raise ValueError(f"Not an ORCiD identifier checksum ({value})")


def validate_ror_url(value: HttpUrl) -> HttpUrl:
    """Check a ROR URL for validity.

    Raises
    ------
    ValueError
        Raised if the URL is not a valid ROR URL.
    """
    m = ROR_PATTERN.search(str(value))
    if not m:
        raise ValueError(f"Expected ROR URL, received: {value}")
    identifier = m["identifier"]
    try:
        base32.decode(identifier, checksum=True)
    except ValueError as e:
        raise ValueError("ROR identifier checksum failed") from e

    return value


RorUrl = Annotated[
    HttpUrl,
    AfterValidator(validate_ror_url),
]

OrcidUrl = Annotated[
    HttpUrl,
    AfterValidator(validate_orcid_url),
    BeforeValidator(format_orcid_url),
]


class FormattedString(BaseModel):
    """A string with plain and HTML encodings."""

    html: str
    """HTML version of the string."""

    plain: str
    """Plain (unicode) version of the string."""

    latex: str | None = None
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

    @field_validator("html")
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

    @field_validator("*")
    @classmethod
    def clean_whitespace(cls, v: str) -> str:
        return collapse_whitespace(v)


class Organization(BaseModel):
    """Data about an organization (often used as an affiliation)."""

    name: str
    """The display name of the institution."""

    ror: RorUrl | None = None
    """The ROR identifier of the institution."""

    address: str | None = None
    """The address of the institution."""

    url: HttpUrl | None = None
    """The homepage of the institution."""


class Person(BaseModel):
    """Data about a person."""

    name: CollapsedWhitespaceStr
    """Display name of the person."""

    orcid: OrcidUrl | None = None
    """The ORCiD of the person."""

    affiliations: list[Organization] | None = Field(default_factory=list)
    """The person's affiliations."""

    email: EmailStr | None = None
    """Email associated with the person."""


class Contributor(Person):
    """Data about a contributor.

    A ``Contributor`` is the same as a ``Person``, with the addition of the
    `role` attribute.
    """

    role: str | None = None
    """Description of the contributor's role."""


class DocumentMetadata(BaseModel):
    """A container for LaTeX document metadata."""

    title: CollapsedWhitespaceStr
    """Document title."""

    identifier: str | None = None
    """Document identifier."""

    abstract: FormattedString | None = None
    """Document abstract or summary."""

    authors: list[Contributor] = Field(default_factory=list)
    """Authors of the document."""

    date_modified: datetime.date | None = None
    """Date when the document was last modified."""

    version: CollapsedWhitespaceStr | None = None
    """Version of this document."""

    keywords: list[CollapsedWhitespaceStr] = Field(default_factory=list)
    """Keywords associated with the document."""

    repository_url: HttpUrl | None = None
    """URL of the document's source code repository."""

    copyright: CollapsedWhitespaceStr | None = None
    """Free-form copyright statement."""

    license_identifier: str | None = None
    """The license of the document, as an SPDX identifier.

    See https://spdx.org/licenses/ for a list of licenses.
    """

    full_text: FormattedString | None = None
    """The full text content document."""

    ci_url: HttpUrl | None = None
    """The URL of the continuous integration build for the document."""

    canonical_url: HttpUrl | None = None
    """The canonical URL where this document is published."""

    @field_validator("license_identifier")
    @classmethod
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
