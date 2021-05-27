"""Pandoc version compatibility checking."""

from __future__ import annotations

import pypandoc

from lander.ext.parser.pandoc._convert import ensure_pandoc


@ensure_pandoc
def print_pandoc_version() -> None:
    version = pypandoc.get_pandoc_version()
    print(f"Using pandoc {version}")
