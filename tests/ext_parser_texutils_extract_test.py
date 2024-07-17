"""Tests for lander.ext.parser.texutils.extract module."""

from __future__ import annotations

from lander.ext.parser.texutils.extract import (
    get_def_macros,
    get_newcommand_macros,
)


def test_get_def_macros() -> None:
    sample = r"\def \name {content}"
    macros = get_def_macros(sample)

    assert r"\name" in macros
    assert macros[r"\name"] == "content"


multiline_sample = r"""
\documentclass[DM,STP,toc]{lsstdoc}
%set the WP number or product here for the requirements
"\def\product{Data Management}
"\def\cycle{S17}
"""


def test_get_def_macros_ldm_503() -> None:
    macros = get_def_macros(multiline_sample)

    assert macros[r"\product"] == "Data Management"
    assert macros[r"\cycle"] == "S17"


def test_get_newcommand_macros() -> None:
    sample = r"\newcommand {\name} {content}"
    macros = get_newcommand_macros(sample)
    assert macros[r"\name"] == "content"

    sample = r"\newcommand { \name } {content}"
    macros = get_newcommand_macros(sample)
    assert macros[r"\name"] == "content"

    sample = r"\newcommand{\name}{content}"
    macros = get_newcommand_macros(sample)
    assert macros[r"\name"] == "content"
