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
        '--env',
        dest='environment',
        choices=['travis'],
        default=None,
        help='Environment for auto-configuration'
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
        '--date',
        dest='build_datetime',
        help='Datetime string describing when the document was authored '
             '(metadata override; the current datetime is used by default).'
    )

    parser.add_argument(
        '--extra-downloads',
        dest='extra_downloads',
        nargs='*',
        help='Paths of additional files to provide '
             'download links for from the landing page. '
             'These files will be copied into the root deployment directory. '
             'The main PDF (--pdf) should not be included in this list.'
    )

    parser.add_argument(
        '--docushare-url',
        dest='docushare_url',
        help='Docushare URL. Prefer the landing page URL in docushare rather '
             'than the direct PDF link so that users can see metadata about '
             'the accepted version. Using ls.st, this is the '
             'https://ls.st/ldm-nnn* URL.'
    )

    parser.add_argument(
        '--ltd-product',
        dest='ltd_product',
        help='Product name on LSST the Docs, such as `ldm-000` '
             '(metadata override).'
    )

    parser.add_argument(
        '--keeper-url',
        dest='keeper_url',
        help='LTD Keeper API URL (or $LTD_KEEPER_URL)'
    )

    parser.add_argument(
        '--keeper-user',
        dest='keeper_user',
        help='LTD Keeper API username (or $LTD_KEEPER_USER)'
    )

    parser.add_argument(
        '--keeper-password',
        dest='keeper_password',
        help='LTD Keeper API password (or $LTD_KEEPER_PASSWORD)'
    )

    parser.add_argument(
        '--aws-id',
        dest='aws_id',
        help='AWS key ID (or $LTD_AWS_ID)'
    )

    parser.add_argument(
        '--aws-secret',
        dest='aws_secret',
        help='AWS secret key (or $LTD_AWS_SECRET)'
    )

    parser.add_argument(
        '--upload',
        dest='upload',
        default=False,
        action='store_true',
        help='Upload built documentation to LSST the Docs'
    )

    return parser.parse_args()


def main():
    """Entrypoint for ``lander`` executable."""
    args = parse_args()
    config_logger(args)
    logger = structlog.get_logger(__name__)

    if args.show_version:
        print_version()
        sys.exit(0)

    config = Configuration(args=args)
    lander = Lander(config)
    lander.build_site()
    logger.info('Build complete')

    if config['upload']:
        lander.upload_site()
        logger.info('Upload complete')

    logger.info('Lander complete')


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


def print_version():
    version = pkg_resources.get_distribution('lander').version
    print(version)
