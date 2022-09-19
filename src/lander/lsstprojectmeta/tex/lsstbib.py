"""APIs for getting and working with the BibTeX databases in lsst-texmf.
"""

__all__ = [
    "get_lsst_bibtex",
    "get_bibliography",
    "get_url_from_entry",
    "NoEntryUrlError",
    "get_authoryear_from_entry",
    "AuthorYearError",
]

import asyncio
import logging
import os

import pybtex.database
from aiohttp import ClientSession

# https://lsst-texmf.lsst.io/lsstdoc.html#bibliographies
KNOWN_LSSTTEXMF_BIB_NAMES = ("lsst", "lsst-dm", "refs", "books", "refs_ads")


# Cache of bibtex file content, keyed by name (see KNOWN_LSSTTEXMF_BIB_NAMES).
_LSSTTEXMF_BIB_CACHE = {}


async def _download_text(url, session):
    """Asynchronously request a URL and get the encoded text content of the
    body.

    Parameters
    ----------
    url : `str`
        URL to download.
    session : `aiohttp.ClientSession`
        An open aiohttp session.

    Returns
    -------
    content : `str`
        Content downloaded from the URL.
    """
    logger = logging.getLogger(__name__)
    async with session.get(url) as response:
        # aiohttp decodes the content to a Python string
        logger.info("Downloading %r", url)
        return await response.text()


async def _download_lsst_bibtex(bibtex_names):
    """Asynchronously download a set of lsst-texmf BibTeX bibliographies from
    GitHub.

    Parameters
    ----------
    bibtex_names : sequence of `str`
        Names of lsst-texmf BibTeX files to download. For example:

        .. code-block:: python

           ["lsst", "lsst-dm", "refs", "books", "refs_ads"]

    Returns
    -------
    bibtexs : `list` of `str`
        List of BibTeX file content, in the same order as ``bibtex_names``.
    """
    blob_url_template = (
        "https://raw.githubusercontent.com/lsst/lsst-texmf/master/texmf/"
        "bibtex/bib/{name}.bib"
    )
    urls = [blob_url_template.format(name=name) for name in bibtex_names]

    tasks = []
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(_download_text(url, session))
            tasks.append(task)

        return await asyncio.gather(*tasks)


def get_lsst_bibtex(bibtex_filenames=None):
    """Get content of lsst-texmf bibliographies.

    BibTeX content is downloaded from GitHub (``master`` branch of
    https://github.com/lsst/lsst-texmf or retrieved from an in-memory cache.

    Parameters
    ----------
    bibtex_filenames : sequence of `str`, optional
        List of lsst-texmf BibTeX files to retrieve. These can be the filenames
        of lsst-bibtex files (for example, ``['lsst.bib', 'lsst-dm.bib']``)
        or names without an extension (``['lsst', 'lsst-dm']``). The default
        (recommended) is to get *all* lsst-texmf bibliographies:

        .. code-block:: python

           ["lsst", "lsst-dm", "refs", "books", "refs_ads"]

    Returns
    -------
    bibtex : `dict`
        Dictionary with keys that are bibtex file names (such as ``'lsst'``,
        ``'lsst-dm'``). Values are the corresponding bibtex file content
        (`str`).
    """
    logger = logging.getLogger(__name__)

    if bibtex_filenames is None:
        # Default lsst-texmf bibliography files
        bibtex_names = KNOWN_LSSTTEXMF_BIB_NAMES
    else:
        # Sanitize filenames (remove extensions, path)
        bibtex_names = []
        for filename in bibtex_filenames:
            name = os.path.basename(os.path.splitext(filename)[0])
            if name not in KNOWN_LSSTTEXMF_BIB_NAMES:
                logger.warning("%r is not a known lsst-texmf bib file", name)
                continue
            bibtex_names.append(name)

    # names of bibtex files not in cache
    uncached_names = [
        name for name in bibtex_names if name not in _LSSTTEXMF_BIB_CACHE
    ]
    if len(uncached_names) > 0:
        # Download bibtex and put into the cache
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(_download_lsst_bibtex(uncached_names))
        loop.run_until_complete(future)
        for name, text in zip(bibtex_names, future.result()):
            _LSSTTEXMF_BIB_CACHE[name] = text

    return {name: _LSSTTEXMF_BIB_CACHE[name] for name in bibtex_names}


