"""APIs for working with the GitHub v4 (GraphQL) API.

https://developer.github.com/v4/
"""

__all__ = ("github_request", "GitHubQuery")

import os


async def github_request(
    session, api_token, query=None, mutation=None, variables=None
):
    """Send a request to the GitHub v4 (GraphQL) API.

    The request is asynchronous, with asyncio.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
    api_token : `str`
        A GitHub personal API token. See the `GitHub personal access token
        guide`_.
    query : `str` or `GitHubQuery`
        GraphQL query string. If provided, then the ``mutation`` parameter
        should not be set. For examples, see the `GitHub guide to query and
        mutation operations`_.
    mutation : `str` or `GitHubQuery`
        GraphQL mutation string. If provided, then the ``query`` parameter
        should not be set. For examples, see the `GitHub guide to query and
        mutation operations`_.
    variables : `dict`
        GraphQL variables, as a JSON-compatible dictionary. This is only
        required if the ``query`` or ``mutation`` uses GraphQL variables.

    Returns
    -------
    data : `dict`
        Parsed JSON as a `dict` object.

    .. `GitHub personal access token guide`: https://ls.st/41d
    .. `GitHub guide to query and mutation operations`: https://ls.st/9s7
    """
    payload = {}
    if query is not None:
        payload["query"] = str(query)  # converts a GitHubQuery
    if mutation is not None:
        payload["mutation"] = str(mutation)  # converts a GitHubQuery
    if variables is not None:
        payload["variables"] = variables

    headers = {"Authorization": "token {}".format(api_token)}

    url = "https://api.github.com/graphql"
    async with session.post(url, json=payload, headers=headers) as response:
        data = await response.json()

    return data


class GitHubQuery(object):
    """GitHub GraphQL (API v4) query string.

    Typically you'll use the `GitHubQuery.load` method to get a pre-made
    query string. Then use the `github_request` function to execute the query.

    Parameters
    ----------
    query : `str`
        GraphQL query or mutation string.
    name : `str`
        Description
    """

    def __init__(self, query, name=None):
        self.query = query
        self.name = name

    @classmethod
    def load(cls, query_name):
        """Load a pre-made query.

        These queries are distributed with lsstprojectmeta. See
        :file:`lsstrojectmeta/data/githubv4/README.rst` inside the
        package repository for details on available queries.

        Parameters
        ----------
        query_name : `str`
            Name of the query, such as ``'technote_repo'``.

        Returns
        -------
        github_query : `GitHubQuery
            A GitHub query or mutation object that you can pass to
            `github_request` to execute the request itself.
        """
        template_path = os.path.join(
            os.path.dirname(__file__),
            "../data/githubv4",
            query_name + ".graphql",
        )

        with open(template_path) as f:
            query_data = f.read()

        return cls(query_data, name=query_name)

    def __str__(self):
        return self.query
