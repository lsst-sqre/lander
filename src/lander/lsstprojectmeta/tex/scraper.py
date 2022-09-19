"""TeX source scraping.
"""

__all__ = ["get_macros", "get_def_macros", "get_newcommand_macros"]

import re

from .commandparser import LatexCommand

# Regular expressions for "\def \name {content}"
# Expects the entire command to be on one line.
DEF_PATTERN = re.compile(
    r"\\def\s*"  # def command with optional whitespace
    r"(?P<name>\\[a-zA-Z]*?)\s*"  # macro name with optional whitespace
    r"{(?P<content>.*?)}"
)  # macro contents


def get_macros(tex_source):
    r"""Get all macro definitions from TeX source, supporting multiple
    declaration patterns.

    Parameters
    ----------
    tex_source : `str`
        TeX source content.

    Returns
    -------
    macros : `dict`
        Keys are macro names (including leading ``\``) and values are the
        content (as `str`) of the macros.

    Notes
    -----
    This function uses the following function to scrape macros of different
    types:

    - `get_def_macros`
    - `get_newcommand_macros`

    This macro scraping has the following caveats:

    - Macro definition (including content) must all occur on one line.
    - Macros with arguments are not supported.
    """
    macros = {}
    macros.update(get_def_macros(tex_source))
    macros.update(get_newcommand_macros(tex_source))
    return macros


def get_def_macros(tex_source):
    r"""Get all ``\def`` macro definition from TeX source.

    Parameters
    ----------
    tex_source : `str`
        TeX source content.

    Returns
    -------
    macros : `dict`
        Keys are macro names (including leading ``\``) and values are the
        content (as `str`) of the macros.

    Notes
    -----
    ``\def`` macros with arguments are not supported.
    """
    macros = {}
    for match in DEF_PATTERN.finditer(tex_source):
        macros[match.group("name")] = match.group("content")
    return macros


def get_newcommand_macros(tex_source):
    r"""Get all ``\newcommand`` macro definition from TeX source.

    Parameters
    ----------
    tex_source : `str`
        TeX source content.

    Returns
    -------
    macros : `dict`
        Keys are macro names (including leading ``\``) and values are the
        content (as `str`) of the macros.

    Notes
    -----
    ``\newcommand`` macros with arguments are not supported.
    """
    macros = {}
    command = LatexCommand(
        "newcommand",
        {"name": "name", "required": True, "bracket": "{"},
        {"name": "content", "required": True, "bracket": "{"},
    )

    for macro in command.parse(tex_source):
        macros[macro["name"]] = macro["content"]

    return macros
