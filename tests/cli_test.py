"""Test the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from lander.cli import app

if TYPE_CHECKING:
    from typer.testing import CliRunner


def test_build(runner: CliRunner, temp_cwd: Path) -> None:
    source_path = Path(__file__).parent.joinpath("data/article/article.tex")
    pdf_path = Path(__file__).parent.joinpath("data/article/article.pdf")
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
            "--url",
            "https://example.com/my-paper/",
        ],
    )
    print(result.stdout)

    assert result.exit_code == 0
    assert "Generated landing page" in result.stdout

    html_output_path = Path("_build/index.html")
    assert html_output_path.exists()

    pdf_path = Path("_build/article.pdf")
    assert pdf_path.exists()

    soup = BeautifulSoup(html_output_path.read_text(), "html.parser")
    assert soup.title.string == "Example Article Document"
    head = soup.head
    print(head)
    canonical_url = head.find("link", attrs={"rel": "canonical"})
    assert canonical_url.attrs["href"] == "https://example.com/my-paper/"


def test_list_themes(runner: CliRunner) -> None:
    result = runner.invoke(app, ["themes"])
    assert result.exit_code == 0
    assert "Available themes" in result.stdout
    assert "minimalist" in result.stdout


def test_list_parsers(runner: CliRunner) -> None:
    result = runner.invoke(app, ["parsers"])
    assert result.exit_code == 0
    assert "Available parsers" in result.stdout
    assert "article" in result.stdout
