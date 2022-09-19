"""Command line interface for lsstprojectmeta-ingest-docs.
"""
import argparse
import asyncio
import logging
import pprint

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

from ..lsstdocument.handles import DOCUMENT_HANDLE_PATTERN
from ..lsstdocument.lander import NotLanderPageError, process_lander_page
from ..lsstdocument.sphinxtechnotes import (
    NotSphinxTechnoteError,
    process_sphinx_technote,
)
from ..ltd import get_ltd_product, get_ltd_product_urls


def main():
    """Command line entrypoint to reduce technote metadata."""
    parser = argparse.ArgumentParser(
        description="Discover and ingest metadata from document sources, "
        "including lsstdoc-based LaTeX documents and "
        "reStructuredText-based technotes. Metadata can be "
        "upserted into the LSST Projectmeta MongoDB."
    )
    parser.add_argument(
        "--ltd-product",
        dest="ltd_product_url",
        help="URL of an LSST the Docs product "
        "(https://keeper.lsst.codes/products/<slug>). If provided, "
        "only this document will be ingested.",
    )
    parser.add_argument("--github-token", help="GitHub personal access token.")
    parser.add_argument(
        "--mongodb-uri",
        help="MongoDB connection URI. If provided, metadata will be loaded "
        "into the Projectmeta database. Omit this argument to just "
        "test the ingest pipeline.",
    )
    parser.add_argument(
        "--mongodb-db",
        default="lsstprojectmeta",
        help="Name of MongoDB database",
    )
    parser.add_argument(
        "--mongodb-collection",
        default="resources",
        help="Name of the MongoDB collection for projectmeta resources",
    )
    args = parser.parse_args()

    # Configure the root logger
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(
        "%(asctime)s %(levelname)8s %(name)s | %(message)s"
    )
    stream_handler.setFormatter(stream_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(logging.WARNING)
    # Configure app logger
    app_logger = logging.getLogger("lsstprojectmeta")
    app_logger.setLevel(logging.DEBUG)

    if args.mongodb_uri is not None:
        mongo_client = AsyncIOMotorClient(args.mongodb_uri, ssl=True)
        collection = mongo_client[args.mongodb_db][args.mongodb_collection]
    else:
        collection = None

    loop = asyncio.get_event_loop()

    if args.ltd_product_url is not None:
        # Run single technote
        loop.run_until_complete(
            run_single_ltd_doc(
                args.ltd_product_url, args.github_token, collection
            )
        )
    else:
        # Run bulk technote processing
        loop.run_until_complete(run_bulk_etl(args.github_token, collection))


async def run_single_ltd_doc(
    ltd_product_url, github_api_token, mongo_collection
):
    async with aiohttp.ClientSession() as session:
        jsonld = await process_ltd_doc(
            session,
            github_api_token,
            ltd_product_url,
            mongo_collection=mongo_collection,
        )
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(jsonld)


async def run_bulk_etl(github_api_token, mongo_collection):
    async with aiohttp.ClientSession() as session:
        product_urls = await get_ltd_product_urls(session)
        await process_ltd_doc_products(
            session,
            product_urls,
            github_api_token,
            mongo_collection=mongo_collection,
        )


async def process_ltd_doc_products(
    session, product_urls, github_api_token, mongo_collection=None
):
    """Run a pipeline to process extract, transform, and load metadata for
    multiple LSST the Docs-hosted projects

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
        See http://aiohttp.readthedocs.io/en/stable/client.html.
    product_urls : `list` of `str`
        List of LSST the Docs product URLs.
    github_api_token : `str`
        A GitHub personal API token. See the `GitHub personal access token
        guide`_.
    mongo_collection : `motor.motor_asyncio.AsyncIOMotorCollection`, optional
        MongoDB collection. This should be the common MongoDB collection for
        LSST projectmeta JSON-LD records.
    """
    tasks = [
        asyncio.ensure_future(
            process_ltd_doc(
                session,
                github_api_token,
                product_url,
                mongo_collection=mongo_collection,
            )
        )
        for product_url in product_urls
    ]
    await asyncio.gather(*tasks)


async def process_ltd_doc(
    session, github_api_token, ltd_product_url, mongo_collection=None
):
    """Ingest any kind of LSST document hosted on LSST the Docs from its
    source.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
        See http://aiohttp.readthedocs.io/en/stable/client.html.
    github_api_token : `str`
        A GitHub personal API token. See the `GitHub personal access token
        guide`_.
    ltd_product_url : `str`
        URL of the technote's product resource in the LTD Keeper API.
    mongo_collection : `motor.motor_asyncio.AsyncIOMotorCollection`, optional
        MongoDB collection. This should be the common MongoDB collection for
        LSST projectmeta JSON-LD records. If provided, ths JSON-LD is upserted
        into the MongoDB collection.

    Returns
    -------
    metadata : `dict`
        JSON-LD-formatted dictionary.

    .. `GitHub personal access token guide`: https://ls.st/41d
    """
    logger = logging.getLogger(__name__)

    ltd_product_data = await get_ltd_product(session, url=ltd_product_url)

    # Ensure the LTD product is a document
    product_name = ltd_product_data["slug"]
    doc_handle_match = DOCUMENT_HANDLE_PATTERN.match(product_name)
    if doc_handle_match is None:
        logger.debug("%s is not a document repo", product_name)
        return

    # Figure out the format of the document by probing for metadata files.
    # reStructuredText-based Sphinx documents have metadata.yaml file.
    try:
        return await process_sphinx_technote(
            session,
            github_api_token,
            ltd_product_data,
            mongo_collection=mongo_collection,
        )
    except NotSphinxTechnoteError:
        # Catch error so we can try the next format
        logger.debug("%s is not a Sphinx-based technote.", product_name)
    except Exception:
        # Something bad happened trying to process the technote.
        # Log and just move on.
        logger.exception("Unexpected error trying to process %s", product_name)
        return

    # Try interpreting it as a Lander page with a /metadata.jsonld document
    try:
        return await process_lander_page(
            session,
            github_api_token,
            ltd_product_data,
            mongo_collection=mongo_collection,
        )
    except NotLanderPageError:
        # Catch error so we can try the next format
        logger.debug(
            "%s is not a Lander page with a metadata.jsonld file.",
            product_name,
        )
    except Exception:
        # Something bad happened; log and move on
        logger.exception("Unexpected error trying to process %s", product_name)
        return
