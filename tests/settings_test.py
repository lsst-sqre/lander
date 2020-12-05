"""Tests for the lander.settings module."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from lander.settings import BuildSettings


def test_load_from_cwd(temp_cwd: Path) -> None:
    """Test where a lander.yaml file is detected in the current working
    directory to the source file.
    """
    settings_data = {
        "output_dir": "_build",
        "source_path": "doc.tex",
        "pdf_path": "doc.pdf",
    }
    settings_path = temp_cwd / "lander.yaml"
    settings_path.write_text(yaml.dump(settings_data))

    settings = BuildSettings.load(parser="article", template="minimalist")
    assert settings.output_dir == Path("_build")
    assert settings.source_path == Path("doc.tex")
    assert settings.pdf_path == Path("doc.pdf")
    assert settings.parser == "article"
    assert settings.template == "minimalist"


def test_load_from_source_directory(temp_cwd: Path) -> None:
    """Test where a lander.yaml file is detected next to the source file."""
    source_path = Path("mysubdir") / "source.tex"
    settings_data = {
        "output_dir": "_build",
        "parser": "article",
        "template": "minimalist",
    }
    source_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path = source_path.parent / "lander.yaml"
    settings_path.write_text(yaml.dump(settings_data))

    settings = BuildSettings.load(
        pdf_path=source_path.parent / "document.pdf", source_path=source_path,
    )
    assert settings.output_dir == Path("_build")
    assert settings.source_path == Path("mysubdir/source.tex")
    assert settings.pdf_path == Path("mysubdir/document.pdf")
    assert settings.parser == "article"
    assert settings.template == "minimalist"


def test_load_from_cli_only(temp_cwd: Path) -> None:
    """Test where configurations are only set from load classmethod parameters.
    """
    settings = BuildSettings.load(
        pdf_path=Path("document.pdf"),
        source_path=Path("document.tex"),
        parser="article",
        template="minimalist",
    )
    assert settings.output_dir == Path("_build")  # a default
    assert settings.source_path == Path("document.tex")
    assert settings.pdf_path == Path("document.pdf")
    assert settings.parser == "article"
    assert settings.template == "minimalist"


def test_parser_plugin_validation() -> None:
    """Test validation of the parser plugin name."""
    with pytest.raises(ValidationError):
        BuildSettings(
            pdf_path=Path("document.pdf"),
            source_path=Path("document.tex"),
            parser="does-not-exist",
            template="minimalist",
        )


def test_template_plugin_validation() -> None:
    """Test validation of the template plugin name."""
    with pytest.raises(ValidationError):
        BuildSettings(
            pdf_path=Path("document.pdf"),
            source_path=Path("document.tex"),
            parser="article",
            template="does-not-exist",
        )
