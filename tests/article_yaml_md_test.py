"""Test CLI and YAML metadata integration using the tests/data/article-yaml-md
dataset.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from lander.cli import app

if TYPE_CHECKING:
    from typer.testing import CliRunner


def test_build(runner: CliRunner, temp_cwd: Path) -> None:
    workdir = Path("article")
    shutil.copytree(
        Path(__file__).parent.joinpath("data/article-yaml-md"), "article"
    )
    source_path = workdir / "article.tex"
    pdf_path = workdir / "article.pdf"
    result = runner.invoke(
        app,
        [
            "build",
            "--source",
            str(source_path),
            "--pdf",
            str(pdf_path),
            "--parser",
            "article",
            "--theme",
            "minimalist",
        ],
    )
    print(result.stdout)

    assert result.exit_code == 0

    metadata_output = Path("_build/metadata.json")
    metadata = json.loads(metadata_output.read_text())
    print(json.dumps(metadata, indent=2))
    # From "canonical_url" field in lander.yaml
    assert (
        metadata["canonical_url"]
        == "https://example.com/example-article-document/"
    )
    # From "metadata.license_identifier" field in lander.yaml
    assert metadata["license_identifier"] == "MIT"
