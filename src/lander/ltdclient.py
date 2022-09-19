"""Client for uploading to LSST the Docs.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

import requests
from ltdconveyor.keeper import confirm_build, get_keeper_token, register_build
from ltdconveyor.s3.presignedpost import prescan_directory, upload_dir

if TYPE_CHECKING:
    from lander.config import Configuration


def upload(config: "Configuration") -> None:
    """Upload the build documentation site to LSST the Docs.

    Parameters
    ----------
    config : `lander.config.Configuration`
        Site configuration, which includes upload information and credentials.
    """
    if config.ltd_user is None or config.ltd_password is None:
        raise RuntimeError("LSST the Docs credentials are not available.")

    token = get_keeper_token(
        config.ltd_url,
        config.ltd_user,
        config.ltd_password.get_secret_value(),
    )
    dirnames = prescan_directory(Path(config.build_dir))
    build_resource = register_build(
        config.ltd_url,
        token,
        config.ltd_product,
        git_refs=[config.git_ref],
        dirnames=dirnames,
    )

    upload_dir(
        post_urls=build_resource["post_prefix_urls"],
        base_dir=Path(config.build_dir),
    )

    confirm_build(build_resource["self_url"], token)


def get_product(config: "Configuration") -> Dict[str, Any]:
    """Get the /product/<product> resource from LTD Keeper."""
    product_url = config.ltd_url + "/products/{p}".format(p=config.ltd_product)
    r = requests.get(product_url)
    if r.status_code != 200:
        raise RuntimeError(r.json())
    product_info = r.json()
    return product_info
