"""Tests for the lander.settings module."""

from __future__ import annotations

from pathlib import Path

import yaml

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

    settings = BuildSettings.load(
        parser="parser_name", template="template_name"
    )
    assert settings.output_dir == Path("_build")
    assert settings.source_path == Path("doc.tex")
    assert settings.pdf_path == Path("doc.pdf")
    assert settings.parser == "parser_name"
    assert settings.template == "template_name"


def test_load_from_source_directory(temp_cwd: Path) -> None:
    """Test where a lander.yaml file is detected next to the source file."""
    source_path = Path("mysubdir") / "source.tex"
    settings_data = {
        "output_dir": "_build",
        "parser": "parser_name",
        "template": "template_name",
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
    assert settings.parser == "parser_name"
    assert settings.template == "template_name"


def test_load_from_cli_only(temp_cwd: Path) -> None:
    """Test where configurations are only set from load classmethod parameters.
    """
    settings = BuildSettings.load(
        pdf_path=Path("document.pdf"),
        source_path=Path("document.tex"),
        parser="parser_name",
        template="template_name",
    )
    assert settings.output_dir == Path("_build")  # a default
    assert settings.source_path == Path("document.tex")
    assert settings.pdf_path == Path("document.pdf")
    assert settings.parser == "parser_name"
    assert settings.template == "template_name"
