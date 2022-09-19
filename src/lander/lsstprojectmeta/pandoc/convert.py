"""Pandoc conversion helper functions.
"""

__all__ = ["convert_text", "ensure_pandoc"]

import functools
import logging

import pypandoc

from ..tex.lsstmacros import LSSTDOC_MACROS


def ensure_pandoc(func):
    """Decorate a function that uses pypandoc to ensure that pandoc is
    installed if necessary.
    """
    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    def _install_and_run(*args, **kwargs):
        try:
            # First try to run pypandoc function
            result = func(*args, **kwargs)
        except OSError:
            # Install pandoc and retry
            message = "pandoc needed but not found. Now installing it for you."
            logger.warning(message)
            # This version of pandoc is known to be compatible with both
            # pypandoc.download_pandoc and the functionality that
            # lsstprojectmeta needs. Travis CI tests are useful for ensuring
            # download_pandoc works.
            pypandoc.download_pandoc()
            logger.debug("pandoc download complete")

            result = func(*args, **kwargs)

        return result

    return _install_and_run


@ensure_pandoc
def convert_text(
    content,
    from_fmt,
    to_fmt,
    deparagraph=False,
    mathjax=False,
    smart=False,
    extra_args=None,
):
    """Convert text from one markup format to another using pandoc.

    This function is a thin wrapper around `pypandoc.convert_text`.

    Parameters
    ----------
    content : `str`
        Original content.

    from_fmt : `str`
        Format of the original ``content``. Format identifier must be one of
        those known by Pandoc. See https://pandoc.org/MANUAL.html for details.

    to_fmt : `str`
        Output format for the content.

    deparagraph : `bool`, optional
        If `True`, then the
        `lsstprojectmeta.pandoc.filters.deparagraph.deparagraph` filter is
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

    smart : `bool`, optional
        If `True` (default) then ascii characters will be converted to unicode
        characters like smart quotes and em dashes.

    extra_args : `list`, optional
        Sequence of Pandoc arguments command line arguments (such as
        ``'--normalize'``). The ``deparagraph``, ``mathjax``, and ``smart``
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

    # No longer works in pandoc 2
    # if smart:
    #     extra_args.append('--smart')

    if deparagraph:
        extra_args.append("--filter=lsstprojectmeta-deparagraph")

    extra_args.append("--wrap=none")

    # de-dupe extra args
    extra_args = set(extra_args)

    logger.debug(
        "Running pandoc from %s to %s with extra_args %s",
        from_fmt,
        to_fmt,
        extra_args,
    )

    output = pypandoc.convert_text(
        content, to_fmt, format=from_fmt, extra_args=extra_args
    )
    return output


def convert_lsstdoc_tex(
    content,
    to_fmt,
    deparagraph=False,
    mathjax=False,
    smart=True,
    extra_args=None,
):
    """Convert lsstdoc-class LaTeX to another markup format.

    This function is a thin wrapper around `convert_text` that automatically
    includes common lsstdoc LaTeX macros.

    Parameters
    ----------
    content : `str`
        Original content.

    to_fmt : `str`
        Output format for the content (see https://pandoc.org/MANUAL.html).
        For example, 'html5'.

    deparagraph : `bool`, optional
        If `True`, then the
        `lsstprojectmeta.pandoc.filters.deparagraph.deparagraph` filter is
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

    smart : `bool`, optional
        If `True` (default) then ascii characters will be converted to unicode
        characters like smart quotes and em dashes.

    extra_args : `list`, optional
        Sequence of Pandoc arguments command line arguments (such as
        ``'--normalize'``). The ``deparagraph``, ``mathjax``, and ``smart``
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
    augmented_content = "\n".join((LSSTDOC_MACROS, content))
    return convert_text(
        augmented_content,
        "latex",
        to_fmt,
        deparagraph=deparagraph,
        mathjax=mathjax,
        smart=smart,
        extra_args=extra_args,
    )
