"""Test the minimalist theme plugin."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from lander.ext.parser import DocumentMetadata
from lander.ext.theme import ThemePluginDirectory
from lander.settings import BuildSettings, DownloadableFile

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_minimalist_article(caplog: LogCaptureFixture, temp_cwd: Path) -> None:
    """Test the minimalist plugin using the ``tests/data/article`` sample."""
    caplog.set_level(logging.DEBUG, logger="lander")

    data_root = Path(__file__).parent / "data" / "article"
    output_dir = Path("_build")
    # Mock up metadata to isolate the test case
    metadata = DocumentMetadata(title="Example Article Document")
    # Mock build settings as well
    settings = BuildSettings(
        source_path=data_root / "article.tex",
        pdf=DownloadableFile.load(data_root / "article.pdf"),
        output_dir=output_dir,
        parser="article",
        theme="minimalist",
    )

    # Load from the plugin system, though directly importing the
    # MinimalistTheme is also valid for this test.
    themes = ThemePluginDirectory.load_plugins()
    Theme = themes["minimalist"]
    theme = Theme(metadata=metadata, settings=settings)

    assert theme.base_theme_name == "base"
    assert isinstance(theme.base_theme, themes["base"])
    assert theme.metadata == metadata
    assert theme.settings == settings

    theme.build_site()

    assert output_dir.is_dir()

    index_html_path = output_dir / "index.html"
    assert index_html_path.exists()
    pdf_path = output_dir / "article.pdf"
    assert pdf_path.exists()

    soup = BeautifulSoup(index_html_path.read_text(), "html.parser")
    assert soup.title.string == "Example Article Document"
    h1 = soup.find("h1")
    assert h1.string == "Example Article Document"

    download_link = soup.find(
        "a", attrs={"download": True, "href": "article.pdf"}
    )
    assert download_link is not None
    assert download_link.text == "article.pdf"
