"""Lander command line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from lander.ext.parser.pandoc import print_pandoc_version
from lander.plugins import parsers, themes
from lander.settings import BuildSettings

__all__ = ["app"]

app = typer.Typer()

# typer doesn't work with modern union syntax for optional types,
# hence the use of UP007 to suppress the error for now.


@app.command()
def build(
    output: Annotated[
        Optional[Path],  # noqa: UP007
        typer.Option(help="Directory for the built site"),
    ] = None,
    source: Annotated[
        Optional[Path],  # noqa: UP007
        typer.Option(
            help="Source file for metadata (usually the root tex file)."
        ),
    ] = None,
    pdf: Annotated[
        Optional[Path],  # noqa: UP007
        typer.Option(
            help="Path to the PDF file to display on the landing page."
        ),
    ] = None,
    parser: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(help="Metadata parsing plugin"),
    ] = None,
    theme: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(help="Theme plugin."),
    ] = None,
    canonical_url: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            "--url", help="Canonical URL where the landing page is hosted."
        ),
    ] = None,
) -> None:
    print_pandoc_version()

    settings = BuildSettings.load(
        output_dir=output,
        source_path=source,
        pdf=pdf,
        parser=parser,
        theme=theme,
        canonical_url=canonical_url,
    )

    # Load plugins and build the site
    parser_plugin = parsers[settings.parser](settings=settings)
    theme_plugin = themes[settings.theme](
        metadata=parser_plugin.metadata, settings=settings
    )
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
