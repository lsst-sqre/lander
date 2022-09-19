"""Utilities for extracting commit timestamps from Git repositories.
"""

__all__ = (
    "read_git_commit_timestamp",
    "read_git_commit_timestamp_for_file",
    "get_content_commit_date",
)

import itertools
import logging
import os

import git


def read_git_commit_timestamp(repo_path=None, repo=None):
    """Obtain the timestamp from the current head commit of a Git repository.

    Parameters
    ----------
    repo_path : `str`, optional
        Path to the Git repository. Leave as `None` to use the current working
        directory.

    Returns
    -------
    commit_timestamp : `datetime.datetime`
        The datetime of the head commit.
    """
    if repo is None:
        repo = git.repo.base.Repo(
            path=repo_path, search_parent_directories=True
        )
    head_commit = repo.head.commit
    return head_commit.committed_datetime


def read_git_commit_timestamp_for_file(filepath, repo_path=None, repo=None):
    """Obtain the timestamp for the most recent commit to a given file in a
    Git repository.

    Parameters
    ----------
    filepath : `str`
        Absolute or repository-relative path for a file.
    repo_path : `str`, optional
        Path to the Git repository. Leave as `None` to use the current working
        directory or if a ``repo`` argument is provided.
    repo : `git.Repo`, optional
        A `git.Repo` instance.

    Returns
    -------
    commit_timestamp : `datetime.datetime`
        The datetime of the most recent commit to the given file.

    Raises
    ------
    IOError
        Raised if the ``filepath`` does not exist in the Git repository.
    """
    logger = logging.getLogger(__name__)

    if repo is None:
        repo = git.repo.base.Repo(
            path=repo_path, search_parent_directories=True
        )
    repo_path = repo.working_tree_dir

    head_commit = repo.head.commit

    # filepath relative to the repo path
    logger.debug("Using Git repo at %r", repo_path)
    filepath = os.path.relpath(os.path.abspath(filepath), start=repo_path)
    logger.debug("Repo-relative filepath is %r", filepath)

    # Most recent commit datetime of the given file.
    # Don't use head_commit.iter_parents because then it skips the
    # commit of a file that's added but never modified.
    for commit in head_commit.iter_items(
        repo, head_commit, [filepath], skip=0
    ):
        return commit.committed_datetime

    # Only get here if git could not find the file path in the history
    raise IOError("File {} not found".format(filepath))


def get_content_commit_date(
    extensions, acceptance_callback=None, root_dir="."
):
    """Get the datetime for the most recent commit to a project that
    affected certain types of content.

    Parameters
    ----------
    extensions : sequence of 'str'
        Extensions of files to consider in getting the most recent commit
        date. For example, ``('rst', 'svg', 'png')`` are content extensions
        for a Sphinx project. **Extension comparision is case sensitive.** add
        uppercase variants to match uppercase extensions.
    acceptance_callback : callable
        Callable function whose sole argument is a file path, and returns
        `True` or `False` depending on whether the file's commit date should
        be considered or not. This callback is only run on files that are
        included by ``extensions``. Thus this callback is a way to exclude
        specific files that would otherwise be included by their extension.
    root_dir : 'str`, optional
        Only content contained within this root directory is considered.
        This directory must be, or be contained by, a Git repository. This is
        the current working directory by default.

    Returns
    -------
    commit_date : `datetime.datetime`
        Datetime of the most recent content commit.

    Raises
    ------
    RuntimeError
        Raised if no content files are found.
    """
    logger = logging.getLogger(__name__)

    def _null_callback(_):
        return True

    if acceptance_callback is None:
        acceptance_callback = _null_callback

    # Cache the repo object for each query
    root_dir = os.path.abspath(root_dir)
    repo = git.repo.base.Repo(path=root_dir, search_parent_directories=True)

    # Iterate over all files with all file extensions, looking for the
    # newest commit datetime.
    newest_datetime = None
    iters = [
        _iter_filepaths_with_extension(ext, root_dir=root_dir)
        for ext in extensions
    ]
    for content_path in itertools.chain(*iters):
        content_path = os.path.abspath(os.path.join(root_dir, content_path))

        if acceptance_callback(content_path):
            logger.debug("Found content path %r", content_path)
            try:
                commit_datetime = read_git_commit_timestamp_for_file(
                    content_path, repo=repo
                )
                logger.debug(
                    "Commit timestamp of %r is %s",
                    content_path,
                    commit_datetime,
                )
            except IOError:
                logger.warning(
                    "Count not get commit for %r, skipping", content_path
                )
                continue

            if not newest_datetime or commit_datetime > newest_datetime:
                # Seed initial newest_datetime
                # or set a newer newest_datetime
                newest_datetime = commit_datetime
                logger.debug("Newest commit timestamp is %s", newest_datetime)

        logger.debug("Final commit timestamp is %s", newest_datetime)

    if newest_datetime is None:
        raise RuntimeError("No content files found in {}".format(root_dir))

    return newest_datetime


def _iter_filepaths_with_extension(extname, root_dir="."):
    """Iterative over relative filepaths of files in a directory, and
    sub-directories, with the given extension.

    Parameters
    ----------
    extname : `str`
        Extension name (such as 'txt' or 'rst'). Extension comparison is
        case sensitive.
    root_dir : 'str`, optional
        Root directory. Current working directory by default.

    Yields
    ------
    filepath : `str`
        File path, relative to ``root_dir``, with the given extension.
    """
    # needed for comparison with os.path.splitext
    if not extname.startswith("."):
        extname = "." + extname

    root_dir = os.path.abspath(root_dir)

    for dirname, sub_dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if os.path.splitext(filename)[-1] == extname:
                full_filename = os.path.join(dirname, filename)
                rel_filepath = os.path.relpath(full_filename, start=root_dir)
                yield rel_filepath
