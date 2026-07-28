"""Author metadata resolution through authors.yaml and the Ook authors API.

Modern Rubin documents (both lsstdoc and AASTeX classes) list their authors
by ID in an ``authors.yaml`` file in the document repository. Those IDs
resolve through the Ook API
(``GET https://roundtable.lsst.cloud/ook/authors/{internal_id}``) to clean
Unicode author names, which is more reliable than parsing names out of
generated LaTeX (DM-55645).
"""

from __future__ import annotations

import html
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import requests
import yaml
from structlog import get_logger

__all__ = ["get_authors_from_authors_yaml", "uses_generated_authors"]

OOK_API_BASE_URL = "https://roundtable.lsst.cloud/ook"
"""Default base URL of the Ook API."""

REQUEST_TIMEOUT = 10.0
"""Timeout (seconds) for each Ook API request."""

MAX_CONCURRENT_REQUESTS = 8
"""Maximum number of concurrent Ook API requests."""

AUTHORS_INPUT_PATTERN = re.compile(r"\\input\s*\{\s*authors(?:\.tex)?\s*\}")
"""Pattern matching an ``\\input`` of the generated ``authors.tex`` file."""


class OokAuthorResolutionError(Exception):
    """Raised when authors cannot be resolved through the Ook API."""


def uses_generated_authors(tex_path: str) -> bool:
    r"""Test whether a LaTeX source file inputs the generated
    ``authors.tex`` file.

    An ``authors.yaml`` file is only an authoritative author list when the
    document actually uses the ``authors.tex`` that db2authors generates
    from it. Some documents carry a stale ``authors.yaml`` alongside a
    hand-written (or commented-out) ``\author`` command; for those, the
    LaTeX source is the truth.

    Parameters
    ----------
    tex_path : `str`
        Path to the document's root LaTeX file.

    Returns
    -------
    bool
        `True` if the source contains an uncommented
        ``\input{authors}`` (or ``\input{authors.tex}``) command.
    """
    try:
        with open(tex_path) as f:
            source = f.read()
    except OSError:
        return False

    for line in source.splitlines():
        # Discard comments: everything after a % that isn't escaped as \%
        code = re.split(r"(?<!\\)%", line, maxsplit=1)[0]
        if AUTHORS_INPUT_PATTERN.search(code):
            return True
    return False


def get_authors_from_authors_yaml(
    root_dir: str,
) -> Optional[List[Dict[str, str]]]:
    """Resolve document authors from an ``authors.yaml`` file via Ook.

    Parameters
    ----------
    root_dir : `str`
        Directory containing the document's root LaTeX file, where an
        ``authors.yaml`` file may reside.

    Returns
    -------
    authors : `list` of `dict`, or `None`
        A list of ``{"plain": ..., "html": ...}`` author names in
        ``authors.yaml`` order, or `None` if ``authors.yaml`` is absent,
        unparseable, or the Ook API could not resolve every author ID. The
        caller should fall back to LaTeX-based author parsing when `None`
        is returned.
    """
    logger = get_logger("lander")

    author_ids = _load_author_ids(os.path.join(root_dir, "authors.yaml"))
    if author_ids is None:
        return None

    base_url = os.getenv("OOK_API_BASE_URL", OOK_API_BASE_URL).rstrip("/")
    try:
        names = _resolve_author_ids(author_ids, base_url)
    except (OokAuthorResolutionError, requests.RequestException) as e:
        logger.warning(
            "Could not resolve authors.yaml through the Ook API; "
            "falling back to LaTeX author parsing: {0}".format(e)
        )
        return None

    logger.info(
        "Resolved {0:d} authors from authors.yaml via the Ook API".format(
            len(names)
        )
    )
    return [
        {"plain": name, "html": html.escape(name, quote=False)}
        for name in names
    ]


def _load_author_ids(yaml_path: str) -> Optional[List[str]]:
    """Load the list of author IDs from an authors.yaml file.

    Returns `None` if the file does not exist or does not contain a list
    of string IDs.
    """
    logger = get_logger("lander")

    if not os.path.exists(yaml_path):
        return None

    try:
        with open(yaml_path) as f:
            data: Any = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.warning("Could not parse {0}: {1}".format(yaml_path, e))
        return None

    if not isinstance(data, list) or not all(
        isinstance(item, str) for item in data
    ):
        logger.warning(
            "{0} is not a list of author ID strings".format(yaml_path)
        )
        return None

    if len(data) == 0:
        return None

    return data


def _resolve_author_ids(author_ids: List[str], base_url: str) -> List[str]:
    """Resolve author IDs to full names through the Ook API.

    Names are returned in the same order as ``author_ids``. Raises
    `OokAuthorResolutionError` if any ID cannot be resolved so the caller
    can fall back to LaTeX parsing rather than exporting a partial author
    list.
    """
    session = requests.Session()

    def _get_name(author_id: str) -> str:
        response = session.get(
            "{0}/authors/{1}".format(base_url, author_id),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            raise OokAuthorResolutionError(
                "Ook API returned {0:d} for author ID {1!r}".format(
                    response.status_code, author_id
                )
            )
        data = response.json()
        given_name = data.get("given_name")
        family_name = data.get("family_name")
        if not family_name:
            raise OokAuthorResolutionError(
                "Ook API returned no family_name for author ID "
                "{0!r}".format(author_id)
            )
        if given_name:
            return "{0} {1}".format(given_name, family_name)
        return family_name

    max_workers = min(MAX_CONCURRENT_REQUESTS, len(author_ids))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_get_name, author_ids))
