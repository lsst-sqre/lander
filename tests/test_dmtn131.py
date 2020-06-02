"""Test using DMTN-131 as the reference document."""

import os
from pathlib import Path

from click.testing import CliRunner

from lander.main import main


def test_dmtn131_manual(tmp_path: Path) -> None:
    """Integration test with DMTN-131, located in tests/data/dmtn-131, with
    all manually-entered data.
    """
    root = os.path.join(os.path.dirname(__file__), "data", "dmtn-131")
    pdf_path = os.path.join(root, "DMTN-131.pdf")
    assert os.path.exists(pdf_path)

    build_dir = tmp_path / "build"
    build_dir.mkdir()
    assert build_dir.exists()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--build-dir",
            str(build_dir),
            "--pdf",
            pdf_path,
            "--title",
            "When  clouds might be good  for LSST",
            "--author",
            "William O'Mullane",
            "--abstract",
            "The abstract.",
            "--handle",
            "DMTN-131",
            "--date",
            "2019-10-04",
            "--github-slug",
            "lsst-dm/dmtn-131",
            "--github-sha",
            "b360515f21ef3bbb9515c6298d22ae47b3f4d722",
            "--github-branch",
            "refs/heads/master",  # simulate GITHUB_REF GitHub Actions env var
        ],
    )
    assert result.exit_code == 0

    assert (build_dir / "index.html").exists()