def get_bibliography(lsst_bib_names=None, bibtex=None):
    """Make a pybtex BibliographyData instance from standard lsst-texmf
    bibliography files and user-supplied bibtex content.

    Parameters
    ----------
    lsst_bib_names : sequence of `str`, optional
        Names of lsst-texmf BibTeX files to include. For example:

        .. code-block:: python

           ["lsst", "lsst-dm", "refs", "books", "refs_ads"]

        Default is `None`, which includes all lsst-texmf bibtex files.

    bibtex : `str`
        BibTeX source content not included in lsst-texmf. This can be content
        from a import ``local.bib`` file.

    Returns
    -------
    bibliography : `pybtex.database.BibliographyData`
        A pybtex bibliography database that includes all given sources:
        lsst-texmf bibliographies and ``bibtex``.
    """
    bibtex_data = get_lsst_bibtex(bibtex_filenames=lsst_bib_names)

    # Parse with pybtex into BibliographyData instances
    pybtex_data = [
        pybtex.database.parse_string(_bibtex, "bibtex")
        for _bibtex in bibtex_data.values()
    ]

    # Also parse local bibtex content
    if bibtex is not None:
        pybtex_data.append(pybtex.database.parse_string(bibtex, "bibtex"))

    # Merge BibliographyData
    bib = pybtex_data[0]
    if len(pybtex_data) > 1:
        for other_bib in pybtex_data[1:]:
            for key, entry in other_bib.entries.items():
                bib.add_entry(key, entry)

    return bib


def get_url_from_entry(entry):
    """Get a usable URL from a pybtex entry.

    Parameters
    ----------
    entry : `pybtex.database.Entry`
        A pybtex bibliography entry.

    Returns
    -------
    url : `str`
        Best available URL from the ``entry``.

    Raises
    ------
    NoEntryUrlError
        Raised when no URL can be made from the bibliography entry.

    Notes
    -----
    The order of priority is:

    1. ``url`` field
    2. ``ls.st`` URL from the handle for ``@docushare`` entries.
    3. ``adsurl``
    4. DOI
    """
    if "url" in entry.fields:
        return entry.fields["url"]
    elif entry.type.lower() == "docushare":
        return "https://ls.st/" + entry.fields["handle"]
    elif "adsurl" in entry.fields:
        return entry.fields["adsurl"]
    elif "doi" in entry.fields:
        return "https://doi.org/" + entry.fields["doi"]
    else:
        raise NoEntryUrlError()


class NoEntryUrlError(RuntimeError):
    """Raised when a URL cannot be resolved from a bib entry."""


def get_authoryear_from_entry(entry, paren=False):
    """Get and format author-year text from a pybtex entry to emulate
    natbib citations.

    Parameters
    ----------
    entry : `pybtex.database.Entry`
        A pybtex bibliography entry.
    parens : `bool`, optional
        Whether to add parentheses around the year. Default is `False`.

    Returns
    -------
    authoryear : `str`
        The author-year citation text.
    """

    def _format_last(person):
        """Reformat a pybtex Person into a last name.

        Joins all parts of a last name and strips "{}" wrappers.
        """
        return " ".join([n.strip("{}") for n in person.last_names])

    if len(entry.persons["author"]) > 0:
        # Grab author list
        persons = entry.persons["author"]
    elif len(entry.persons["editor"]) > 0:
        # Grab editor list
        persons = entry.persons["editor"]
    else:
        raise AuthorYearError

    try:
        year = entry.fields["year"]
    except KeyError:
        raise AuthorYearError

    if paren and len(persons) == 1:
        template = "{author} ({year})"
        return template.format(author=_format_last(persons[0]), year=year)
    elif not paren and len(persons) == 1:
        template = "{author} {year}"
        return template.format(author=_format_last(persons[0]), year=year)
    elif paren and len(persons) == 2:
        template = "{author1} and {author2} ({year})"
        return template.format(
            author1=_format_last(persons[0]),
            author2=_format_last(persons[1]),
            year=year,
        )
    elif not paren and len(persons) == 2:
        template = "{author1} and {author2} {year}"
        return template.format(
            author1=_format_last(persons[0]),
            author2=_format_last(persons[1]),
            year=year,
        )
    elif not paren and len(persons) > 2:
        template = "{author} et al {year}"
        return template.format(author=_format_last(persons[0]), year=year)
    elif paren and len(persons) > 2:
        template = "{author} et al ({year})"
        return template.format(author=_format_last(persons[0]), year=year)


class AuthorYearError(RuntimeError):
    """Raised when an author-year citation cannot be made from a bib entry."""
