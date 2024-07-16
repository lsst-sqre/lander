"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def temp_cwd(tmp_path: Path) -> Generator[Path, None, None]:
    """Run the test from a temporary directory."""
    current_dir = Path.cwd()

    os.chdir(tmp_path)
    yield tmp_path

    os.chdir(current_dir)


@pytest.fixture
def temp_article_dir(temp_cwd: Path) -> Path:
    """Run the test from a temporary directory containing the
    "tests/data/article" dataset.
    """
    article_source_dir = Path(__file__).parent / "data" / "article"
    for source_path in article_source_dir.iterdir():
        relative_path = source_path.relative_to(article_source_dir)
        dest_path = Path.cwd().joinpath(relative_path)
        if source_path.is_dir():
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)

    return temp_cwd


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()
