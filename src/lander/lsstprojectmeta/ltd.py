"""LSST the Docs client.
"""

__all__ = ("get_ltd_product_urls", "get_ltd_product")


async def get_ltd_product_urls(session):
    """Get URLs for LSST the Docs (LTD) products from the LTD Keeper API.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
        See http://aiohttp.readthedocs.io/en/stable/client.html.

    Returns
    -------
    product_urls : `list`
        List of product URLs.
    """
    product_url = "https://keeper.lsst.codes/products/"
    async with session.get(product_url) as response:
        data = await response.json()

    return data["products"]


async def get_ltd_product(session, slug=None, url=None):
    """Get the product resource (JSON document) from the LSST the Docs API.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        Your application's aiohttp client session.
        See http://aiohttp.readthedocs.io/en/stable/client.html.
    slug : `str`, optional
        Slug identfying the product. This is the same as the subdomain.
        For example, ``'ldm-151'`` is the slug for ``ldm-151.lsst.io``.
        A full product URL can be provided instead, see ``url``.
    url : `str`, optional
        The full LTD Keeper URL for the product resource. For example,
        ``'https://keeper.lsst.codes/products/ldm-151'``. The ``slug``
        can be provided instead.

    Returns
    -------
    product : `dict`
        Product dataset. See
        https://ltd-keeper.lsst.io/products.html#get--products-(slug)
        for fields.
    """
    if url is None:
        url = "https://keeper.lsst.codes/products/{}".format(slug)

    async with session.get(url) as response:
        data = await response.json()

    return data
