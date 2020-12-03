"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner


@pytest.fixture(scope="function")
def temp_cwd(tmp_path: Path) -> Generator[Path, None, None]:
    """Run the test from a temporary directory."""
    current_dir = Path.cwd()

    os.chdir(tmp_path)
    yield tmp_path

    os.chdir(current_dir)


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()
