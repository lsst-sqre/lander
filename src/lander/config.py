"""Lander's configuration."""

import datetime
import os
import re
import sys
import urllib.parse
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    SecretStr,
    root_validator,
    validator,
)
from structlog import get_logger

from .lsstprojectmeta.tex.lsstdoc import LsstLatexDoc

# Detects a GitHub repo slug from a GitHub URL
GITHUB_SLUG_PATTERN = re.compile(
    r"https://github.com"
    r"/(?P<org>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
    r"/(?P<name>[a-z0-9\-_~%!$&'()*+,;=:@]+)"
)


# Regular expression that matches docushare release tags
# E.g. docushare-v1
DOCUSHARE_TAG_PATTERN = re.compile(r"^docushare-v(?P<number>\d+$)")


HANDLE_PATTERN = re.compile(r"^(?P<series>[a-zA-Z]+)-(?P<number>[0-9]+)")
"""Regular expression that matches a Rubin Observatory document handle
``<series>-<number>`` format.
"""

GIT_REF_PATTERN = re.compile(r"refs/(?P<kind>heads|tags|pull)/(?P<ref>.+)")
"""Regular expression that matches a GitHub Actions ``GITHUB_REF`` environment
variable.
"""


SERIES_NAMES = {
    "dmtn": "Data Management Technical Note",
    "ittn": "LSST IT Technical Note",
    "ldm": "LSST Data Management",
    "lse": "LSST Systems Engineering",
    "lpm": "LSST Project Management",
    "opstn": "LSST Operations Technical Note",
    "pstn": "Project Science Team Technical Note",
    "rtn": "Rubin Observatory Technical Note",
    "smtn": "Simulations Technical Note",
    "sqr": "SQuaRE Technical Note",
    "tstn": "Telescope & Site Technical Note",
    "testn": "Documentation Testing Technical Note",
}
"""Map of the handles of document series to their full names."""


def _build_ci_url() -> Optional[str]:
    if os.getenv("GITHUB_RUN_ID") and os.getenv("GITHUB_REPOSITORY"):
        run_id = os.getenv("GITHUB_RUN_ID")
        repo = os.getenv("GITHUB_REPOSITORY")
        return "https://github.com/{repo}/actions/runs/{run_id}".format(
            repo=repo, run_id=run_id
        )
    elif os.getenv("TRAVIS_BUILD_WEB_URL"):
        return os.getenv("TRAVIS_BUILD_WEB_URL")
    else:
        return None


def _build_ci_number() -> Optional[str]:
    envvars = ["GITHUB_RUN_NUMBER", "TRAVIS_JOB_NUMBER"]
    for envvar in envvars:
        v = os.getenv(envvar)
        if v:
            return v
    return None


def build_configuration(
    build_dir: str,
    pdf_path: str,
    lsstdoc_tex_path: Optional[str],
    cli_configs: Dict[str, Any],
    extra_downloads: List[str],
    ltd_product: Optional[str],
    ltd_url: str,
    ltd_user: Optional[str],
    ltd_password: Optional[str],
    upload: bool,
) -> "Configuration":
    """Compile the configuration from the command line and document inspection
    sources.
    """
    configs: Dict[str, Any] = {
        "build_dir": build_dir,
        "pdf_path": pdf_path,
        "extra_downloads": extra_downloads,
        "ltd_product": ltd_product,
        "ltd_url": ltd_url,
        "ltd_user": ltd_user,
        "ltd_password": ltd_password,
        "upload": upload,
    }

    # Set configurations from document metadata
    if lsstdoc_tex_path is not None:
        configs.update(_get_lsstdoc_configuration(lsstdoc_tex_path))

    # Override with configurations from the CLI
    configs.update(cli_configs)

    # Build and validation configurations
    return Configuration(**configs)


