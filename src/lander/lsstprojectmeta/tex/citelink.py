__all__ = ["CitationLinker"]

from .commandparser import LatexCommand
from .lsstbib import (
    AuthorYearError,
    NoEntryUrlError,
    get_authoryear_from_entry,
    get_url_from_entry,
)


class CitationLinker(object):
    r"""LaTeX source processor that converts citation commands to ``\href``
    commands.

    This processing is useful for decoupling BibTeX from extracted TeX source
    snippets, like abstracts, that are intended to be converted into another
    markup language by pandoc.

    Parameters
    ----------
    bibtex_database : `pybtex.database.BibliographyData`
        A pybtex bibliography. Use `lsstprojectmeta.lsstbib.get_bibliography`
        to get this.
    """

    def __init__(self, bibtex_database):
        super().__init__()
        self._db = bibtex_database

        # Register and build Linker classes. They all share the same API.
        self._linker_classes = [CitedsLinker, CitedspLinker]
        self._linkers = [cls(self._db) for cls in self._linker_classes]

    def __call__(self, tex_source):
        r"""Convert citations in LaTeX source to Hyperref links.

        Parameters
        ----------
        tex_source : `str`
            LaTeX document source.

        Returns
        -------
        processed_tex : `str`
            LaTeX document source with all citation commands converted to
            ``\hyperref`` commands.
        """
        for linker in self._linkers:
            tex_source = linker(tex_source)
        return tex_source


class BaseCommandLinker(object):
    """Baseclass for citation linkers that process specific types of
    LaTeX commands.
    """

    def __call__(self, tex_source):
        r"""Convert commands of type ``command`` in LaTeX source to Hyperref
        links.

        Parameters
        ----------
        tex_source : `str`
            LaTeX document source.

        Returns
        -------
        processed_tex : `str`
            LaTeX document source with commands of type ``command`` to
            ``\hyperref`` commands.
        """
        while True:
            try:
                parsed = next(self.command.parse(tex_source))
            except StopIteration:
                break
            tex_source = self._replace_command(tex_source, parsed)
        return tex_source


class CitedsLinker(BaseCommandLinker):
    r"""Replace a ``\citeds`` citation with ``\href`` command.

    Examples
    --------
    >>> replace_citeds = CitedsLinker()
    >>> print(replace_citeds(r'\citeds{LDM-151}'))
    \href{https://ls.st/LDM-151}{LDM-151}

    Variant with defined title text:

    >>> print(replace_citeds(r'\citeds[Pipelines Design]{LDM-151}'))
    \href{https://ls.st/LDM-151}{Pipelines Design}
    """

    parens = ("", "")
    """Parentheses characters."""

    command_name = "citeds"
    """Name of LaTeX command."""

    def __init__(self, bibtex_database=None):
        super().__init__()
        self._db = bibtex_database
        self.command = LatexCommand(
            self.command_name,
            {"bracket": "[", "required": False, "name": "title"},
            {"bracket": "{", "required": True, "name": "citekey"},
        )
        self.template = (
            self.parens[0] + r"\href{{{url}}}{{{content}}}" + self.parens[1]
        )

    def _replace_command(self, tex_source, parsed):
        if "title" in parsed:
            content = parsed["title"]
        else:
            # The document handle
            # Could get this from BibTeX
            content = parsed["citekey"]

        url = "https://ls.st/{citekey}".format(citekey=parsed["citekey"])

        href_command = self.template.format(url=url, content=content)
        tex_source = tex_source.replace(parsed.command_source, href_command)

        return tex_source


class CitedspLinker(CitedsLinker):
    r"""Replace a ``\citedsp`` citation with ``\href`` command.

    Examples
    --------
    >>> replace_citedsp = CitedspLinker()
    >>> print(replace_citedsp(r'\citedsp{LDM-151}'))
    [\href{https://ls.st/LDM-151}{LDM-151}]

    Variant with defined title text:

    >>> print(replace_citedsp(r'\citedsp[Pipelines Design]{LDM-151}'))
    [\href{https://ls.st/LDM-151}{Pipelines Design}]
    """

    parens = ("[", "]")
    """Parentheses characters."""

    command_name = "citedsp"
    """Name of LaTeX command."""


class CitepLinker(BaseCommandLinker):
    r"""Replace a ``\citep`` citation with an ``\href`` command.

    Examples
    --------
    >>> from pybtex.database import parse_string
    >>> bibitem = r'''
    ... @ARTICLE{2001ApJ...550..212B,
    ...   author = {{Bell}, E.~F. and {de Jong}, R.~S.},
    ...   title = "{Stellar Mass-to-Light Ratios and the Tully-Fisher
    ...     Relation}",
    ...   journal = {\apj},
    ...   eprint = {astro-ph/0011493},
    ...   keywords = {ISM: Dust, Extinction, Galaxies: Evolution,
    ...     Galaxies: Kinematics and Dynamics, Galaxies: Spiral,
    ...     Galaxies: Stellar Content},
    ...   year = 2001,
    ...   month = mar,
    ...   volume = 550,
    ...   pages = {212-229},
    ...   doi = {10.1086/319728},
    ...   adsurl = {http://adsabs.harvard.edu/abs/2001ApJ...550..212B},
    ...   adsnote = {Provided by the SAO/NASA Astrophysics Data System}
    ... }
    ... '''
    >>> bib_db = parse_string(bibitem, 'bibtex')
    >>> link_citep = CitepLinker(bib_db)
    >>> sample_text = r"\citep{2001ApJ...550..212B}"
    >>> print(link_citep(sample_text))  # doctest: +ELLIPSIS
    [\href{http://adsabs.harvard.edu/abs/2001ApJ...}{Bell and de Jong 2001}]
    """

    def __init__(self, bibtex_database=None):
        super().__init__()
        self._db = bibtex_database
        self.command = LatexCommand(
            "citep",
            {"bracket": "[", "required": False, "name": "prefix"},
            {"bracket": "[", "required": False, "name": "suffix"},
            {"bracket": "{", "required": True, "name": "citekeys"},
        )
        self.outer_template = "[{content}]"
        self.link_template = r"\href{{{url}}}{{{content}}}"

    def _replace_command(self, tex_source, parsed):
        cite_keys = [k.strip() for k in parsed["citekeys"].split(",")]

        hrefs = []
        for cite_key in cite_keys:
            if self._db and cite_key in self._db.entries:
                entry = self._db.entries[cite_key]
                try:
                    url = get_url_from_entry(entry)
                except NoEntryUrlError:
                    url = None

                try:
                    authoryear = get_authoryear_from_entry(entry, paren=False)
                except AuthorYearError:
                    authoryear = None

                if url is not None and authoryear is not None:
                    hrefs.append(
                        self.link_template.format(url=url, content=authoryear)
                    )
                elif url is None and authoryear is not None:
                    # No link in this case
                    hrefs.append(authoryear)
                elif url is not None and authoryear is None:
                    # Link with cite key
                    hrefs.append(
                        self.link_template.format(url=url, content=cite_key)
                    )
                else:
                    # Just show cite key
                    hrefs.append(cite_key)

        replacement = self.outer_template.format(content=", ".join(hrefs))
        tex_source = tex_source.replace(parsed.command_source, replacement)

        return tex_source
