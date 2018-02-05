"""Client for uploading to LSST the Docs.
"""

import requests
import ltdconveyor


def upload(config):
    """Upload the build documentation site to LSST the Docs.

    Parameters
    ----------
    config : `lander.config.Configuration`
        Site configuration, which includes upload information and credentials.
    """
    token = get_keeper_token(config['keeper_url'],
                             config['keeper_user'],
                             config['keeper_password'])
    build_resource = register_build(config, token)

    ltdconveyor.upload_dir(
        build_resource['bucket_name'],
        build_resource['bucket_root_dir'],
        config['build_dir'],
        aws_access_key_id=config['aws_id'],
        aws_secret_access_key=config['aws_secret'],
        surrogate_key=build_resource['surrogate_key'],
        cache_control='max-age=31536000',
        surrogate_control=None,
        upload_dir_redirect_objects=True)

    confirm_build(config, token, build_resource)


def get_keeper_token(base_url, username, password):
    """Get a temporary auth token from LTD Keeper."""
    token_endpoint = base_url + '/token'
    r = requests.get(token_endpoint, auth=(username, password))
    if r.status_code != 200:
        raise RuntimeError('Could not authenticate to {0}: error {1:d}\n{2}'.
                           format(base_url, r.status_code, r.json()))
    return r.json()['token']


def register_build(config, keeper_token):
    data = {
        'git_refs': [config['git_branch']],
    }

    r = requests.post(
        config['keeper_url'] + '/products/{p}/builds/'.format(
            p=config['ltd_product']),
        auth=(keeper_token, ''),
        json=data)

    if r.status_code != 201:
        raise RuntimeError(r.json())
    build_info = r.json()
    return build_info


def confirm_build(config, keeper_token, build_resource):
    build_url = build_resource['self_url']
    r = requests.patch(build_url,
                       auth=(keeper_token, ''),
                       json={'uploaded': True})
    if r.status_code != 200:
        raise RuntimeError(r)


def get_product(config):
    """Get the /product/<product> resource from LTD Keeper.
    """
    product_url = config['keeper_url'] + '/products/{p}'.format(
        p=config['ltd_product'])
    r = requests.get(product_url)
    if r.status_code != 200:
        raise RuntimeError(r.json())
    product_info = r.json()
    return product_info