def _get_lsstdoc_configuration(path: str) -> Dict[str, Any]:
    """Get configuration from the lsstdoc-formatted LaTeX source."""
    logger = get_logger("lander")

    if not os.path.exists(path):
        # FIXME raise exception instead
        logger.error("Cannot find {0}".format(path))
        sys.exit(1)

    config = {}

    lsstdoc = LsstLatexDoc.read(path)
    config["lsstdoc"] = lsstdoc

    config["title"] = {
        "html": lsstdoc.html_title,
        "plain": lsstdoc.plain_title,
    }
    config["build_datetime"] = lsstdoc.revision_datetime

    if lsstdoc.abstract is not None:
        config["abstract"] = {
            "html": lsstdoc.html_abstract,
            "plain": lsstdoc.plain_abstract,
        }
    if lsstdoc.handle is not None:
        config["handle"] = lsstdoc.handle
        config["series"] = lsstdoc.series

    if lsstdoc.authors is not None:
        config["authors"] = [
            {"html": html_author, "plain": plain_author}
            for html_author, plain_author in zip(
                lsstdoc.html_authors, lsstdoc.plain_authors
            )
        ]

    return config


class EncodedString(BaseModel):
    """A string with plain and HTML encodings."""

    plain: Optional[str]
    """Plain encoding."""

    html: Optional[str]
    """HTML encoding."""


class GitRefType(str, Enum):

    tag = "tag"
    branch = "branch"


