"""Coordination infrastructure for making a landing page."""

__all__ = ["Lander"]

import os
import shutil
from typing import TYPE_CHECKING

import structlog

from . import ltdclient
from .lsstprojectmeta.jsonld import encode_jsonld
from .renderer import create_jinja_env, render_homepage

if TYPE_CHECKING:
    from lander.config import Configuration


class Lander:
    """Lander coordinates the creation and upload of a landing page for
    a PDF document.
    """

    def __init__(self, config: "Configuration") -> None:
        super().__init__()
        self._config = config
        self._logger = structlog.get_logger("lander")
        self._jinja_env = create_jinja_env()

    def build_site(self) -> None:
        if not os.path.isdir(self._config.build_dir):
            os.makedirs(self._config.build_dir)

        # Copy assets (css, js)
        # This algorithm is slightly naieve; we copy the whole built
        # assets directory everytime.
        asset_src_dir = os.path.join(os.path.dirname(__file__), "assets")
        asset_dest_dir = os.path.join(self._config.build_dir, "assets")
        if os.path.isdir(asset_dest_dir):
            shutil.rmtree(asset_dest_dir)
        shutil.copytree(asset_src_dir, asset_dest_dir)

        # Copy PDF
        shutil.copy(
            self._config.pdf_path,
            os.path.join(
                self._config.build_dir, self._config.relative_pdf_path
            ),
        )

        # Copy extra downloads
        for download_path, relative_download_path in zip(
            self._config.extra_downloads, self._config.relative_extra_downloads
        ):
            shutil.copy(
                download_path,
                os.path.join(
                    self._config.build_dir, relative_download_path["path"]
                ),
            )

        # Write index.html page
        index_html = render_homepage(self._config, self._jinja_env)
        index_html_path = os.path.join(self._config.build_dir, "index.html")
        with open(index_html_path, mode="w", encoding="utf-8") as f:
            f.write(index_html)

        # Write metadata file
        jsonld_path = os.path.join(self._config.build_dir, "metadata.jsonld")
        self.write_metadata(jsonld_path)

    def write_metadata(self, output_path: str) -> None:
        """Build a JSON-LD dataset for LSST Projectmeta.

        Parameters
        ----------
        output_path : `str`
            File path where the ``metadata.jsonld`` should be written for the
            build.
        """
        if self._config.lsstdoc is None:
            self._logger.info(
                "No known LSST LaTeX source (--lsstdoc argument). "
                "Not writing a metadata.jsonld file."
            )
            return

        # Build a JSON-LD dataset for the report+source repository.
        product_data = ltdclient.get_product(self._config)
        metadata = self._config.lsstdoc.build_jsonld(
            url=product_data["published_url"],
            code_url=product_data["doc_repo"],
            ci_url=self._config.ci_url,
            readme_url=None,
            license_id=None,
        )

        json_text = encode_jsonld(
            metadata, separators=(",", ":"), ensure_ascii=False  # compact
        )  # unicode output
        with open(output_path, "w") as f:
            f.write(json_text)

    def upload_site(self) -> None:
        """Upload a previously-built site to LSST the Docs."""
        if not os.path.isdir(self._config.build_dir):
            message = "Site not built at {0}".format(self._config.build_dir)
            self._logger.error(message)
            raise RuntimeError(message)

        ltdclient.upload(self._config)
