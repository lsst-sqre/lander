"""Command line interface for ``lander`` executable."""
from argparse import ArgumentParser
import os
import sys

import pkg_resources


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

    return parser.parse_args()


def main():
    """Entrypoint for ``lander`` executable."""
    args = parse_args()

    if args.show_license:
        print_license()
        sys.exit(0)

    if args.show_version:
        print_version()
        sys.exit(0)


def print_license():
    license_txt = pkg_resources.resource_string(
        __name__,
        os.path.join("..", "LICENSE"))
    license = license_txt.decode('utf-8')
    print(license)


def print_version():
    version = pkg_resources.get_distribution('lander').version
    print(version)
