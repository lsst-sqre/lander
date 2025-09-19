"""Tests for metadata generation."""

import datetime
import os

from lander.config import Configuration, EncodedString
from lander.metadata.highwire import HighwireMetadata
from lander.metadata.opengraph import OpenGraphMetadata

# Path to test fixtures
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "test.pdf")


def test_highwire_metadata() -> None:
    """Test Highwire metadata generation."""
    config = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Test Document", html="Test Document"),
        abstract=EncodedString(
            plain="This is a test abstract.",
            html="<p>This is a test abstract.</p>",
        ),
        handle="TEST-001",
        authors=[
            EncodedString(plain="John Doe", html="John Doe"),
            EncodedString(plain="Jane Smith", html="Jane Smith"),
        ],
        build_datetime=datetime.datetime(2024, 1, 15, 12, 0, 0),
        github_slug="lsst/test-repo",
        ltd_product="test-001",
    )

    metadata = HighwireMetadata(config)
    html = metadata.as_html()

    # Check for required tags
    assert "citation_title" in html
    assert "citation_author" in html
    assert "citation_date" in html
    assert "citation_technical_report_number" in html
    assert "TEST-001" in html
    assert "2024/01/15" in html


def test_opengraph_metadata() -> None:
    """Test OpenGraph metadata generation."""
    config = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Test Document", html="Test Document"),
        abstract=EncodedString(
            plain="This is a test abstract.",
            html="<p>This is a test abstract.</p>",
        ),
        build_datetime=datetime.datetime(2024, 1, 15, 12, 0, 0),
        github_slug="lsst/test-repo",
        ltd_product="test-001",
    )

    metadata = OpenGraphMetadata(config)
    html = metadata.as_html()

    # Check for required tags
    assert "og:title" in html
    assert "og:description" in html
    assert "og:url" in html
    assert "og:type" in html
    assert "article" in html
    assert "2024-01-15T12:00:00Z" in html


def test_canonical_url_generation() -> None:
    """Test canonical URL generation."""
    # Test with LTD product
    config_ltd = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Test Document", html="Test Document"),
        ltd_product="test-001",
    )
    assert config_ltd.canonical_url == "https://test-001.lsst.io"

    # Test with GitHub slug fallback
    config_github = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Test Document", html="Test Document"),
        github_slug="lsst/test-repo",
    )
    assert config_github.canonical_url == "https://github.com/lsst/test-repo"

    # Test with neither
    config_none = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Test Document", html="Test Document"),
    )
    assert config_none.canonical_url is None


def test_metadata_escaping() -> None:
    """Test that HTML content is properly escaped."""
    config = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(
            plain="Title with \"quotes\" and 'apostrophes'", html="Title"
        ),
        abstract=EncodedString(
            plain="Abstract with \"quotes\" and 'apostrophes'",
            html="<p>Abstract</p>",
        ),
        authors=[
            EncodedString(plain='Author "Name"', html="Author Name"),
        ],
        github_slug="lsst/test-repo",
    )

    highwire = HighwireMetadata(config)
    html = highwire.as_html()

    # Check that quotes are escaped
    assert "&quot;" in html
    assert "&#39;" in html

    # Check that unescaped quotes are not present in content attributes
    assert 'content="Title with "quotes"' not in html
    assert "content='Title with 'apostrophes'" not in html


def test_metadata_with_missing_fields() -> None:
    """Test metadata generation with minimal configuration."""
    config = Configuration(
        build_dir="build",
        pdf_path=TEST_PDF_PATH,
        title=EncodedString(plain="Minimal Document", html="Minimal Document"),
    )

    highwire = HighwireMetadata(config)
    html = highwire.as_html()

    # Should have title and date (auto-generated) but not other optional fields
    assert "citation_title" in html
    assert "citation_date" in html  # This will be auto-generated
    assert "citation_author" not in html
    assert "citation_technical_report_number" not in html

    opengraph = OpenGraphMetadata(config)
    html = opengraph.as_html()

    # Should have title, type and dates but not other optional fields
    assert "og:title" in html
    assert "og:type" in html
    assert "og:article:published_time" in html  # This will be auto-generated
    assert "og:description" not in html
    assert "og:url" not in html
