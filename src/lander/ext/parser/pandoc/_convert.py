"""Pandoc-based markup conversion APIs."""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, List, Optional, TypeVar

import pypandoc

__all__ = ["convert_text", "ensure_pandoc"]

F = TypeVar("F", bound=Callable[..., Any])


def ensure_pandoc(func: F) -> Callable[..., Any]:
    """Decorate a function that uses pypandoc to ensure that pandoc is
    installed if necessary.
    """
    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    def _install_and_run(*args: Any, **kwargs: Any) -> Any:
        try:
            # First try to run pypandoc function
            result = func(*args, **kwargs)
        except OSError:
            # Install pandoc and retry
            message = "Pandoc is required but not found."
            logger.warning(message)

            result = func(*args, **kwargs)

        return result

    return _install_and_run


@ensure_pandoc
def convert_text(
    *,
    content: str,
    source_fmt: str,
    output_fmt: str,
    deparagraph: bool = False,
    mathjax: bool = False,
    extra_args: Optional[List[str]] = None,
) -> str:
    """Convert text from one markup format to another using pandoc.

    This function is a thin wrapper around `pypandoc.convert_text`.

    Parameters
    ----------
    content : `str`
        Original content.

    source_fmt : `str`
        Format of the original ``content``. Format identifier must be one of
        those known by Pandoc. See https://pandoc.org/MANUAL.html for details.

    output_fmt : `str`
        Output format for the content.

    deparagraph : `bool`, optional
        If `True`, then the
        `lander.parse.pandoc.filters.deparagraph.deparagraph` filter is
        used to remove paragraph (``<p>``, for example) tags around a single
        paragraph of content. That filter does not affect content that
        consists of multiple blocks (several paragraphs, or lists, for
        example). Default is `False`.

        For example, **without** this filter Pandoc will convert
        the string ``"Title text"`` to ``"<p>Title text</p>"`` in HTML. The
        paragraph tags aren't useful if you intend to wrap the converted
        content in different tags, like ``<h1>``, using your own templating
        system.

        **With** this filter, Pandoc will convert the string ``"Title text"``
        to ``"Title text"`` in HTML.

    mathjax : `bool`, optional
        If `True` then Pandoc will markup output content to work with MathJax.
        Default is False.

    extra_args : `list`, optional
        Sequence of Pandoc arguments command line arguments (such as
        ``'--normalize'``). The ``deparagraph``, and ``mathjax``
        arguments are convenience arguments that are equivalent to items
        in ``extra_args``.

    Returns
    -------
    output : `str`
        Content in the output (``to_fmt``) format.

    Notes
    -----
    This function will automatically install Pandoc if it is not available.
    See `ensure_pandoc`.
    """
    logger = logging.getLogger(__name__)

    if extra_args is not None:
        extra_args = list(extra_args)
    else:
        extra_args = []

    if mathjax:
        extra_args.append("--mathjax")

    if deparagraph:
        extra_args.append("--filter=lander-deparagraph")

    extra_args.append("--wrap=none")

    # de-dupe extra args
    extra_args = list(set(extra_args))

    logger.debug(
        "Running pandoc from %s to %s with extra_args %s",
        source_fmt,
        output_fmt,
        extra_args,
    )

    output = pypandoc.convert_text(
        content, output_fmt, format=source_fmt, extra_args=extra_args
    )
    return output
