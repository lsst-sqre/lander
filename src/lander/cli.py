from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from lander.plugins import parsers, themes
from lander.settings import BuildSettings

__all__ = ["app"]

app = typer.Typer()


@app.command()
def build(
    output: Optional[Path] = typer.Option(
        None, help="Directory for the built site"
    ),
    source: Optional[Path] = typer.Option(
        None, help="Source file for metadata (usually the root tex file)."
    ),
    pdf: Optional[Path] = typer.Option(
        None, help="Path to the PDF file to display on the landing page."
    ),
    parser: Optional[str] = typer.Option(None, help="Metadata parsing plugin"),
    theme: Optional[str] = typer.Option(None, help="Theme plugin."),
    canonical_url: Optional[str] = typer.Option(
        None, "--url", help="Canonical URL where the landing page is hosted."
    ),
) -> None:
    settings = BuildSettings.load(
        output_dir=output,
        source_path=source,
        pdf=pdf,
        parser=parser,
        theme=theme,
        canonical_url=canonical_url,
    )

    # Load plugins
    Parser = parsers[settings.parser]
    Theme = themes[settings.theme]

    # Run the document parser
    parser_plugin = Parser(settings.source_path)
    theme_plugin = Theme(metadata=parser_plugin.metadata, settings=settings)
    theme_plugin.build_site()

    print(f"Generated landing page in: {settings.output_dir}")


@app.command("themes")
def list_themes() -> None:
    print("Available themes:\n")
    print(themes.names)


@app.command("parsers")
def list_parsers() -> None:
    print("Available parsers:\n")
    print(parsers.names)
