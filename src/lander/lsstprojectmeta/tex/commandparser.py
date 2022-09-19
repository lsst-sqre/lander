"""Flexible LaTeX command parsing.
"""

__all__ = ["LatexCommand", "ParsedCommand"]

import logging
import re


class LatexCommand(object):
    r"""Definition of a LaTeX command's syntax that is used for parsing that
    command's content from a LaTeX source document.

    Parameters
    ----------
    name : `str`
        Name of the LaTeX command. For example, the name of the ``'\title'``
        command is ``'title'`` (without the backslash prefix).
    *elements : `dict`
        Each position element is a dictionary describing that element of the
        command. These elements are provided in the order they appear in
        the command syntax.

        The keys of each dictionary are:

        - ``bracket``: The element's bracket style. Can be ``'['`` or ``'{'``.
        - ``required`` (optional field): `False` if the field is optional.
          `True` if required. Default is `True`.
        - ``name`` (optional field): Name of the field.
    """

    _brackets = {"[": "]", "{": "}"}

    def __init__(self, name, *elements):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.name = name
        # Should add validation to elements
        self.elements = []
        for i, element in enumerate(elements):
            base_element = dict(bracket="{", required=True, name=None)
            base_element.update(element)
            base_element["index"] = i
            self.elements.append(base_element)

    def parse(self, source):
        """Parse command content from the LaTeX source.

        Parameters
        ----------
        source : `str`
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
    def _make_command_regex(name):
        r"""Given a command name, build a regular expression to detect that
        command in TeX source.

        The regular expression is designed to discern "\title{..}" from
        "\titlename{..}". It does this by ensuring that the command is
        followed by a whitespace character, argument brackets, or a comment
        character.

        Parameters
        ----------
        name : `str`
            Name of the command (with a backslash prefix).

        Returns
        -------
        regex : `str`
            Regular expression pattern for detecting the command.
        """
        return r"\\" + name + r"(?:[\s{[%])"

    def _parse_command(self, source, start_index):
        """Parse a single command.

        Parameters
        ----------
        source : `str`
            The full source of the tex document.
        start_index : `int`
            Character index in ``source`` where the command begins.

        Returns
        -------
        parsed_command : `ParsedCommand`
            The parsed command from the source at the given index.
        """
        parsed_elements = []

        # Index of the parser in the source
        running_index = start_index

        for element in self.elements:
            opening_bracket = element["bracket"]
            closing_bracket = self._brackets[opening_bracket]

            # Find the opening bracket.
            element_start = None
            element_end = None
            for i, c in enumerate(source[running_index:], start=running_index):
                if c == element["bracket"]:
                    element_start = i
                    break
                elif c == "\n":
                    # No starting bracket on the line.
                    if element["required"] is True:
                        # Try to parse a single single-word token after the
                        # command, like '\input file'
                        content = self._parse_whitespace_argument(
                            source[running_index:], self.name
                        )
                        return ParsedCommand(
                            self.name,
                            [
                                {
                                    "index": element["index"],
                                    "name": element["name"],
                                    "content": content.strip(),
                                }
                            ],
                            start_index,
                            source[start_index:i],
                        )
                    else:
                        # Give up on finding an optional element
                        break

            # Handle cases when the opening bracket is never found.
            if element_start is None and element["required"] is False:
                # Optional element not found. Continue to next element,
                # not advancing the running_index of the parser.
                continue
            elif element_start is None and element["required"] is True:
                message = (
                    "Parsing command {0} at index {1:d}, "
                    "did not detect element {2:d}".format(
                        self.name, start_index, element["index"]
                    )
                )
                raise CommandParserError(message)

            # Find the closing bracket, keeping track of the number of times
            # the same type of bracket was opened and closed.
            balance = 1
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
                    "Parsing command {0} at index {1:d}, "
                    "did not find closing bracket for required "
                    "command element {2:d}".format(
                        self.name, start_index, element["index"]
                    )
                )
                raise CommandParserError(message)

            # Package the parsed element's content.
            element_content = source[element_start + 1 : element_end]
            parsed_element = {
                "index": element["index"],
                "name": element["name"],
                "content": element_content.strip(),
            }
            parsed_elements.append(parsed_element)

            running_index = element_end + 1

        command_source = source[start_index:running_index]
        parsed_command = ParsedCommand(
            self.name, parsed_elements, start_index, command_source
        )
        return parsed_command

    @staticmethod
    def _parse_whitespace_argument(source, name):
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
            raise CommandParserError(message.format(name))
        content = match.group("content")
        content.strip()
        return content


class ParsedCommand(object):
    r"""Contents of a parsed LaTeX command.

    Parameters
    ----------
    name : `str`
        Name of the LaTeX command. For example, the name of the ``'\title'``
        command is ``'title'`` (without the backslash prefix).
    parsed_elements : `list`
        Parsed command elements. Each item is a `dict` with keys:

        - ``index``: `int` index of the element in the `LatexCommand` command
          definition.
        - ``name``: `str` name of the element in the `LatexCommand` command
          definition, or `None` if the element is not named.
        - ``content``: `str` content of the element (tex source).
    start_index : `int`
        Character index in the ``full_source`` where the command begins.
    command_source : `str`
        The full source of the parsed LaTeX command. This can be used to
        replace the full command in the source document.
    """

    def __init__(self, name, parsed_elements, start_index, command_source):
        super().__init__()
        self.name = name
        self.start_index = start_index
        self._parsed_elements = parsed_elements
        self.command_source = command_source

    def __getitem__(self, key):
        element = self._get_element(key)
        return element["content"]

    def __contains__(self, key):
        try:
            self._get_element(key)
        except KeyError:
            return False

        return True

    def _get_element(self, key):
        element = None

        if isinstance(key, int):
            # Get by element index
            for _element in self._parsed_elements:
                if _element["index"] == key:
                    element = _element
                    break
        else:
            # Get by element name
            for _element in self._parsed_elements:
                if _element["name"] == key:
                    element = _element
                    break

        if element is None:
            message = "Key {} not found".format(key)
            raise KeyError(message)
        return element


class CommandParserError(Exception):
    """Error raised when parsing commands from LaTeX source with the
    `CommandParser` class.
    """
