"""Tests for the lander.settings module."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from lander.settings import BuildSettings, DownloadableFile


def test_load_from_cwd(temp_article_dir: Path) -> None:
    """Test where a lander.yaml file is detected in the current working
    directory to the source file.
    """
    settings_data = {
        "output_dir": "_build",
        "source_path": "article.tex",
        "pdf": "article.pdf",
    }
    settings_path = Path("lander.yaml")
    settings_path.write_text(yaml.dump(settings_data))

    settings = BuildSettings.load(parser="article", theme="minimalist")
    assert settings.output_dir == Path("_build")
    assert settings.source_path == Path("article.tex")
    assert settings.pdf.file_path == Path("article.pdf")
    assert settings.parser == "article"
    assert settings.theme == "minimalist"


def test_load_from_source_directory(temp_cwd: Path) -> None:
    """Test where a lander.yaml file is detected next to the source file."""
    root_path = temp_cwd.joinpath("mysubdir")
    root_path.mkdir(parents=True, exist_ok=True)
    article_source_dir = Path(__file__).parent / "data" / "article"
    for source_path in article_source_dir.iterdir():
        relative_path = source_path.relative_to(article_source_dir)
        dest_path = root_path.joinpath(relative_path)
        if source_path.is_dir():
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)

    source_path = root_path / "article.tex"
    pdf_path = root_path / "article.pdf"
    settings_data = {
        "output_dir": "_build",
        "parser": "article",
        "theme": "minimalist",
    }
    source_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path = source_path.parent / "lander.yaml"
    settings_path.write_text(yaml.dump(settings_data))

    settings = BuildSettings.load(pdf=pdf_path, source_path=source_path,)
    assert settings.output_dir == Path("_build")
    assert settings.source_path == source_path
    assert settings.pdf.file_path == pdf_path
    assert settings.parser == "article"
    assert settings.theme == "minimalist"


def test_load_from_cli_only(temp_article_dir: Path) -> None:
    """Test where configurations are only set from load classmethod parameters.
    """
    settings = BuildSettings.load(
        pdf=Path("article.pdf"),
        source_path=Path("article.tex"),
        parser="article",
        theme="minimalist",
    )
    assert settings.output_dir == Path("_build")  # a default
    assert settings.source_path == Path("article.tex")
    assert settings.pdf.file_path == Path("article.pdf")
    assert settings.parser == "article"
    assert settings.theme == "minimalist"


def test_parser_plugin_validation(temp_article_dir: Path) -> None:
    """Test validation of the parser plugin name."""
    with pytest.raises(ValidationError):
        BuildSettings(
            pdf=DownloadableFile.load(Path("article.pdf")),
            source_path=Path("article.tex"),
            parser="does-not-exist",
            theme="minimalist",
        )


def test_theme_plugin_validation(temp_article_dir: Path) -> None:
    """Test validation of the theme plugin name."""
    with pytest.raises(ValidationError):
        BuildSettings(
            pdf=DownloadableFile.load(Path("article.pdf")),
            source_path=Path("article.tex"),
            parser="article",
            theme="does-not-exist",
        )
