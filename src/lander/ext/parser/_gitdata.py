"""Metadata retrieval from a local Git repository."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import List, Optional, Sequence

import git

__all__ = ["GitFile", "GitRepository"]


@dataclass
class GitFile:
    """A file in Git."""

    path: Path

    name: PurePath

    date_modified: datetime.datetime

    @property
    def extension(self) -> str:
        """The file's extension (without the ``.`` suffix)."""
        return self.name.suffix[1:]  # remove "."


@dataclass
class GitRepository:
    """A Git repository."""

    path: Path
    """Path for the root of the repository."""

    date_modified: datetime.datetime
    """Date when the head commit was created."""

    repo: git.Repo
    """The GitPython repository representation."""

    files: List[GitFile]
    """"Files in the Git repository."""

    @classmethod
    def create(cls, path: Path) -> GitRepository:
        """Create a GitRepository from a Git repository located on the
        file system.
        """
        repo = git.Repo(path=str(path), search_parent_directories=True)
        repo_path = Path(repo.working_tree_dir)
        head_commit = repo.head.commit

        files = GitRepository._gather_files(repo)

        return cls(
            path=repo_path,
            date_modified=head_commit.committed_datetime,
            repo=repo,
            files=files,
        )

    @staticmethod
    def _gather_files(repo: git.Repo) -> List[GitFile]:
        """Gather metadata about all files in the Git tree."""
        files: List[GitFile] = []

        head_commit = repo.head.commit

        for item in head_commit.tree.traverse():
            if item.type == "blob":
                try:
                    git_file = GitRepository._import_file(
                        filepath=Path(item.abspath), repo=repo
                    )
                    files.append(git_file)
                except IOError:
                    continue

        return files

    @staticmethod
    def _import_file(*, filepath: Path, repo: git.Repo) -> GitFile:
        """Gather Git metadata about a file.

        Parameters
        ----------
        filepath : `Path`
            Absolute or repository-relative path for a file.
        repo : `git.Repo`
            A `git.Repo` instance.

        Returns
        -------
        git_file : `GitFile`
            Representation of the Git file.

        Raises
        ------
        IOError
            Raised if the ``filepath`` does not exist in the Git repository.
        """
        head_commit = repo.head.commit

        # Filepath relative to the repo path
        repo_path = Path(repo.working_tree_dir)
        repo_rel_path = filepath.resolve().relative_to(repo_path.resolve())

        # Most recent commit datetime of the given file.
        # Don't use head_commit.iter_parents because then it skips the
        # commit of a file that's added but never modified.
        for commit in head_commit.iter_items(
            repo, head_commit, [repo_rel_path], skip=0,
        ):
            return GitFile(
                path=filepath.resolve(),
                name=PurePath(repo_rel_path),
                date_modified=commit.committed_datetime,
            )

        # Only get here if git could not find the file path in the history
        raise IOError("File {} not found".format(filepath))

    def compute_date_modified(
        self, extensions: Optional[Sequence[str]] = None
    ) -> datetime.datetime:
        """Get the most recent modification date, optional considering only
        files with one of an accepted sequence of extensions.

        Parameters
        ----------
        extensions : sequence of `str`
            Extension names, such as ``"pdf"``, ``"tex"``.
        """
        dates_modified = []
        for git_file in self.files:
            if extensions and git_file.extension not in extensions:
                continue
            dates_modified.append(git_file.date_modified)

        return max(dates_modified)
