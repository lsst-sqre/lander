"""Tests for the lander.ext.parser._gitdata module."""

from __future__ import annotations

import datetime
from pathlib import Path, PurePath

from lander.ext.parser import GitFile, GitRepository


def test_gitfile_extension() -> None:
    """Test the GitFile.extension property."""
    gitfile = GitFile(
        path=Path(__file__),
        name=PurePath(__file__),
        date_modified=datetime.datetime.now(),
    )
    assert gitfile.extension == "py"  # this test file


def test_gitrepository() -> None:
    git_repository = GitRepository.create(Path(__file__).parent)
    assert len(git_repository.files) > 0

    extensions = set([gitfile.extension for gitfile in git_repository.files])
    assert "py" in extensions
