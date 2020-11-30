"""Pandoc filter to remove the outer Para wrapper and replace it with a
Plain wrapper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from panflute import Para, Plain, toJSONFilter

__all__ = ["main", "deparagraph"]

if TYPE_CHECKING:
    from panflute import Element, Doc


def deparagraph(element: Element, doc: Doc) -> Element:
    """Panflute filter function that converts content wrapped in a Para to
    Plain.

    Use this filter with pandoc as::

        pandoc [..] --filter=lander-deparagraph

    Only lone paragraphs are affected. Para elements with siblings (like a
    second Para) are left unaffected.

    This filter is useful for processing strings like titles or author names so
    that the output isn't wrapped in paragraph tags. For example, without
    this filter, pandoc converts a string ``"The title"`` to
    ``<p>The title</p>`` in HTML. These ``<p>`` tags aren't useful if you
    intend to put the title text in ``<h1>`` tags using your own templating
    system.
    """
    if isinstance(element, Para):
        # Check if siblings exist; don't process the paragraph in that case.
        if element.next is not None:
            return element
        elif element.prev is not None:
            return element

        # Remove the Para wrapper from the lone paragraph.
        # `Plain` is a container that isn't rendered as a paragraph.
        return Plain(*element.content)


def main() -> None:
    """Setuptools entrypoint for the deparagraph CLI.

    Use this filter as::

        pandoc [..] --filter=lander-deparagraph
    """
    toJSONFilter(deparagraph)
