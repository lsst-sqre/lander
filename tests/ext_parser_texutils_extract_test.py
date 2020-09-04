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


def test_get_def_macros_LDM_503() -> None:
    sample = (
        r"\documentclass[DM,STP,toc]{lsstdoc}" + "\n"
        "%set the WP number or product here for the requirements\n"
        r"\def\product{Data Management}" + "\n"
        r"\def\cycle{S17}" + "\n"
    )
    macros = get_def_macros(sample)

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
