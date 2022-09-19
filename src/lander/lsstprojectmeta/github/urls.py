"""Build and parse standard GitHub URLs.
"""

__all__ = (
    "RepoSlug",
    "parse_repo_slug_from_url",
    "make_raw_content_url",
    "normalize_repo_root_url",
)

import collections
import re

RepoSlug = collections.namedtuple("RepoSlug", "full owner repo")
"""GitHub repository slug (`collections.namedtuple`).

Attributes
----------
full : `str`
    Full repository slug. Example: ``'lsst-sqre/lsst-projectmeta-kit'``.
owner : `str`
    Repository owner component. Example: ``'lsst-sqre'``.
repo : `str`
    Repository name component. Example: ``'lsst-projectmeta-kit'``.
"""


# Detects a GitHub repo slug from a GitHub URL
GITHUB_SLUG_PATTERN = re.compile(
    r"https://github.com"
    r"/(?P<org>[a-zA-Z0-9\-_~%!$&'()*+,;=:@]+)"
    r"/(?P<name>[a-zA-Z0-9\-_~%!$&'()*+,;=:@]+)"
)


def parse_repo_slug_from_url(github_url):
    """Get the slug, <owner>/<repo_name>, for a GitHub repository from
    its URL.

    Parameters
    ----------
    github_url : `str`
        URL of a GitHub repository.

    Returns
    -------
    repo_slug : `RepoSlug`
        Repository slug with fields ``full``, ``owner``, and ``repo``.
        See `RepoSlug` for details.

    Raises
    ------
    RuntimeError
        Raised if the URL cannot be parsed.
    """
    match = GITHUB_SLUG_PATTERN.match(github_url)
    if not match:
        message = "Could not parse GitHub slug from {}".format(github_url)
        raise RuntimeError(message)

    _full = "/".join((match.group("org"), match.group("name")))
    return RepoSlug(_full, match.group("org"), match.group("name"))


def make_raw_content_url(repo_slug, git_ref, file_path):
    """Make a raw content (raw.githubusercontent.com) URL to a file.

    Parameters
    ----------
    repo_slug : `str` or `RepoSlug`
        The repository slug, formatted as either a `str` (``'owner/name'``)
        or a `RepoSlug` object (created by `parse_repo_slug_from_url`).
    git_ref : `str`
        The git ref: a branch name, commit hash, or tag name.
    file_path : `str`
        The POSIX path of the file in the repository tree.
    """
    if isinstance(repo_slug, RepoSlug):
        slug_str = repo_slug.full
    else:
        slug_str = repo_slug

    if file_path.startswith("/"):
        file_path = file_path.lstrip("/")

    template = "https://raw.githubusercontent.com/{slug}/{git_ref}/{path}"
    return template.format(slug=slug_str, git_ref=git_ref, path=file_path)


def normalize_repo_root_url(url):
    """Normalize a GitHub URL into the root repository URL.

    Parameters
    ----------
    url : `str`
        A GitHub URL

    Returns
    -------
    url : `str`
        Normalized URL of a GitHub repository.

    Examples
    --------
    >>> normalize_repo_root_url('https://github.com/lsst/LDM-151.git')
    'https://github.com/lsst/LDM-151'
    """
    # Strip the .git extension, if present
    if url.endswith(".git"):
        url = url[:-4]
    return url
