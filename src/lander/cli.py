from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

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
    print("Running lander build")
    print(settings)
