"""Content extraction form TeX source"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Union

__all__ = [
    "get_macros",
    "get_def_macros",
    "get_newcommand_macros",
    "LaTeXCommandElement",
    "LaTeXCommand",
    "ParsedCommand",
    "ParsedElement",
]

# Regular expressions for "\def \name {content}"
# Expects the entire command to be on one line.
DEF_PATTERN = re.compile(
    r"\\def\s*"  # def command with optional whitespace
    r"(?P<name>\\[a-zA-Z]*?)\s*"  # macro name with optional whitespace
    r"{(?P<content>.*?)}"
)  # macro contents


def get_macros(tex_source: str) -> Dict[str, str]:
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


def get_def_macros(tex_source: str) -> Dict[str, str]:
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


def get_newcommand_macros(tex_source: str) -> Dict[str, str]:
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
    command = LaTeXCommand(
        "newcommand",
        LaTeXCommandElement(name="name", required=True, bracket="{"),
        LaTeXCommandElement(name="content", required=True, bracket="{"),
    )

    for macro in command.parse(tex_source):
        macros[macro["name"]] = macro["content"]

    return macros


@dataclass
class LaTeXCommandElement:

    bracket: Optional[str] = None
    """The element's bracket style, either ``[`` or ``{``."""

    required: bool = False
    """Whether the element is considered optional in the command invocation.
    """

    name: Optional[str] = None
    """Optional name of the element."""

    index: Optional[int] = None
    """Index of the command element in the command."""


@dataclass
class ParsedElement:

    name: Optional[str]
    """Optional name of the element (`None` if the element is not named)."""

    index: int
    """Index of the command element in the command."""

    content: str
    """Content of the command element (tex source)."""


