"""Functions for normalizing TeX source.
"""

__all__ = [
    "remove_comments",
    "remove_trailing_whitespace",
    "read_tex_file",
    "process_inputs",
    "replace_macros",
]

import logging
import os
import re

# Regular expression for finding input or include commands
input_include_pattern = re.compile(
    r"\\(?P<command>input|include)"  # command name
    r"(([ ]*\{)|([ ]+))"
    r"(?P<filename>[\w/\-\.]+)"  # included filename
    r"[\}%\s]"  # closing whitespace or bracket
)
input_pattern = re.compile(r"\\input[ ]*?{*?(?P<filename>[\w/\-\.]+)[\}%\s]")
include_pattern = re.compile(
    r"\\include[ ]*?{*?(?P<filename>[\w/\-\.]+)[\}%\s]"
)


def remove_comments(tex_source):
    """Delete latex comments from TeX source.

    Parameters
    ----------
    tex_source : str
        TeX source content.

    Returns
    -------
    tex_source : str
        TeX source without comments.
    """
    # Expression via http://stackoverflow.com/a/13365453
    return re.sub(r"(?<!\\)%.*$", r"", tex_source, flags=re.M)


def remove_trailing_whitespace(tex_source):
    """Delete trailing whitespace from TeX source.

    Parameters
    ----------
    tex_source : str
        TeX source content.

    Returns
    -------
    tex_source : str
        TeX source without trailing whitespace.
    """
    # Delete any space or tab characters right before a new line
    return re.sub(r"[ \t]+$", "", tex_source, flags=re.M)


def read_tex_file(root_filepath, root_dir=None):
    r"""Read a TeX file, automatically processing and normalizing it
    (including other input files, removing comments, and deleting trailing
    whitespace).

    Parameters
    ----------
    root_filepath : `str`
        Filepath to a TeX file.
    root_dir : `str`
        Root directory of the TeX project. This only needs to be set when
        recursively reading in ``\input`` or ``\include`` files.

    Returns
    -------
    tex_source : `str`
        TeX source.
    """
    with open(root_filepath, "r") as f:
        tex_source = f.read()

    if root_dir is None:
        root_dir = os.path.dirname(root_filepath)

    # Text processing pipline
    tex_source = remove_comments(tex_source)
    tex_source = remove_trailing_whitespace(tex_source)
    tex_source = process_inputs(tex_source, root_dir=root_dir)

    return tex_source


def process_inputs(tex_source, root_dir=None):
    r"""Insert referenced TeX file contents (from  ``\input`` and ``\include``
    commands) into the source.

    Parameters
    ----------
    tex_source : `str`
        TeX source where referenced source files will be found and inserted.
    root_dir : `str`, optional
        Name of the directory containing the TeX project's root file. Files
        referenced by TeX ``\input`` and ``\include`` commands are relative to
        this directory. If not set, the current working directory is assumed.

    Returns
    -------
    tex_source : `str`
        TeX source.

    See also
    --------
    `read_tex_file`
        Recommended API for reading a root TeX source file and inserting
        referenced files.
    """
    logger = logging.getLogger(__name__)

    def _sub_line(match):
        """Function to be used with re.sub to inline files for each match."""
        fname = match.group("filename")
        if not fname.endswith(".tex"):
            full_fname = ".".join((fname, "tex"))
        else:
            full_fname = fname
        full_path = os.path.abspath(os.path.join(root_dir, full_fname))

        try:
            included_source = read_tex_file(full_path, root_dir=root_dir)
        except IOError:
            logger.error("Cannot open {0} for inclusion".format(full_path))
            raise
        else:
            return included_source

    tex_source = input_include_pattern.sub(_sub_line, tex_source)
    return tex_source


def replace_macros(tex_source, macros):
    r"""Replace macros in the TeX source with their content.

    Parameters
    ----------
    tex_source : `str`
        TeX source content.
    macros : `dict`
        Keys are macro names (including leading ``\``) and values are the
        content (as `str`) of the macros. See
        `lsstprojectmeta.tex.scraper.get_macros`.

    Returns
    -------
    tex_source : `str`
        TeX source with known macros replaced.

    Notes
    -----
    Macros with arguments are not supported.

    Examples
    --------
    >>> macros = {r'\handle': 'LDM-nnn'}
    >>> sample = r'This is document \handle.'
    >>> replace_macros(sample, macros)
    'This is document LDM-nnn.'

    Any trailing slash after the macro command is also replaced by this
    function.

    >>> macros = {r'\product': 'Data Management'}
    >>> sample = r'\title    [Test Plan]  { \product\ Test Plan}'
    >>> replace_macros(sample, macros)
    '\\title    [Test Plan]  { Data Management Test Plan}'
    """
    for macro_name, macro_content in macros.items():
        # '\\?' suffix matches an optional trailing '\' that might be used
        # for spacing.
        pattern = re.escape(macro_name) + r"\\?"
        # Wrap macro_content in lambda to avoid processing escapes
        tex_source = re.sub(pattern, lambda _: macro_content, tex_source)
    return tex_source
