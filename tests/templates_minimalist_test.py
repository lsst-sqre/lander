"""Test the minimalist template plugin."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from lander.ext.parser import DocumentMetadata
from lander.ext.template import TemplatePluginDirectory
from lander.settings import BuildSettings


def test_minimalist_article(temp_cwd: Path) -> None:
    """Test the minimalist plugin using the ``tests/data/article`` sample."""
    data_root = Path(__file__).parent / "data" / "article"
    output_dir = Path("_build")
    # Mock up metadata to isolate the test case
    metadata = DocumentMetadata(title="Example Article Document")
    # Mock build settings as well
    settings = BuildSettings(
        source_path=data_root / "article.tex",
        pdf_path=data_root / "article.pdf",
        output_dir=output_dir,
        parser="article",
        template="minimalist",
    )

    # Load from the plugin system, though directly importing the
    # MinimalistTemplate is also valid for this test.
    templates = TemplatePluginDirectory.load_plugins()
    Template = templates["minimalist"]
    template = Template(metadata=metadata, settings=settings)
    assert template.metadata == metadata
    assert template.settings == settings

    template.build_site()

    assert output_dir.is_dir()

    index_html_path = output_dir / "index.html"
    assert index_html_path.exists()
    pdf_path = output_dir / "article.pdf"
    assert pdf_path.exists()

    soup = BeautifulSoup(index_html_path.read_text(), "html.parser")
    assert soup.title.string == "Example Article Document"
