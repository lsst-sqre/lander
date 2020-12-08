"""Jinja2 filters."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    import datetime

__all__ = ["filter_simple_date", "filter_paragraphify"]


def filter_simple_date(value: datetime.datetime) -> str:
    """Filter a `datetime.datetime` into a 'YYYY-MM-DD' string."""
    return value.strftime("%Y-%m-%d")


def filter_paragraphify(value: str) -> str:
    """Convert text into one or more paragraphs, including <p> tags.

    Based on https://gist.github.com/cemk/1324543
    """
    value = re.sub(r"\r\n|\r|\n", "\n", value)  # Normalize newlines
    paras = re.split("\n{2,}", value)
    paras = ["<p>{0}</p>".format(p) for p in paras if len(p) > 0]
    return jinja2.Markup("\n\n".join(paras))
