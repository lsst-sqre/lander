"""Extract metadata from document landing pages created by Lander_.

.. Lander: https://github.com/lsst/lander
"""

__all__ = ("process_lander_page", "NotLanderPageError")

import logging
from urllib.parse import urljoin

import aiohttp

from ..jsonld import decode_jsonld


async def process_lander_page(
    session, github_api_token, ltd_product_data, mongo_collection=None
):
    """Extract, transform, and load metadata from Lander-based projects.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
        See http://aiohttp.readthedocs.io/en/stable/client.html.
    github_api_token : `str`
        A GitHub personal API token. See the `GitHub personal access token
        guide`_.
    ltd_product_data : `dict`
        Contents of ``metadata.yaml``, obtained via `download_metadata_yaml`.
        Data for this technote from the LTD Keeper API
        (``GET /products/<slug>``). Usually obtained via
        `lsstprojectmeta.ltd.get_ltd_product`.
    mongo_collection : `motor.motor_asyncio.AsyncIOMotorCollection`, optional
        MongoDB collection. This should be the common MongoDB collection for
        LSST projectmeta JSON-LD records. If provided, ths JSON-LD is upserted
        into the MongoDB collection.

    Returns
    -------
    metadata : `dict`
        JSON-LD-formatted dictionary.

    Raises
    ------
    NotLanderPageError
        Raised when the LTD product cannot be interpreted as a Lander page
        because the ``/metadata.jsonld`` file is absent. This implies that
        the LTD product *could* be of a different format.

    .. `GitHub personal access token guide`: https://ls.st/41d
    """
    logger = logging.getLogger(__name__)

    # Try to download metadata.jsonld from the Landing page site.
    published_url = ltd_product_data["published_url"]
    jsonld_url = urljoin(published_url, "/metadata.jsonld")
    try:
        async with session.get(jsonld_url) as response:
            logger.debug("%s response status %r", jsonld_url, response.status)
            response.raise_for_status()
            json_data = await response.text()
    except aiohttp.ClientResponseError as err:
        logger.debug(
            "Tried to download %s, got status %d", jsonld_url, err.code
        )
        raise NotLanderPageError()
    # Use our own json parser to get datetimes
    metadata = decode_jsonld(json_data)

    if mongo_collection is not None:
        await _upload_to_mongodb(mongo_collection, metadata)

    return metadata


async def _upload_to_mongodb(collection, jsonld):
    """Upsert the technote resource into the projectmeta MongoDB collection.

    Parameters
    ----------
    collection : `motor.motor_asyncio.AsyncIOMotorCollection`
        The MongoDB collection.
    jsonld : `dict`
        The JSON-LD document that represents the document resource.
    """
    document = {"data": jsonld}
    query = {"data.reportNumber": jsonld["reportNumber"]}
    await collection.update(query, document, upsert=True, multi=False)


class NotLanderPageError(Exception):
    """Exception indicating that an LSST the Docs product cannot be a Lander
    landing page because ``/metadata.jsonld`` is missing.
    """