class Configuration(BaseModel):
    """Lander configuration container and validator."""

    lsstdoc: Optional[LsstLatexDoc]
    """The reduced lsstdoc document."""

    build_dir: str
    """Build directory."""

    pdf_path: str
    """Path of the PDF file."""

    title: EncodedString
    """Document title."""

    abstract: Optional[EncodedString]
    """Document abstract or summary."""

    handle: Optional[str]
    """Document handle."""

    authors: Optional[List[EncodedString]]
    """Document authors."""

    ci_build: Optional[str] = Field(default_factory=_build_ci_number)
    """CI build number."""

    ci_url: Optional[HttpUrl] = Field(default_factory=_build_ci_url)
    """CI build URL."""

    git_sha: Optional[str]
    """The SHA1 of the Git commit."""

    git_ref: Optional[str]
    """Git reference: branch or tag name."""

    git_ref_type: GitRefType = GitRefType.branch
    """Type of git reference: branch or tag."""

    is_travis_pull_request: bool = Field(
        env="TRAVIS_PULL_REQUEST", default=False
    )
    """Flag that is true in a Travis CI PR build.

    This is used to abort PR builds on Travis CI (see the main app runner).
    """

    github_slug: Optional[str]
    """Slug of the GitHub repository (``org/repo``)."""

    extra_downloads: List[str] = Field(default_factory=list)
    """Paths of additional files to include for download."""

    build_datetime: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now()
    )
    """Timestamp of the build."""

    is_draft_branch: bool = False
    """A flag whether a document is a draft."""

    upload: bool = False
    """A flag whether to perform an LSST the Docs upload."""

    ltd_url: HttpUrl = Field(default="https://keeper.lsst.codes")
    """URL of the LTD Keeper API."""

    ltd_user: Optional[str]
    """Username of the LTD Keeper account."""

    ltd_password: Optional[SecretStr]
    """Password of the LTD Keeper account."""

    ltd_product: Optional[str]
    """LSST the Docs product slug."""

    @property
    def series(self) -> Optional[str]:
        """The series, if the handle is set."""
        if self.handle is None:
            return None

        m = HANDLE_PATTERN.match(self.handle)
        if m is None:
            return None
        try:
            return m["series"].upper()
        except Exception:
            return None

    @property
    def series_name(self) -> Optional[str]:
        """The name of the series (if known)."""
        if self.series is None:
            return None

        try:
            return SERIES_NAMES[self.series.lower()]
        except KeyError:
            return None

    @property
    def repo_url(self) -> Optional[str]:
        """GitHub repository URL."""
        if self.github_slug:
            return "https://github.com/{slug}".format(slug=self.github_slug)
        else:
            return None

    @property
    def docushare_url(self) -> Optional[str]:
        """The canonical URL of the document in DocuShare."""
        if self.handle is not None:
            # Make a short link to the DocuShare version page since
            # a) It doesn't immediately trigger a PDF download,
            # b) It gives the user extra information about the document before
            #    downloading it.
            url = "https://ls.st/{}*".format(self.handle)
            try:
                response = requests.head(url, allow_redirects=True, timeout=30)
                if response.status_code != 200:
                    return None
                redirect_url_parts = urllib.parse.urlsplit(response.url)
                if redirect_url_parts.netloc != "docushare.lsst.org":
                    return None
            except requests.exceptions.RequestException:
                return None

            return url
        else:
            return None

    @property
    def relative_pdf_path(self) -> str:
        """The ``pdf_path`` relative to the site root."""
        return os.path.basename(self.pdf_path)

    @property
    def relative_extra_downloads(self) -> List[Dict[str, str]]:
        """Extra downloads: information for the HTML template."""
        data: List[Dict[str, str]] = []

        for download_path in self.extra_downloads:
            relative_path = os.path.basename(download_path)
            # determine a type to choose the octicon
            ext = os.path.splitext(relative_path)[-1].lower()
            if ext == ".pdf":
                download_type = "pdf"
            elif ext in [".tex", ".md", ".txt", ".rst"]:
                download_type = "text"
            elif ext in [".gz", ".zip"]:
                download_type = "zip"
            elif ext in [".tif", ".tiff", ".jpg", ".jpeg", ".png", ".gif"]:
                download_type = "media"
            elif ext in [".py", ".h", ".c", ".cpp", ".ipynb", ".json"]:
                download_type = "code"
            else:
                download_type = "file"
            data.append({"path": relative_path, "type": download_type})

        return data

    @validator("pdf_path", always=True)
    def check_pdf_path(cls, v: str) -> str:
        """Validate the pdf_path field."""
        if not os.path.exists(v):
            raise ValueError('PDF "{}" not found. Check --pdf-path'.format(v))

        ext = os.path.splitext(v)[-1]
        if ext.lower() != ".pdf":
            raise ValueError(
                "--pdf-path must be a PDF. "
                "The detected extension is {}".format(ext)
            )

        return v

    @validator("title", always=True)
    def check_title(cls, v: EncodedString) -> EncodedString:
        """Validate the title field."""
        if v.plain is None and v.html is None:
            raise ValueError("--title must be set.")

        # Ensure both html and plain encodings are set
        if v.html is None:
            v.html = v.plain
        if v.plain is None:
            v.plain = v.html

        return v

    @validator("abstract", always=True)
    def check_abstract(
        cls, v: Optional[EncodedString]
    ) -> Optional[EncodedString]:
        """Validate the abstract field."""
        if v is None:
            return None

        # Ensure both html and plain encodings are set
        if v.html is None:
            v.html = v.plain
        if v.plain is None:
            v.plain = v.html

        return v

    @validator("authors", always=True, each_item=True)
    def check_author(cls, v: EncodedString) -> EncodedString:
        """Check individual author names."""
        if v.plain is None and v.html is None:
            raise ValueError("Author name is empty.")

        # Ensure both html and plain encodings are set
        if v.html is None:
            v.html = v.plain
        if v.plain is None:
            v.plain = v.html

        return v

    @root_validator
    def validate_git_ref(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the ``git_ref`` field and set ``git_ref_type``."""
        if values["git_ref"] is None:
            return values

        m = GIT_REF_PATTERN.match(values["git_ref"])
        if m is not None:
            # Must be in GitHub Actions
            values["git_ref"] = m["ref"]
            if m["kind"] == "heads":
                values["git_ref_type"] = GitRefType.branch
            else:
                values["git_ref_type"] = GitRefType.tag
        else:
            # Not in GitHub Actions
            if os.getenv("TRAVIS_TAG") is not None:
                values["git_ref_type"] = GitRefType.tag

        return values

    @root_validator
    def validate_upload(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LTD upload configurations."""
        if values["upload"]:
            if values["ltd_user"] is None:
                raise ValueError(
                    "An LSST the Docs username must be set with the "
                    "--ltd-user option or LTD_USERNAME environment variable "
                    "to upload to LSST the Docs."
                )

            if values["ltd_password"] is None:
                raise ValueError(
                    "An LSST the Docs password must be set with the "
                    "--ltd-password option or LTD_PASSWORD environment "
                    "variable to upload to LSST the Docs."
                )

            if values["ltd_product"] is None:
                raise ValueError(
                    "An LSST the Docs product slug must be set with the "
                    "--ltd-product option to upload to LSST the Docs."
                )

        return values

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
