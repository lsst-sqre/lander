from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from lander.plugins import parsers, templates
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
    template: Optional[str] = typer.Option(None, help="Template plugin."),
) -> None:
    settings = BuildSettings.load(
        output_dir=output,
        source_path=source,
        pdf_path=pdf,
        parser=parser,
        template=template,
    )

    # Load plugins
    Parser = parsers[settings.parser]
    Template = templates[settings.template]

    # Run the document parser
    parser_plugin = Parser(settings.source_path)
    template_plugin = Template(
        metadata=parser_plugin.metadata, settings=settings
    )
    template_plugin.build_site()

    print(f"Generated landing page in: {settings.output_dir}")


@app.command("templates")
def list_templates() -> None:
    print("Available templates:\n")
    print(templates.names)


@app.command("parsers")
def list_parsers() -> None:
    print("Available parsers:\n")
    print(parsers.names)
