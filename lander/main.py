"""Command line interface for ``lander`` executable."""
from argparse import ArgumentParser
import logging
import os
import sys

import pkg_resources
import structlog

from .config import Configuration
from .lander import Lander


def parse_args():
    """Create an `argparse.ArgumentParser` and parse command line arguments.
    """
    parser = ArgumentParser(
        description="Create a landing website for for PDF documentation.",
        epilog="lander is a product of LSST Data Management. Code is "
               "available at https://github.com/lsst-sqre/lander.")

    parser.add_argument(
        '--license',
        dest='show_license',
        default=False,
        action='store_true',
        help="Show license information and exit.")

    parser.add_argument(
        '--version',
        dest='show_version',
        default=False,
        action='store_true',
        help="Show version information and exit.")

    parser.add_argument(
        '--verbose',
        default=False,
        action='store_true',
        help='Show debugging information.')

    parser.add_argument(
        '--build-dir',
        dest='build_dir',
        default=os.path.abspath('_build'),
        help='Build directory (scratch space).')

    parser.add_argument(
        '--pdf',
        dest='pdf_path',
        help='Filepath of PDF document.'
    )

    parser.add_argument(
        '--lsstdoc',
        dest='lsstdoc_tex_path',
        help='File path of a lsstdoc LaTeX file (for metadata).'
    )

    parser.add_argument(
        '--title',
        dest='title',
        help='Document title (metadata override)'
    )

    parser.add_argument(
        '--authors',
        dest='authors_json',
        help='Author list, as a JSON array of strings (metadata override).'
    )

    parser.add_argument(
        '--abstract',
        dest='abstract',
        help='Document abstract (metadata override).'
    )

    parser.add_argument(
        '--handle',
        dest='doc_handle',
        help='Document handle, such as LDM-000 (metadata override).'
    )

    parser.add_argument(
        '--repo-url',
        dest='repo_url',
        help='Git repository URL (metadata override).'
    )

    parser.add_argument(
        '--repo-branch',
        dest='repo_branch',
        help='Git repository branch name (metadata override).'
    )

    parser.add_argument(
        '--ltd-product',
        dest='ltd_product',
        help='Product name on LSST the Docs, such as `ldm-000` '
             '(metadata override).'
    )

    return parser.parse_args()


def main():
    """Entrypoint for ``lander`` executable."""
    args = parse_args()
    config_logger(args)
    logger = structlog.get_logger(__name__)

    if args.show_license:
        print_license()
        sys.exit(0)

    if args.show_version:
        print_version()
        sys.exit(0)

    config = Configuration(args=args)
    lander = Lander(config)
    lander.build_site()

    logger.info('Complete')


def config_logger(args):
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level)

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


def print_license():
    license_txt = pkg_resources.resource_string(
        __name__,
        os.path.join("..", "LICENSE"))
    license = license_txt.decode('utf-8')
    print(license)


def print_version():
    version = pkg_resources.get_distribution('lander').version
    print(version)
