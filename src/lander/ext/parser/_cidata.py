"""Metadata from the continuous integration environment."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

__all__ = ["GitRefType", "CiMetadata", "GitRefType"]


class GitRefType(str, Enum):
    """Type of git reftag, or branch."""

    tag = "tag"
    """The git ref corresponds to a tag."""

    branch = "branch"
    """The git ref corresponds to a branch."""


class CiPlatform(str, Enum):
    """The name of the CI platform."""

    null = "null"
    """The build is not performed through a common CI platform."""

    github_actions = "github_actions"
    """The build is performed on GitHub Actions."""

    travis = "travis"
    """The build is performed on Travis CI."""


@dataclass
class CiMetadata:
    """Metadata gathered from CI platform environment variables."""

    platform: CiPlatform = CiPlatform.null
    """The CI platform."""

    git_ref: Optional[str] = None
    """Git reference: branch or tag name."""

    git_ref_type: Optional[GitRefType] = None
    """Type of git reference: branch or tag."""

    git_sha: Optional[str] = None
    """The SHA1 of the Git commit."""

    build_id: Optional[str] = None
    """CI build number."""

    build_url: Optional[str] = None
    """CI dashboard URL for this build."""

    github_slug: Optional[str] = None
    """Slug of the GitHub repository (``org/repo``)."""

    @property
    def github_repository(self) -> Optional[str]:
        """URL of the GitHub repository homepage."""
        if self.github_slug:
            return f"https://github.com/{self.github_slug}"
        else:
            return None

    @classmethod
    def create(cls) -> CiMetadata:
        """Gather CI metadata, automatically inferring the CI platform."""
        if os.getenv("GITHUB_ACTIONS"):
            return cls.for_github_actions()
        elif os.getenv("TRAVIS") == "true":
            return cls.for_travis()
        else:
            # CI platform cannot be inferred, so return empty metadata.
            return cls()

    @classmethod
    def for_github_actions(cls) -> CiMetadata:
        """Gather CI metadata from a GitHub Actions environment."""
        github_ref = os.getenv("GITHUB_REF")
        run_id = os.getenv("GITHUB_RUN_ID")
        repo = os.getenv("GITHUB_REPOSITORY")

        if run_id and repo:
            ci_build_url: Optional[str] = (
                f"https://github.com/{repo}/actions/runs/{run_id}"
            )
        else:
            ci_build_url = None

        if github_ref:
            m = re.match(
                r"refs/(?P<kind>heads|tags|pull)/(?P<ref>.+)", github_ref
            )
            if m:
                if m.group("kind") == "heads":
                    git_ref_type: Optional[GitRefType] = GitRefType.branch
                elif m.group("kind") == "tags":
                    git_ref_type = GitRefType.tag
                else:
                    git_ref_type = None

                git_ref: Optional[str] = m.group("ref")
            else:
                git_ref_type = None
                git_ref = None

        return cls(
            platform=CiPlatform.github_actions,
            git_sha=os.getenv("GITHUB_SHA"),
            git_ref=git_ref,
            git_ref_type=git_ref_type,
            build_id=run_id,
            build_url=ci_build_url,
            github_slug=repo,
        )

    @classmethod
    def for_travis(cls) -> CiMetadata:
        """Gather CI metadata from a Travis environment."""
        if os.getenv("TRAVIS_TAG"):
            git_ref: Optional[str] = os.getenv("TRAVIS_TAG")
            git_ref_type: Optional[GitRefType] = GitRefType.tag
        elif os.getenv("TRAVIS_BRANCH"):
            git_ref = os.getenv("TRAVIS_BRANCH")
            git_ref_type = GitRefType.branch
        else:
            git_ref = None
            git_ref_type = None

        return cls(
            platform=CiPlatform.travis,
            git_sha=os.getenv("TRAVIS_COMMIT"),
            git_ref=git_ref,
            git_ref_type=git_ref_type,
            build_id=os.getenv("TRAVIS_BUILD_NUMBER"),
            build_url=os.getenv("TRAVIS_BUILD_WEB_URL"),
            github_slug=os.getenv("TRAVIS_REPO_SLUG"),
        )
