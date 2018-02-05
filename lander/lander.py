"""Coordination infrastructure for making a landing page."""

import os
import shutil

import structlog
from lsstprojectmeta.jsonld import encode_jsonld

from .renderer import create_jinja_env, render_homepage
from . import ltdclient


class Lander(object):
    """Lander coordinates the creation and upload of a landing page for
    a PDF document.
    """

    def __init__(self, config):
        super().__init__()
        self._config = config
        self._logger = structlog.get_logger(__name__)
        self._jinja_env = create_jinja_env()

    def build_site(self):
        if not os.path.isdir(self._config['build_dir']):
            os.makedirs(self._config['build_dir'])

        # Define name of PDF file relative to index.html in built site
        relative_pdf_path = os.path.basename(self._config['pdf_path'])
        self._config['relative_pdf_path'] = relative_pdf_path

        # Add data for HTML title/description tags
        self._config['page_title'] = self._config['title_plain']
        self._config['page_description'] = self._config['abstract_plain']

        # Copy assets (css, js)
        # This algorithm is slightly naieve; we copy the whole built
        # assets directory everytime.
        asset_src_dir = os.path.join(os.path.dirname(__file__), 'assets')
        asset_dest_dir = os.path.join(self._config['build_dir'], 'assets')
        if os.path.isdir(asset_dest_dir):
            shutil.rmtree(asset_dest_dir)
        shutil.copytree(asset_src_dir, asset_dest_dir)

        # Copy PDF
        shutil.copy(self._config['pdf_path'],
                    os.path.join(self._config['build_dir'],
                                 relative_pdf_path))

        # Copy extra downloads. Also determine type for the template to
        # choose an appropriate icon.
        relative_extra_downloads = []
        for download_path in self._config['extra_downloads']:
            relative_path = os.path.basename(download_path)
            shutil.copy(download_path,
                        os.path.join(self._config['build_dir'],
                                     relative_path))
            # determine a type to choose the octicon
            ext = os.path.splitext(relative_path)[-1]
            if ext == ['.pdf']:
                download_type = 'pdf'
            elif ext in ['.tex', '.md', '.txt', '.rst']:
                download_type = 'text'
            elif ext in ['.gz', '.zip']:
                download_type = 'zip'
            elif ext in ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.gif']:
                download_type = 'media'
            elif ext in ['.py', '.h', '.c', '.cpp', '.ipynb', '.json']:
                download_type = 'code'
            else:
                download_type = 'file'
            relative_extra_downloads.append({
                'path': relative_path,
                'type': download_type
            })
        self._config['relative_extra_downloads'] = relative_extra_downloads

        # Write index.html page
        index_html = render_homepage(self._config, self._jinja_env)
        index_html_path = os.path.join(self._config['build_dir'], 'index.html')
        with open(index_html_path, mode='w', encoding='utf-8') as f:
            f.write(index_html)

        # Write metadata file
        jsonld_path = os.path.join(self._config['build_dir'],
                                   'metadata.jsonld')
        self.write_metadata(jsonld_path)

    def write_metadata(self, output_path):
        """Build a JSON-LD dataset for LSST Projectmeta.

        Parameters
        ----------
        output_path : `str`
            File path where the ``metadata.jsonld`` should be written for the
            build.
        """
        if self._config.lsstdoc is None:
            self._logger.info('No known LSST LaTeX source (--tex argument). '
                              'Not writing a metadata.jsonld file.')
            return

        # Build a JSON-LD dataset for the report+source repository.
        product_data = ltdclient.get_product(self._config)
        metadata = self._config.lsstdoc.build_jsonld(
            url=product_data['published_url'],
            code_url=product_data['doc_repo'],
            ci_url='https://travis-ci.org/' + self._config['github_slug'],
            readme_url=None,
            license_id=None)

        json_text = encode_jsonld(
            metadata,
            separators=(',', ':'),  # compact
            ensure_ascii=False)  # unicode output
        with open(output_path, 'w') as f:
            f.write(json_text)

    def upload_site(self):
        """Upload a previously-built site to LSST the Docs."""
        if not os.path.isdir(self._config['build_dir']):
            message = 'Site not built at {0}'.format(self._config['build_dir'])
            self._logger.error(message)
            raise RuntimeError(message)

        ltdclient.upload(self._config)
