"""Tests for the lsstprojectmeta.tex.normalizer module."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from lander.ext.parser.texutils.normalize import (
    input_include_pattern,
    read_tex_file,
    remove_comments,
    remove_trailing_whitespace,
    replace_macros,
)


def test_remove_comments_abstract() -> None:
    sample = (
        r"\setDocAbstract{%" + "\n"
        " The LSST Data Management System (DMS) is a set of services\n"
        " employing a variety of software components running on\n"
        " computational and networking infrastructure that combine to\n"
        " deliver science data products to the observatory's users and\n"
        " support observatory operations.  This document describes the\n"
        " components, their service instances, and their deployment\n"
        " environments as well as the interfaces among them, the rest\n"
        " of the LSST system, and the outside world.\n"
        "}"
    )
    expected = (
        r"\setDocAbstract{" + "\n"
        " The LSST Data Management System (DMS) is a set of services\n"
        " employing a variety of software components running on\n"
        " computational and networking infrastructure that combine to\n"
        " deliver science data products to the observatory's users and\n"
        " support observatory operations.  This document describes the\n"
        " components, their service instances, and their deployment\n"
        " environments as well as the interfaces among them, the rest\n"
        " of the LSST system, and the outside world.\n"
        "}"
    )
    assert remove_comments(sample) == expected


def test_escaped_remove_comments() -> None:
    """Test remove_comments where a "%" is escaped."""
    sample = r"The uncertainty is 5\%.  % a comment"
    expected = r"The uncertainty is 5\%.  "
    assert remove_comments(sample) == expected


def test_single_line_remove_comments() -> None:
    sample = "This is content.  % a comment"
    expected = "This is content.  "
    assert remove_comments(sample) == expected


def test_remove_single_line_trailing_whitespace() -> None:
    sample = "This is content.    "
    expected = "This is content."
    assert remove_trailing_whitespace(sample) == expected


def test_multi_line_trailing_whitespace() -> None:
    sample = "First line.    \n" "Second line. "
    expected = "First line.\n" "Second line."
    assert remove_trailing_whitespace(sample) == expected


def test_read_tex_file() -> None:
    project_dir = Path(__file__).parent / "data" / "texinputs"
    root_filepath = project_dir / "LDM-nnn.tex"
    tex_source = read_tex_file(root_filepath)

    # verify that input'd and include'd content is present
    assert re.search(r"\\setDocAbstract", tex_source) is not None
    assert re.search(r"\\section{Introduction}", tex_source) is not None


def test_replace_macros() -> None:
    sample = (
        r"\def \product {Data Management}" + "\n"
        r"\title    [Test Plan]  { \product\ Test Plan}" + "\n"
        r"\setDocAbstract {" + "\n"
        r"This is the  Test Plan for \product.}"
    )

    expected = (
        r"\def Data Management {Data Management}" + "\n"
        r"\title    [Test Plan]  { Data Management Test Plan}" + "\n"
        r"\setDocAbstract {" + "\n"
        r"This is the  Test Plan for Data Management.}"
    )

    macros = {r"\product": "Data Management"}
    tex_source = replace_macros(sample, macros)
    assert re.search(r"\\product", sample) is not None  # sanity check
    assert re.search(r"\\product", tex_source) is None
    assert tex_source == expected


@pytest.mark.parametrize(
    "sample,expected",
    [
        (r"\input{file.tex}", "file.tex"),
        (r"\input{dirname/file.tex}", "dirname/file.tex"),
        (r"\input {file}%", "file"),
        (r"\input file%", "file"),
        (r"\input file" + "\n", "file"),
        (r"\input file " + "\n", "file"),
        (r"\include{file.tex}", "file.tex"),
        (r"\include{dirname/file.tex}", "dirname/file.tex"),
        (r"\include {file}%", "file"),
        (r"\include file%", "file"),
        (r"\include file" + "\n", "file"),
        (r"\include file" + " \n", "file"),
    ],
)
def test_input_include_pattern(sample: str, expected: str) -> None:
    match = re.search(input_include_pattern, sample)
    assert match is not None
    assert match.group("filename") == expected


def test_non_inputs() -> None:
    r"""Test for patterns like ``\inputData{XYZ}`` that have in the past been
    detected as an ``\input`` command.
    """
    sample = r"\newcommand{\inputData}[1]{\texttt{#1}}"
    match = re.search(input_include_pattern, sample)
    assert match is None
