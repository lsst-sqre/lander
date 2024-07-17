"""Functions for normalizing TeX source."""

from __future__ import annotations

import logging
import re
from pathlib import Path

__all__ = [
    "remove_comments",
    "remove_trailing_whitespace",
    "read_tex_file",
    "process_inputs",
    "replace_macros",
]


# Regular expression for finding input or include commands
input_include_pattern = re.compile(
    r"\\(?P<command>input|include)"  # command name
    r"(([ ]*\{)|([ ]+))"
    r"(?P<filename>[\w/\-\.]+)"  # included filename
    r"[\}%\s]"  # closing whitespace or bracket
)
"""Regular expression for finding input or include commands."""

input_pattern = re.compile(r"\\input[ ]*?{*?(?P<filename>[\w/\-\.]+)[\}%\s]")
"""Regular expression for finding ``input`` commands."""

include_pattern = re.compile(
    r"\\include[ ]*?{*?(?P<filename>[\w/\-\.]+)[\}%\s]"
)
"""Regular expression for finding ``include`` commands."""


def read_tex_file(root_filepath: Path, root_dir: Path | None = None) -> str:
    r"""Read a TeX file, automatically processing and normalizing it
    (including other input files, removing comments, and deleting trailing
    whitespace).

    Parameters
    ----------
    root_filepath
        Filepath to a TeX file.
    root_dir
        Root directory of the TeX project. This only needs to be set when
        recursively reading in ``\input`` or ``\include`` files and the root
        directory is not the directory of ``root_filepath``.

    Returns
    -------
    tex_source
        TeX source.

    Notes
    -----
    This function runs the following pipeline:

    1. `remove_comments`
    2. `remove_trailing_whitespace`
    3. `process_inputs`
    """
    if not root_filepath.is_file():
        raise ValueError(
            f"root_filepath must be a file (got {root_filepath})."
        )
    tex_source = root_filepath.read_text()

    if root_dir is None:
        root_dir = root_filepath.parent

    # Text processing pipline
    tex_source = remove_comments(tex_source)
    tex_source = remove_trailing_whitespace(tex_source)
    return process_inputs(tex_source, root_dir=root_dir)


def remove_comments(tex_source: str) -> str:
    """Delete latex comments from TeX source.

    Parameters
    ----------
    tex_source
        TeX source content.

    Returns
    -------
    tex_source
        TeX source without comments.
    """
    # Expression via http://stackoverflow.com/a/13365453
    return re.sub(r"(?<!\\)%.*$", r"", tex_source, flags=re.MULTILINE)


def remove_trailing_whitespace(tex_source: str) -> str:
    """Delete trailing whitespace from TeX source.

    Parameters
    ----------
    tex_source
        TeX source content.

    Returns
    -------
    tex_source
        TeX source without trailing whitespace.
    """
    # Delete any space or tab characters right before a new line
    return re.sub(r"[ \t]+$", "", tex_source, flags=re.MULTILINE)


def process_inputs(tex_source: str, root_dir: Path | None = None) -> str:
    r"""Insert referenced TeX file contents (from  ``\input`` and ``\include``
    commands) into the source.

    Parameters
    ----------
    tex_source
        TeX source where referenced source files will be found and inserted.
    root_dir
        Name of the directory containing the TeX project's root file. Files
        referenced by TeX ``\input`` and ``\include`` commands are relative to
        this directory. If not set, the current working directory is assumed.

    Returns
    -------
    tex_source
        TeX source.

    See Also
    --------
    `read_tex_file`
        Recommended API for reading a root TeX source file and inserting
        referenced files.
    """
    logger = logging.getLogger(__name__)

    def _sub_line(match: re.Match) -> str:
        """Substitution content for each match.

        Function to be used with re.sub to inline files for each match.
        """
        fname = match.group("filename")
        full_fname = f"{fname}.tex" if not fname.endswith(".tex") else fname
        dirname = root_dir or Path.cwd()
        full_path = dirname.joinpath(full_fname).resolve()

        try:
            included_source = read_tex_file(full_path, root_dir=root_dir)
        except OSError:
            logger.exception(f"Cannot open {full_path} for inclusion")
            raise
        else:
            return included_source

    return input_include_pattern.sub(_sub_line, tex_source)


def replace_macros(tex_source: str, macros: dict[str, str]) -> str:
    r"""Replace macros in the TeX source with their content.

    Parameters
    ----------
    tex_source
        TeX source content.
    macros
        Keys are macro names (including leading ``\``) and values are the
        content (as `str`) of the macros.

    Returns
    -------
    tex_source : `str`
        TeX source with known macros replaced.

    Notes
    -----
    Macros with arguments are not supported.

    Examples
    --------
    >>> macros = {r"\handle": "LDM-nnn"}
    >>> sample = r"This is document \handle."
    >>> replace_macros(sample, macros)
    'This is document LDM-nnn.'

    Any trailing slash after the macro command is also replaced by this
    function.

    >>> macros = {r"\product": "Data Management"}
    >>> sample = r"\title    [Test Plan]  { \product\ Test Plan}"
    >>> replace_macros(sample, macros)
    '\\title    [Test Plan]  { Data Management Test Plan}'
    """
    for macro_name, macro_content in macros.items():
        # '\\?' suffix matches an optional trailing '\' that might be used
        # for spacing.
        pattern = re.escape(macro_name) + r"\\?"
        # Wrap macro_content in lambda to avoid processing escapes
        tex_source = re.sub(
            pattern,
            lambda _, replacement_content=macro_content: replacement_content,  # type: ignore [misc]
            tex_source,
        )
    return tex_source
