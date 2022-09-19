"""Metadata extraction from lsstdoc LSST LaTeX documents."""

__all__ = ["LsstLatexDoc"]

import datetime
import logging
import os

import pytz
from pytz import timezone

from ..git.timestamp import get_content_commit_date
from ..pandoc.convert import convert_lsstdoc_tex
from .citelink import CitationLinker
from .commandparser import LatexCommand
from .lsstbib import KNOWN_LSSTTEXMF_BIB_NAMES, get_bibliography
from .normalizer import read_tex_file, replace_macros
from .scraper import get_macros


class LsstLatexDoc(object):
    """An lsstdoc-class LaTeX document with metadata access.

    Parameters
    ----------
    tex_source : `str`
        LaTeX source for the main file of an lsstdoc LaTeX document.
    root_dir : `str`, optional
        Root directory of the LaTeX project. `None` is treated as the
        current working directory.
    """

    def __init__(self, tex_source, root_dir=None):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        # The BibliographyData (parsed BibTeX) is only loaded when
        # the self.bib_db attributed is first accessed.
        self._bib_db = None

        self._tex = tex_source
        if root_dir is None:
            self._root_dir = ""
        else:
            self._root_dir = root_dir

    @classmethod
    def read(cls, root_tex_path):
        """Construct an `LsstLatexDoc` instance by reading and parsing the
        LaTeX source.

        Parameters
        ----------
        root_tex_path : `str`
            Path to the LaTeX source on the filesystem. For multi-file LaTeX
            projects this should be the path to the root document.

        Notes
        -----
        This method implements the following pipeline:

        1. `lsstprojectmeta.tex.normalizer.read_tex_file`
        2. `lsstprojectmeta.tex.scraper.get_macros`
        3. `lsstprojectmeta.tex.normalizer.replace_macros`

        Thus ``input`` and ``includes`` are resolved along with simple macros.
        """
        # Read and normalize the TeX source, replacing macros with content
        root_dir = os.path.dirname(root_tex_path)
        tex_source = read_tex_file(root_tex_path)
        tex_macros = get_macros(tex_source)
        tex_source = replace_macros(tex_source, tex_macros)
        return cls(tex_source, root_dir=root_dir)

    @property
    def plain_content(self):
        """Plain-text-formatted document content (`str`)."""
        return self.format_content(format="plain", mathjax=False, smart=True)

    @property
    def html_title(self):
        """HTML5-formatted document title (`str`)."""
        return self.format_title(
            format="html5", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def plain_title(self):
        """Plain-text-formatted document title (`str`)."""
        return self.format_title(
            format="plain", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def title(self):
        """LaTeX-formatted document title (`str`)."""
        if not hasattr(self, "_title"):
            self._parse_title()

        return self._title

    @property
    def html_short_title(self):
        """HTML5-formatted document short title (`str`)."""
        return self.format_short_title(
            format="html5", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def plain_short_title(self):
        """Plaintext-formatted document short title (`str`)."""
        return self.format_short_title(
            format="plain", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def short_title(self):
        """LaTeX-formatted document short title (`str`)."""
        if not hasattr(self, "_short_title"):
            self._parse_title()

        return self._short_title

    @property
    def html_authors(self):
        """HTML5-formatted authors (`list` of `str`)."""
        return self.format_authors(
            format="html5", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def plain_authors(self):
        """Plaintext-formatted authors (`list` of `str`)."""
        return self.format_authors(
            format="plain", deparagraph=True, mathjax=False, smart=True
        )

    @property
    def authors(self):
        """LaTeX-formatted authors (`list` of `str`)."""
        if not hasattr(self, "_authors"):
            self._parse_author()

        return self._authors

    @property
    def html_abstract(self):
        """HTML5-formatted document abstract (`str`)."""
        return self.format_abstract(
            format="html5", deparagraph=False, mathjax=False, smart=True
        )

    @property
    def plain_abstract(self):
        """Plaintext-formatted document abstract (`str`)."""
        return self.format_abstract(
            format="plain", deparagraph=False, mathjax=False, smart=True
        )

    @property
    def abstract(self):
        """LaTeX-formatted abstract (`str`)."""
        if not hasattr(self, "_abstract"):
            self._parse_abstract()

        return self._abstract

    @property
    def handle(self):
        """LaTeX-formatted document handle (`str`)."""
        if not hasattr(self, "_handle"):
            self._parse_doc_ref()

        return self._handle

    @property
    def series(self):
        """Document series identifier (`str`)."""
        if not hasattr(self, "_series"):
            self._parse_doc_ref()

        return self._series

    @property
    def serial(self):
        """Document serial number within series (`str`)."""
        if not hasattr(self, "_serial"):
            self._parse_doc_ref()

        return self._serial

    @property
    def is_draft(self):
        """Document is a draft if ``'lsstdoc'`` is included in the
        documentclass options (`bool`).
        """
        if not hasattr(self, "_document_options"):
            self._parse_documentclass()

        if "lsstdraft" in self._document_options:
            return True
        else:
            return False

    @property
    def revision_datetime(self):
        """Current revision date of the document (`datetime.datetime`).

        The `revision_datetime_source` describes how the revision date
        is computed.

        This ``revision datetime`` is cached the first time you access it. This
        means that a datetime computed via ``now`` or ``git`` will not change
        during the lifetime of an `LsstLatexDoc` object.
        """
        if not hasattr(self, "_datetime"):
            self._parse_revision_date()

        return self._datetime

    @property
    def revision_datetime_source(self):
        r"""Data source for the `revision_datetime` attribute (`str`).

        Possible string values are:

        - ``'tex'``: The document revision date is defined in the ``\date``
          command. ``YYYY-MM-DD`` dates are converted to UTC datetimes by
          assuming the document is released at the beginning of the day in the
          ``US/Pacific`` timezone. Note: the ``\date`` command is ignored
          for draft documents (`is_draft` is `True`) so that drafts always
          fall back to ``'git'`` or ``'now'``.

        - ``'git'``: The latest Git commit's timestamp that affected document
          content. Content is considered any file with a ``tex``, ``bib``,
          ``pdf``, ``jpg``, or ``png`` extension. Git timestamps are used when
          the ``\date`` command is missing or can't be parsed.

        - ``'now'``: The current date and time. This source is used as a
          fallback when the LaTeX and Git-based methods of determining a
          document's date fail.

        The `revision datetime` is cached the first time you access it. This
        means that a datetime computed via ``now`` or ``git`` will not change
        during the lifetime of an `LsstLatexDoc` object.
        """
        if not hasattr(self, "_datetime"):
            self._parse_revision_date()

        return self._revision_datetime_source

    @property
    def bib_db(self):
        """Bibliography database referenced by the document
        (`pybtex.database.BibliographyData`).
        """
        if self._bib_db is None:
            # Load reference BibTeX into a pybtex BibliographyData
            self._load_bib_db()
        return self._bib_db

    def format_content(
        self, format="plain", mathjax=False, smart=True, extra_args=None
    ):
        """Get the document content in the specified markup format.

        Parameters
        ----------
        format : `str`, optional
            Output format (such as ``'html5'`` or ``'plain'``).
        mathjax : `bool`, optional
            Allow pandoc to use MathJax math markup.
        smart : `True`, optional
            Allow pandoc to create "smart" unicode punctuation.
        extra_args : `list`, optional
            Additional command line flags to pass to Pandoc. See
            `lsstprojectmeta.pandoc.convert.convert_text`.

        Returns
        -------
        output_text : `str`
            Converted content.
        """
        output_text = convert_lsstdoc_tex(
            self._tex,
            format,
            mathjax=mathjax,
            smart=smart,
            extra_args=extra_args,
        )
        return output_text

    def format_title(
        self,
        format="html5",
        deparagraph=True,
        mathjax=False,
        smart=True,
        extra_args=None,
    ):
        """Get the document title in the specified markup format.

        Parameters
        ----------
        format : `str`, optional
            Output format (such as ``'html5'`` or ``'plain'``).
        deparagraph : `bool`, optional
            Remove the paragraph tags from single paragraph content.
        mathjax : `bool`, optional
            Allow pandoc to use MathJax math markup.
        smart : `True`, optional
            Allow pandoc to create "smart" unicode punctuation.
        extra_args : `list`, optional
            Additional command line flags to pass to Pandoc. See
            `lsstprojectmeta.pandoc.convert.convert_text`.

        Returns
        -------
        output_text : `str`
            Converted content or `None` if the title is not available in
            the document.
        """
        if self.title is None:
            return None

        output_text = convert_lsstdoc_tex(
            self.title,
            format,
            deparagraph=deparagraph,
            mathjax=mathjax,
            smart=smart,
            extra_args=extra_args,
        )
        return output_text

    def format_short_title(
        self,
        format="html5",
        deparagraph=True,
        mathjax=False,
        smart=True,
        extra_args=None,
    ):
        """Get the document short title in the specified markup format.

        Parameters
        ----------
        format : `str`, optional
            Output format (such as ``'html5'`` or ``'plain'``).
        deparagraph : `bool`, optional
            Remove the paragraph tags from single paragraph content.
        mathjax : `bool`, optional
            Allow pandoc to use MathJax math markup.
        smart : `True`, optional
            Allow pandoc to create "smart" unicode punctuation.
        extra_args : `list`, optional
            Additional command line flags to pass to Pandoc. See
            `lsstprojectmeta.pandoc.convert.convert_text`.

        Returns
        -------
        output_text : `str`
            Converted content or `None` if the short title is not available in
            the document.
        """
        if self.short_title is None:
            return None

        output_text = convert_lsstdoc_tex(
            self.short_title,
            "html5",
            deparagraph=deparagraph,
            mathjax=mathjax,
            smart=smart,
            extra_args=extra_args,
        )
        return output_text

    def format_abstract(
        self,
        format="html5",
        deparagraph=False,
        mathjax=False,
        smart=True,
        extra_args=None,
    ):
        """Get the document abstract in the specified markup format.

        Parameters
        ----------
        format : `str`, optional
            Output format (such as ``'html5'`` or ``'plain'``).
        deparagraph : `bool`, optional
            Remove the paragraph tags from single paragraph content.
        mathjax : `bool`, optional
            Allow pandoc to use MathJax math markup.
        smart : `True`, optional
            Allow pandoc to create "smart" unicode punctuation.
        extra_args : `list`, optional
            Additional command line flags to pass to Pandoc. See
            `lsstprojectmeta.pandoc.convert.convert_text`.

        Returns
        -------
        output_text : `str`
            Converted content or `None` if the title is not available in
            the document.
        """
        if self.abstract is None:
            return None

        abstract_latex = self._prep_snippet_for_pandoc(self.abstract)

        output_text = convert_lsstdoc_tex(
            abstract_latex,
            format,
            deparagraph=deparagraph,
            mathjax=mathjax,
            smart=smart,
            extra_args=extra_args,
        )
        return output_text

    def format_authors(
        self,
        format="html5",
        deparagraph=True,
        mathjax=False,
        smart=True,
        extra_args=None,
    ):
        """Get the document authors in the specified markup format.

        Parameters
        ----------
        format : `str`, optional
            Output format (such as ``'html5'`` or ``'plain'``).
        deparagraph : `bool`, optional
            Remove the paragraph tags from single paragraph content.
        mathjax : `bool`, optional
            Allow pandoc to use MathJax math markup.
        smart : `True`, optional
            Allow pandoc to create "smart" unicode punctuation.
        extra_args : `list`, optional
            Additional command line flags to pass to Pandoc. See
            `lsstprojectmeta.pandoc.convert.convert_text`.

        Returns
        -------
        output_text : `list` of `str`
            Sequence of author names in the specified output markup format.
        """
        formatted_authors = []
        for latex_author in self.authors:
            formatted_author = convert_lsstdoc_tex(
                latex_author,
                format,
                deparagraph=deparagraph,
                mathjax=mathjax,
                smart=smart,
                extra_args=extra_args,
            )
            # removes Pandoc's terminal newlines
            formatted_author = formatted_author.strip()
            formatted_authors.append(formatted_author)
        return formatted_authors

    def _parse_documentclass(self):
        """Parse documentclass options.

        Sets the the ``_document_options`` attribute.
        """
        command = LatexCommand(
            "documentclass",
            {"name": "options", "required": False, "bracket": "["},
            {"name": "class_name", "required": True, "bracket": "{"},
        )
        try:
            parsed = next(command.parse(self._tex))
        except StopIteration:
            self._logger.warning("lsstdoc has no documentclass")
            self._document_options = []

        try:
            content = parsed["options"]
            self._document_options = [
                opt.strip() for opt in content.split(",")
            ]
        except KeyError:
            self._logger.warning("lsstdoc has no documentclass options")
            self._document_options = []

    def _parse_title(self):
        """Parse the title from TeX source.

        Sets these attributes:

        - ``_title``
        - ``_short_title``
        """
        command = LatexCommand(
            "title",
            {"name": "short_title", "required": False, "bracket": "["},
            {"name": "long_title", "required": True, "bracket": "{"},
        )
        try:
            parsed = next(command.parse(self._tex))
        except StopIteration:
            self._logger.warning("lsstdoc has no title")
            self._title = None
            self._short_title = None

        self._title = parsed["long_title"]

        try:
            self._short_title = parsed["short_title"]
        except KeyError:
            self._logger.warning("lsstdoc has no short title")
            self._short_title = None

    def _parse_doc_ref(self):
        """Parse the document handle.

        Sets the ``_series``, ``_serial``, and ``_handle`` attributes.
        """
        command = LatexCommand(
            "setDocRef", {"name": "handle", "required": True, "bracket": "{"}
        )
        try:
            parsed = next(command.parse(self._tex))
        except StopIteration:
            self._logger.warning("lsstdoc has no setDocRef")
            self._handle = None
            self._series = None
            self._serial = None
            return

        self._handle = parsed["handle"]
        try:
            self._series, self._serial = self._handle.split("-", 1)
        except ValueError:
            self._logger.warning(
                "lsstdoc handle cannot be parsed into "
                "series and serial: %r",
                self._handle,
            )
            self._series = None
            self._serial = None

    def _parse_author(self):
        r"""Parse the author from TeX source.

        Sets the ``_authors`` attribute.

        Goal is to parse::

           \author{
           A.~Author,
           B.~Author,
           and
           C.~Author}

        Into::

           ['A. Author', 'B. Author', 'C. Author']
        """
        command = LatexCommand(
            "author", {"name": "authors", "required": True, "bracket": "{"}
        )
        try:
            parsed = next(command.parse(self._tex))
        except StopIteration:
            self._logger.warning("lsstdoc has no author")
            self._authors = []
            return

        try:
            content = parsed["authors"]
        except KeyError:
            self._logger.warning("lsstdoc has no author")
            self._authors = []
            return

        # Clean content
        content = content.replace("\n", " ")
        content = content.replace("~", " ")
        content = content.strip()

        # Split content into list of individual authors
        authors = []
        for part in content.split(","):
            part = part.strip()
            for split_part in part.split("and "):
                split_part = split_part.strip()
                if len(split_part) > 0:
                    authors.append(split_part)
        self._authors = authors

    def _parse_abstract(self):
        """Parse the abstract from the TeX source.

        Sets the ``_abstract`` attribute.
        """
        command = LatexCommand(
            "setDocAbstract",
            {"name": "abstract", "required": True, "bracket": "{"},
        )
        try:
            parsed = next(command.parse(self._tex))
        except StopIteration:
            self._logger.warning("lsstdoc has no abstract")
            self._abstract = None
            return

        try:
            content = parsed["abstract"]
        except KeyError:
            self._logger.warning("lsstdoc has no abstract")
            self._abstract = None
            return

        content = content.strip()
        self._abstract = content

    def _prep_snippet_for_pandoc(self, latex_text):
        """Process a LaTeX snippet of content for better transformation
        with pandoc.

        Currently runs the CitationLinker to convert BibTeX citations to
        href links.
        """
        replace_cite = CitationLinker(self.bib_db)
        latex_text = replace_cite(latex_text)
        return latex_text

    def _load_bib_db(self):
        r"""Load the BibTeX bibliography referenced by the document.

        This method triggered by the `bib_db` attribute and populates the
        `_bib_db` private attribute.

        The ``\bibliography`` command is parsed to identify the bibliographies
        referenced by the document.
        """
        # Get the names of custom bibtex files by parsing the
        # \bibliography command and filtering out the default lsstdoc
        # bibliographies.
        command = LatexCommand(
            "bibliography",
            {"name": "bib_names", "required": True, "bracket": "{"},
        )
        try:
            parsed = next(command.parse(self._tex))
            bib_names = [n.strip() for n in parsed["bib_names"].split(",")]
        except StopIteration:
            self._logger.warning("lsstdoc has no bibliography command")
            bib_names = []
        custom_bib_names = [
            n for n in bib_names if n not in KNOWN_LSSTTEXMF_BIB_NAMES
        ]

        # Read custom bibliographies.
        custom_bibs = []
        for custom_bib_name in custom_bib_names:
            custom_bib_path = os.path.join(
                os.path.join(self._root_dir), custom_bib_name + ".bib"
            )
            if not os.path.exists(custom_bib_path):
                self._logger.warning(
                    "Could not find bibliography %r", custom_bib_path
                )
                continue
            with open(custom_bib_path, "r") as file_handle:
                custom_bibs.append(file_handle.read())
        if len(custom_bibs) > 0:
            custom_bibtex = "\n\n".join(custom_bibs)
        else:
            custom_bibtex = None

        # Get the combined pybtex bibliography
        db = get_bibliography(bibtex=custom_bibtex)

        self._bib_db = db

    def _parse_revision_date(self):
        r"""Parse the ``\date`` command, falling back to getting the
        most recent Git commit date and the current datetime.

        Result is available from the `revision_datetime` attribute.
        """
        doc_datetime = None

        # First try to parse the \date command in the latex.
        # \date is ignored for draft documents.
        if not self.is_draft:
            date_command = LatexCommand(
                "date", {"name": "content", "required": True, "bracket": "{"}
            )
            try:
                parsed = next(date_command.parse(self._tex))
                command_content = parsed["content"].strip()
            except StopIteration:
                command_content = None
                self._logger.warning("lsstdoc has no date command")

            # Try to parse a date from the \date command
            if command_content is not None and command_content != r"\today":
                try:
                    doc_datetime = datetime.datetime.strptime(
                        command_content, "%Y-%m-%d"
                    )
                    # Assume LSST project time (Pacific)
                    project_tz = timezone("US/Pacific")
                    localized_datetime = project_tz.localize(doc_datetime)
                    # Normalize to UTC
                    doc_datetime = localized_datetime.astimezone(pytz.utc)

                    self._revision_datetime_source = "tex"
                except ValueError:
                    self._logger.warning(
                        "Could not parse a datetime from "
                        "lsstdoc date command: %r",
                        command_content,
                    )

        # Fallback to getting the datetime from Git
        if doc_datetime is None:
            content_extensions = ("tex", "bib", "pdf", "png", "jpg")
            try:
                doc_datetime = get_content_commit_date(
                    content_extensions, root_dir=self._root_dir
                )
                self._revision_datetime_source = "git"
            except RuntimeError:
                self._logger.warning(
                    "Could not get a datetime from the Git "
                    "repository at %r",
                    self._root_dir,
                )

        # Final fallback to the current datetime
        if doc_datetime is None:
            doc_datetime = pytz.utc.localize(datetime.datetime.now())
            self._revision_datetime_source = "now"

        self._datetime = doc_datetime

    def build_jsonld(
        self,
        url=None,
        code_url=None,
        ci_url=None,
        readme_url=None,
        license_id=None,
    ):
        """Create a JSON-LD representation of this LSST LaTeX document.

        Parameters
        ----------
        url : `str`, optional
            URL where this document is published to the web. Prefer
            the LSST the Docs URL if possible.
            Example: ``'https://ldm-151.lsst.io'``.
        code_url : `str`, optional
            Path the the document's repository, typically on GitHub.
            Example: ``'https://github.com/lsst/LDM-151'``.
        ci_url : `str`, optional
            Path to the continuous integration service dashboard for this
            document's repository.
            Example: ``'https://travis-ci.org/lsst/LDM-151'``.
        readme_url : `str`, optional
            URL to the document repository's README file. Example:
            ``https://raw.githubusercontent.com/lsst/LDM-151/master/README.rst``.
        license_id : `str`, optional
            License identifier, if known. The identifier should be from the
            listing at https://spdx.org/licenses/. Example: ``CC-BY-4.0``.

        Returns
        -------
        jsonld : `dict`
            JSON-LD-formatted dictionary.
        """
        jsonld = {
            "@context": [
                "https://raw.githubusercontent.com/codemeta/codemeta/2.0-rc/"
                "codemeta.jsonld",
                "http://schema.org",
            ],
            "@type": ["Report", "SoftwareSourceCode"],
            "language": "TeX",
            "reportNumber": self.handle,
            "name": self.plain_title,
            "description": self.plain_abstract,
            "author": [
                {"@type": "Person", "name": author_name}
                for author_name in self.plain_authors
            ],
            # This is a datetime.datetime; not a string. If writing to a file,
            # Need to convert this to a ISO 8601 string.
            "dateModified": self.revision_datetime,
        }

        try:
            jsonld["articleBody"] = self.plain_content
            jsonld["fileFormat"] = "text/plain"  # MIME type of articleBody
        except RuntimeError:
            # raised by pypandoc when it can't convert the tex document
            self._logger.exception(
                "Could not convert latex body to plain "
                "text for articleBody."
            )
            self._logger.warning("Falling back to tex source for articleBody")
            jsonld["articleBody"] = self._tex
            jsonld["fileFormat"] = "text/plain"  # no mimetype for LaTeX?

        if url is not None:
            jsonld["@id"] = url
            jsonld["url"] = url
        else:
            # Fallback to using the document handle as the ID. This isn't
            # entirely ideal from a linked data perspective.
            jsonld["@id"] = self.handle

        if code_url is not None:
            jsonld["codeRepository"] = code_url

        if ci_url is not None:
            jsonld["contIntegration"] = ci_url

        if readme_url is not None:
            jsonld["readme"] = readme_url

        if license_id is not None:
            jsonld["license_id"] = None

        return jsonld
