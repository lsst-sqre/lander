"""Test for the built-in (demo) article class document parser plugin."""

from __future__ import annotations

from pathlib import Path

from lander.ext.parser._discovery import ParsingPlugins
from lander.settings import BuildSettings, DownloadableFile


def test_article() -> None:
    """Test using the dataset at ``tests/data/article/article.tex``."""
    data_root = Path(__file__).parent / "data" / "article"
    output_dir = Path("_build")
    settings = BuildSettings(
        source_path=data_root / "article.tex",
        pdf=DownloadableFile.load(data_root / "article.pdf"),
        output_dir=output_dir,
        parser="article",
        theme="minimalist",
    )

    plugins = ParsingPlugins.load_plugins()
    article_parser = plugins["article"]

    parser = article_parser(settings=settings)

    assert parser.tex_macros == {r"\version": "1.0"}

    md = parser.metadata
    assert md.title == "Example Article Document"
