"""Test the CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lander.cli import app

if TYPE_CHECKING:
    from pathlib import Path
    from typer.testing import CliRunner


def test_build(runner: CliRunner, temp_cwd: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--source",
            "doc.tex",
            "--pdf",
            "doc.pdf",
            "--parser",
            "myparser",
            "--template",
            "mytemplate",
        ],
    )
    assert result.exit_code == 0
    assert "Running lander build" in result.stdout
