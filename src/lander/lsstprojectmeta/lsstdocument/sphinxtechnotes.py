"""Reduce technote projects into JSON-LD metadata.
"""

__all__ = (
    "process_sphinx_technote",
    "reduce_technote_metadata",
    "download_metadata_yaml",
    "NotSphinxTechnoteError",
)

import datetime
import logging

import aiohttp
import yaml

from ..github.graphql import GitHubQuery, github_request
from ..github.urls import (
    make_raw_content_url,
    normalize_repo_root_url,
    parse_repo_slug_from_url,
)


async def process_sphinx_technote(
    session, github_api_token, ltd_product_data, mongo_collection=None
):
    """Extract, transform, and load Sphinx-based technote metadata.

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
    NotSphinxTechnoteError
        Raised when the LTD product cannot be interpreted as a Sphinx-based
        technote project because it's missing a metadata.yaml file in its
        GitHub repository. This implies that the LTD product *could* be of a
        different format.

    .. `GitHub personal access token guide`: https://ls.st/41d
    """
    logger = logging.getLogger(__name__)

    github_url = ltd_product_data["doc_repo"]
    github_url = normalize_repo_root_url(github_url)
    repo_slug = parse_repo_slug_from_url(github_url)

    try:
        metadata_yaml = await download_metadata_yaml(session, github_url)
    except aiohttp.ClientResponseError as err:
        # metadata.yaml not found; probably not a Sphinx technote
        logger.debug(
            "Tried to download %s's metadata.yaml, got status %d",
            ltd_product_data["slug"],
            err.code,
        )
        raise NotSphinxTechnoteError()

    # Extract data from the GitHub API
    github_query = GitHubQuery.load("technote_repo")
    github_variables = {"orgName": repo_slug.owner, "repoName": repo_slug.repo}
    github_data = await github_request(
        session,
        github_api_token,
        query=github_query,
        variables=github_variables,
    )

    try:
        jsonld = reduce_technote_metadata(
            github_url, metadata_yaml, github_data, ltd_product_data
        )
    except Exception as exception:
        message = "Issue building JSON-LD for technote %s"
        logger.exception(message, github_url, exception)
        raise

    if mongo_collection is not None:
        await _upload_to_mongodb(mongo_collection, jsonld)

    logger.info("Ingested technote %s into MongoDB", github_url)

    return jsonld


def reduce_technote_metadata(
    github_url, metadata, github_data, ltd_product_data
):
    """Reduce a technote project's metadata from multiple sources into a
    single JSON-LD resource.

    Parameters
    ----------
    github_url : `str`
        URL of the technote's GitHub repository.
    metadata : `dict`
        The parsed contents of ``metadata.yaml`` found in a technote's
        repository.
    github_data : `dict`
        The contents of the ``technote_repo`` GitHub GraphQL API query.
    ltd_product_data : `dict`
        JSON dataset for the technote corresponding to the
        ``/products/<product>`` of LTD Keeper.

    Returns
    -------
    metadata : `dict`
        JSON-LD-formatted dictionary.

    .. `GitHub personal access token guide`: https://ls.st/41d
    """
    repo_slug = parse_repo_slug_from_url(github_url)

    # Initialize a schema.org/Report and schema.org/SoftwareSourceCode
    # linked data resource
    jsonld = {
        "@context": [
            "https://raw.githubusercontent.com/codemeta/codemeta/2.0-rc/"
            "codemeta.jsonld",
            "http://schema.org",
        ],
        "@type": ["Report", "SoftwareSourceCode"],
        "codeRepository": github_url,
    }

    if "url" in metadata:
        url = metadata["url"]
    elif "published_url" in ltd_product_data:
        url = ltd_product_data["published_url"]
    else:
        raise RuntimeError(
            "No identifying url could be found: " "{}".format(github_url)
        )
    jsonld["@id"] = url
    jsonld["url"] = url

    if "series" in metadata and "serial_number" in metadata:
        jsonld["reportNumber"] = "{series}-{serial_number}".format(**metadata)
    else:
        raise RuntimeError("No reportNumber: {}".format(github_url))

    if "doc_title" in metadata:
        jsonld["name"] = metadata["doc_title"]

    if "description" in metadata:
        jsonld["description"] = metadata["description"]

    if "authors" in metadata:
        jsonld["author"] = [
            {"@type": "Person", "name": author_name}
            for author_name in metadata["authors"]
        ]

    if "last_revised" in metadata:
        # Prefer getting the 'last_revised' date from metadata.yaml
        # since it's considered an override.
        jsonld["dateModified"] = datetime.datetime.strptime(
            metadata["last_revised"], "%Y-%m-%d"
        )
    else:
        # Fallback to parsing the date of the last commit to the
        # default branch on GitHub (usually `master`).
        try:
            _repo_data = github_data["data"]["repository"]
            _master_data = _repo_data["defaultBranchRef"]
            jsonld["dateModified"] = datetime.datetime.strptime(
                _master_data["target"]["committedDate"], "%Y-%m-%dT%H:%M:%SZ"
            )
        except KeyError:
            pass

    try:
        _license_data = github_data["data"]["repository"]["licenseInfo"]
        _spdxId = _license_data["spdxId"]
        if _spdxId is not None:
            _spdx_url = "https://spdx.org/licenses/{}.html".format(_spdxId)
            jsonld["license"] = _spdx_url
    except KeyError:
        pass

    try:
        # Find the README(|.md|.rst|*) file in the repo root
        _master_data = github_data["data"]["repository"]["defaultBranchRef"]
        _files = _master_data["target"]["tree"]["entries"]
        for _node in _files:
            filename = _node["name"]
            normalized_filename = filename.lower()
            if normalized_filename.startswith("readme"):
                readme_url = make_raw_content_url(
                    repo_slug, "master", filename
                )
                jsonld["readme"] = readme_url
                break
    except KeyError:
        pass

    # Assume Travis is the CI service (always true at the moment)
    travis_url = "https://travis-ci.org/{}".format(repo_slug.full)
    jsonld["contIntegration"] = travis_url

    return jsonld


async def download_metadata_yaml(session, github_url):
    """Download the metadata.yaml file from a technote's GitHub repository."""
    metadata_yaml_url = _build_metadata_yaml_url(github_url)
    async with session.get(metadata_yaml_url) as response:
        response.raise_for_status()
        yaml_data = await response.text()
    return yaml.safe_load(yaml_data)


def _build_metadata_yaml_url(github_url):
    """Compute the URL to the raw metadata.yaml resource given the technote's
    GitHub repository URL.

    Parameters
    ----------
    github_url : `str`
        URL of the technote's GitHub repository.

    Returns
    -------
    metadata_yaml_url : `str`
        metadata.yaml URL (using the ``raw.githubusercontent.com`` domain).
    """
    repo_slug = parse_repo_slug_from_url(github_url)
    return make_raw_content_url(repo_slug, "master", "metadata.yaml")


async def _upload_to_mongodb(collection, jsonld):
    """Upsert the technote resource into the projectmeta MongoDB collection.

    Parameters
    ----------
    collection : `motor.motor_asyncio.AsyncIOMotorCollection`
        The MongoDB collection.
    jsonld : `dict`
        The JSON-LD document that reprsents the technote resource.
    """
    document = {"data": jsonld}
    query = {"data.reportNumber": jsonld["reportNumber"]}
    await collection.update(query, document, upsert=True, multi=False)


class NotSphinxTechnoteError(Exception):
    """Exception indicating that an LSST the Docs product cannot be a
    Sphinx-formatted technote and that a different format should be tried.
    """
