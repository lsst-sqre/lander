"""GitHub integration installation authentication.

https://developer.github.com/early-access/integrations/authentication/
"""

import datetime

import jwt
import requests

__all__ = ["create_jwt", "get_installation_token"]


def get_installation_token(installation_id, integration_jwt):
    """Create a GitHub token for an integration installation.

    Parameters
    ----------
    installation_id : `int`
        Installation ID. This is available in the URL of the integration's
        **installation** ID.
    integration_jwt : `bytes`
        The integration's JSON Web Token (JWT). You can create this with
        `create_jwt`.

    Returns
    -------
    token_obj : `dict`
        GitHub token object. Includes the fields:

        - ``token``: the token string itself.
        - ``expires_at``: date time string when the token expires.

    Example
    -------
    The typical workflow for authenticating to an integration installation is:

    .. code-block:: python

       from dochubadapter.github import auth

       jwt = auth.create_jwt(integration_id, private_key_path)
       token_obj = auth.get_installation_token(installation_id, jwt)
       print(token_obj["token"])

    Notes
    -----
    See
    https://developer.github.com/early-access/integrations/authentication/#as-an-installation
    for more information
    """
    api_root = "https://api.github.com"
    url = "{root}/installations/{id_:d}/access_tokens".format(
        root=api_root, id_=installation_id
    )

    headers = {
        "Authorization": "Bearer {0}".format(integration_jwt.decode("utf-8")),
        "Accept": "application/vnd.github.machine-man-preview+json",
    }

    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def create_jwt(integration_id, private_key_path):
    """Create a JSON Web Token to authenticate a GitHub Integration or
    installation.

    Parameters
    ----------
    integration_id : `int`
        Integration ID. This is available from the GitHub integration's
        homepage.
    private_key_path : `str`
        Path to the integration's private key (a ``.pem`` file).

    Returns
    -------
    jwt : `bytes`
        JSON Web Token that is good for 9 minutes.

    Notes
    -----
    The JWT is encoded with the RS256 algorithm. It includes a payload with
    fields:

    - ``'iat'``: The current time, as an `int` timestamp.
    - ``'exp'``: Expiration time, as an `int timestamp. The expiration
      time is set of 9 minutes in the future (maximum allowance is 10 minutes).
    - ``'iss'``: The integration ID (`int`).

    For more information, see
    https://developer.github.com/early-access/integrations/authentication/.
    """
    integration_id = int(integration_id)

    with open(private_key_path, "rb") as f:
        cert_bytes = f.read()

    now = datetime.datetime.now()
    expiration_time = now + datetime.timedelta(minutes=9)
    payload = {
        # Issued at time
        "iat": int(now.timestamp()),
        # JWT expiration time (10 minute maximum)
        "exp": int(expiration_time.timestamp()),
        # Integration's GitHub identifier
        "iss": integration_id,
    }

    return jwt.encode(payload, cert_bytes, algorithm="RS256")
