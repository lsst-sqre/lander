"""Command line interface for ``lander`` executable."""

__all__ = ["main"]

import getpass
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import click
import pkg_resources
import structlog

from .config import build_configuration
from .lander import Lander


@click.command()
@click.option(
    "--build-dir",
    required=True,
    default=os.path.abspath("_build"),
    help="Build directory (scratch space).",
)
@click.option(
    "--pdf", "pdf_path", required=True, help="File path of PDF document."
)
@click.option(
    "--lsstdoc",
    "lsstdoc_tex_path",
    help="File path of an lsstdoc LaTeX file (for metadata).",
)
@click.option(
    "--env",
    "environment",
    type=click.Choice(["travis", "github"]),
    help="Deprecated",
)
@click.option(
    "--title",
    "title",
    help="Document title. This overrides information extracted from the "
    "document itself",
)
@click.option(
    "--author",
    "authors",
    multiple=True,
    help="Author name. This overrides information extracted from the document "
    "itself. Set a --author option for each author.",
)
@click.option(
    "--abstract",
    help="Document abstract. This overrides information extracted from the "
    "document itself",
)
@click.option(
    "--handle",
    help="Document handle, such as LDM-000. This overrides information "
    "extracted from the document itself.",
)
@click.option(
    "--date",
    help="Datetime string describing when the document was authored. "
    "This overrides information extracted from the document itself.",
)
@click.option(
    "--github-slug",
    help="Git repository slug. This option is automatically set when "
    "running from GitHub actions or Travis CI.",
    envvar=["GITHUB_REPOSITORY", "TRAVIS_REPO_SLUG"],
)
@click.option(
    "--github-sha",
    help="Git commit SHA. This option is automatically set when running "
    "from GitHub Actions or Travis CI.",
    envvar=["GITHUB_SHA", "TRAVIS_COMMIT"],
)
@click.option(
    "--github-branch",
    help="Git repository branch name. This option is automatically set when "
    "running from GitHub Actions or Travis CI.",
    envvar=["GITHUB_REF", "TRAVIS_BRANCH"],
)
@click.option(
    "--extra-download",
    "extra_downloads",
    multiple=True,
    default=[],
    help="Path of additional an file to provide a download link for from the "
    "landing page. Set a --extra-download option for each file. These files "
    "will be copied into the root deployment directory. The main PDF (--pdf) "
    "should not be included in this list.",
)
@click.option(
    "--ltd-product", help="Product name on LSST the Docs, such as ``ldm-000``."
)
@click.option(
    "--ltd-url",
    help="LSST the Docs API URL.",
    default="https://keeper.lsst.codes",
)
@click.option(
    "--ltd-user",
    help="LSST the Docs username.",
    envvar=["LTD_USERNAME", "LTD_KEEPER_USER"],
)
@click.option(
    "--ltd-password",
    help="LSST the Docs password.",
    envvar=["LTD_PASSWORD", "LTD_KEEPER_PASSWORD"],
    hide_input=True,
)
@click.option(
    "--upload/--no-upload",
    help="Upload the landing page to LSST the Docs",
    default=False,
)
@click.option(
    "--version",
    "show_version",
    default=False,
    help="Print the app version and exit.",
)
@click.option(
    "--verbose/--quiet", default=False, help="Show debugging information."
)
def main(
    build_dir: str,
    pdf_path: str,
    lsstdoc_tex_path: Optional[str],
    environment: str,
    title: Optional[str],
    authors: Optional[List[str]],
    abstract: Optional[str],
    handle: Optional[str],
    github_slug: Optional[str],
    github_sha: Optional[str],
    github_branch: Optional[str],
    date: Optional[str],
    extra_downloads: List[str],
    ltd_product: Optional[str],
    ltd_url: str,
    ltd_user: Optional[str],
    ltd_password: Optional[str],
    upload: bool,
    verbose: bool,
    show_version: bool,
) -> None:
    """Entrypoint for ``lander`` executable."""
    configure_logger(verbose=verbose)
    logger = structlog.get_logger("lander")

    if show_version:
        # only print the version
        print_version()
        sys.exit(0)

    version = pkg_resources.get_distribution("lander").version
    logger.info("Lander version {0}".format(version))

    if upload and ltd_password is None:
        ltd_password = getpass.getpass(prompt="LSST the Docs password: ")

    # Collect CLI-based configurations
    cli_configs: Dict[str, Any] = {}
    if title:
        cli_configs["title"] = {"plain": title}
    if authors:
        cli_configs["authors"] = [{"plain": a} for a in authors]
    if abstract:
        cli_configs["abstract"] = {"plain": abstract}
    if handle:
        cli_configs["handle"] = handle
    if github_slug:
        cli_configs["github_slug"] = github_slug
    if github_branch:
        cli_configs["git_ref"] = github_branch
    if github_sha:
        cli_configs["git_sha"] = github_sha
    if date:
        cli_configs["date"] = date

    # Create the finalized Configuration that compiles information from
    # the CLI and also document metadata.
    config = build_configuration(
        build_dir=build_dir,
        pdf_path=pdf_path,
        lsstdoc_tex_path=lsstdoc_tex_path,
        cli_configs=cli_configs,
        extra_downloads=extra_downloads,
        ltd_product=ltd_product,
        ltd_url=ltd_url,
        ltd_user=ltd_user,
        ltd_password=ltd_password,
        upload=upload,
    )

    logger.info(config.dict())

    # disable any build confirmed to be a PR with Travis
    if config.is_travis_pull_request:
        logger.info("Skipping build from PR.")
        sys.exit(0)

    lander = Lander(config)
    lander.build_site()
    logger.info("Build complete")

    if config.upload:
        lander.upload_site()
        logger.info("Upload complete")

    logger.info("Lander complete")


def configure_logger(verbose: bool = False) -> None:
    """Configure the application's root logger."""
    # Configure the root logger
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(
        "%(asctime)s %(levelname)8s %(name)s | %(message)s"
    )
    stream_handler.setFormatter(stream_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(logging.WARNING)

    # Setup first-party logging
    app_logger = logging.getLogger("lander")
    lsstprojectmeta_logger = logging.getLogger("lsstprojectmeta")
    ltdconveyor_logger = logging.getLogger("ltdconveyor")
    if verbose:
        app_logger.setLevel(logging.DEBUG)
        lsstprojectmeta_logger.setLevel(logging.DEBUG)
        ltdconveyor_logger.setLevel(logging.DEBUG)
    else:
        app_logger.setLevel(logging.INFO)
        lsstprojectmeta_logger.setLevel(logging.INFO)
        ltdconveyor_logger.setLevel(logging.INFO)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def print_version() -> None:
    version = pkg_resources.get_distribution("lander").version
    print(version)
