"""Tests for the lander.ext.parser._cidata module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lander.ext.parser import CiMetadata

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_null(monkeypatch: MonkeyPatch) -> None:
    """Test when CI environment variables aren't available."""
    # Ensure the triggering environment variable from GitHub Actions isn't set
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    ci_metadata = CiMetadata.create()

    assert ci_metadata.platform == "null"


def test_github_actions_branch(monkeypatch: MonkeyPatch) -> None:
    """Test a branch build in GitHub Actions."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/tickets/DM-26564")
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_REPOSITORY", "lsst-sqre/lander")
    monkeypatch.setenv(
        "GITHUB_SHA", "cecaac52e1dbbc7709a93f715c3c68b845a3f976"
    )

    ci_metadata = CiMetadata.create()

    assert ci_metadata.platform == "github_actions"
    assert ci_metadata.git_ref == "tickets/DM-26564"
    assert ci_metadata.git_ref_type == "branch"
    assert ci_metadata.git_sha == ("cecaac52e1dbbc7709a93f715c3c68b845a3f976")
    assert ci_metadata.build_id == "1234"
    assert ci_metadata.build_url == (
        "https://github.com/lsst-sqre/lander/actions/runs/1234"
    )
    assert ci_metadata.github_slug == "lsst-sqre/lander"
    assert ci_metadata.github_repository == (
        "https://github.com/lsst-sqre/lander"
    )


def test_github_actions_tag(monkeypatch: MonkeyPatch) -> None:
    """Test a branch build in GitHub Actions."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REF", "refs/tags/1.0.0")

    ci_metadata = CiMetadata.create()

    assert ci_metadata.platform == "github_actions"
    assert ci_metadata.git_ref == "1.0.0"
    assert ci_metadata.git_ref_type == "tag"
    assert ci_metadata.github_repository is None


def test_travis_branch(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("TRAVIS", "true")
    monkeypatch.setenv("TRAVIS_BRANCH", "tickets/DM-26564")
    monkeypatch.setenv(
        "TRAVIS_COMMIT", "cecaac52e1dbbc7709a93f715c3c68b845a3f976"
    )
    monkeypatch.setenv("TRAVIS_BUILD_NUMBER", "1234")
    monkeypatch.setenv("TRAVIS_BUILD_WEB_URL", "https://example.com/1234")
    monkeypatch.setenv("TRAVIS_REPO_SLUG", "lsst-sqre/lander")

    ci_metadata = CiMetadata.create()

    assert ci_metadata.platform == "travis"
    assert ci_metadata.git_ref == "tickets/DM-26564"
    assert ci_metadata.git_ref_type == "branch"
    assert ci_metadata.git_sha == ("cecaac52e1dbbc7709a93f715c3c68b845a3f976")
    assert ci_metadata.build_id == "1234"
    assert ci_metadata.build_url == "https://example.com/1234"
    assert ci_metadata.github_slug == "lsst-sqre/lander"
    assert ci_metadata.github_repository == (
        "https://github.com/lsst-sqre/lander"
    )


def test_travis_tag(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("TRAVIS", "true")
    monkeypatch.setenv("TRAVIS_TAG", "1.0.0")
    monkeypatch.setenv(
        "TRAVIS_COMMIT", "cecaac52e1dbbc7709a93f715c3c68b845a3f976"
    )
    monkeypatch.setenv("TRAVIS_BUILD_NUMBER", "1234")
    monkeypatch.setenv("TRAVIS_BUILD_WEB_URL", "https://example.com/1234")
    monkeypatch.setenv("TRAVIS_REPO_SLUG", "lsst-sqre/lander")

    ci_metadata = CiMetadata.create()

    assert ci_metadata.platform == "travis"
    assert ci_metadata.git_ref == "1.0.0"
    assert ci_metadata.git_ref_type == "tag"
    assert ci_metadata.git_sha == ("cecaac52e1dbbc7709a93f715c3c68b845a3f976")
    assert ci_metadata.build_id == "1234"
    assert ci_metadata.build_url == "https://example.com/1234"
    assert ci_metadata.github_slug == "lsst-sqre/lander"
    assert ci_metadata.github_repository == (
        "https://github.com/lsst-sqre/lander"
    )