class LaTeXCommand:
    r"""Definition of a LaTeX command's syntax that is used for parsing that
    command's content from a LaTeX source document.

    Parameters
    ----------
    name
        Name of the LaTeX command. For example, the name of the ``'\title'``
        command is ``'title'`` (without the backslash prefix).
    *elements
        Each position element is a dictionary describing that element of the
        command. These elements are provided in the order they appear in
        the command syntax.

        The keys of each dictionary are:

        - ``bracket``: The element's bracket style. Can be ``'['`` or ``'{'``.
        - ``required`` (optional field): `False` if the field is optional.
          `True` if required. Default is `True`.
        - ``name`` (optional field): Name of the field.
    """

    _brackets: Dict[str, str] = {"[": "]", "{": "}"}

    def __init__(self, name: str, *elements: LaTeXCommandElement) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.name = name
        # Should add validation to elements
        self.elements: List[LaTeXCommandElement] = []
        for i, element in enumerate(elements):
            element.index = i
            self.elements.append(element)

    def parse(self, source: str) -> Iterator[ParsedCommand]:
        """Parse command content from the LaTeX source.

        Parameters
        ----------
        source
            The full source of the tex document.

        Yields
        ------
        parsed_command : `ParsedCommand`
            Yields parsed commands instances for each occurence of the command
            in the source.
        """
        command_regex = self._make_command_regex(self.name)
        for match in re.finditer(command_regex, source):
            self._logger.debug(match)
            start_index = match.start(0)
            yield self._parse_command(source, start_index)

    @staticmethod
    def _make_command_regex(name: str) -> str:
        r"""Given a command name, build a regular expression to detect that
        command in TeX source.

        The regular expression is designed to discern "\title{..}" from
        "\titlename{..}". It does this by ensuring that the command is
        followed by a whitespace character, argument brackets, or a comment
        character.

        Parameters
        ----------
        name
            Name of the command (with a backslash prefix).

        Returns
        -------
        regex
            Regular expression pattern for detecting the command.
        """
        return r"\\" + name + r"(?:[\s{[%])"

    def _parse_command(self, source: str, start_index: int) -> ParsedCommand:
        """Parse a single command.

        Parameters
        ----------
        source : `str`
            The full source of the tex document.
        start_index : `int`
            Character index in ``source`` where the command begins.

        Returns
        -------
        parsed_command
            The parsed command from the source at the given index.
        """
        parsed_elements = []

        # Index of the parser in the source
        running_index = start_index

        for element in self.elements:
            assert element.bracket is not None
            opening_bracket = element.bracket
            closing_bracket = self._brackets[opening_bracket]

            # Find the opening bracket.
            element_start = None
            element_end = None
            for i, c in enumerate(source[running_index:], start=running_index):
                if c == element.bracket:
                    element_start = i
                    break
                elif c == "\n":
                    # No starting bracket on the line.
                    if element.required is True:
                        # Try to parse a single single-word token after the
                        # command, like '\input file'
                        content = self._parse_whitespace_argument(
                            source[running_index:], self.name
                        )
                        assert element.index is not None
                        return ParsedCommand(
                            self.name,
                            [
                                ParsedElement(
                                    index=element.index,
                                    name=element.name,
                                    content=content.strip(),
                                )
                            ],
                            start_index,
                            source[start_index:i],
                        )
                    else:
                        # Give up on finding an optional element
                        break

            # Handle cases when the opening bracket is never found.
            if element_start is None and element.required is False:
                # Optional element not found. Continue to next element,
                # not advancing the running_index of the parser.
                continue
            elif element_start is None and element.required is True:
                message = (
                    f"Parsing command {self.name} at index {start_index:d}, "
                    f"did not detect element {element.index:d}"
                )
                raise RuntimeError(message)

            # Find the closing bracket, keeping track of the number of times
            # the same type of bracket was opened and closed.
            balance = 1
            assert element_start is not None
            for i, c in enumerate(
                source[element_start + 1 :], start=element_start + 1
            ):
                if c == opening_bracket:
                    balance += 1
                elif c == closing_bracket:
                    balance -= 1

                if balance == 0:
                    element_end = i
                    break

            if balance > 0:
                message = (
                    f"Parsing command {self.name} at index {start_index:d}, "
                    "did not find closing bracket for required "
                    f"command element {element.index:d}"
                )
                raise RuntimeError(message)

            # Package the parsed element's content.
            element_content = source[element_start + 1 : element_end]
            assert element.index is not None
            assert element_end is not None
            parsed_element = ParsedElement(
                index=element.index,
                name=element.name,
                content=element_content.strip(),
            )
            parsed_elements.append(parsed_element)

            running_index = element_end + 1

        command_source = source[start_index:running_index]
        parsed_command = ParsedCommand(
            self.name, parsed_elements, start_index, command_source
        )
        return parsed_command

    @staticmethod
    def _parse_whitespace_argument(source: str, name: str) -> str:
        r"""Attempt to parse a single token on the first line of this source.

        This method is used for parsing whitespace-delimited arguments, like
        ``\input file``. The source should ideally contain `` file`` along
        with a newline character.

        >>> source = 'Line 1\n' r'\input test.tex' '\nLine 2'
        >>> LatexCommand._parse_whitespace_argument(source, 'input')
        'test.tex'

        Bracket delimited arguments (``\input{test.tex}``) are handled in
        the normal logic of `_parse_command`.
        """
        # First match the command name itself so that we find the argument
        # *after* the command
        command_pattern = r"\\(" + name + r")(?:[\s{[%])"
        command_match = re.search(command_pattern, source)
        if command_match is not None:
            # Trim `source` so we only look after the command
            source = source[command_match.end(1) :]

        # Find the whitespace-delimited argument itself.
        pattern = r"(?P<content>\S+)(?:[ %\t\n]+)"
        match = re.search(pattern, source)
        if match is None:
            message = (
                "When parsing {}, did not find whitespace-delimited command "
                "argument"
            )
            raise RuntimeError(message.format(name))
        content = match.group("content")
        content.strip()
        return content


class ParsedCommand:
    r"""Contents of a parsed LaTeX command.

    Parameters
    ----------
    name
        Name of the LaTeX command. For example, the name of the ``'\title'``
        command is ``'title'`` (without the backslash prefix).
    parsed_elements
        Parsed command elements.
    start_index
        Character index in the ``full_source`` where the command begins.
    command_source
        The full source of the parsed LaTeX command. This can be used to
        replace the full command in the source document.
    """

    def __init__(
        self,
        name: str,
        parsed_elements: List[ParsedElement],
        start_index: int,
        command_source: str,
    ) -> None:
        self.name: str = name
        self.start_index: int = start_index
        self._parsed_elements: List[ParsedElement] = parsed_elements
        self.command_source: str = command_source

    def __getitem__(self, key: Union[int, str]) -> str:
        element = self._get_element(key)
        return element.content

    def __contains__(self, key: Union[int, str]) -> bool:
        try:
            self._get_element(key)
        except KeyError:
            return False

        return True

    def _get_element(self, key: Union[int, str]) -> ParsedElement:
        element = None

        if isinstance(key, int):
            # Get by element index
            for _element in self._parsed_elements:
                if _element.index == key:
                    element = _element
                    break
        else:
            # Get by element name
            for _element in self._parsed_elements:
                if _element.name == key:
                    element = _element
                    break

        if element is None:
            message = "Key {} not found".format(key)
            raise KeyError(message)
        return element
