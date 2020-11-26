"""Interface to SPDX license metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field, HttpUrl

__all__ = ["SpdxLicense", "SpdxFile", "Licenses"]


class SpdxLicense(BaseModel):
    """A license item as contained in a SpdxFile."""

    name: str
    """Common human-readable name of the license."""

    license_id: str = Field(alias="licenseId")
    """SPDX license identifier."""

    see_also: List[HttpUrl] = Field(alias="seeAlso")
    """"URLs to documentation about this license."""

    is_osi_approved: bool = Field(alias="isOsiApproved")
    """Flag indicating if the license is approved by the OSI
    (Open Software Initiative)
    """


class SpdxFile(BaseModel):
    """Representation of a SPDX license database file as a Pydantic model."""

    licenseListVersion: str
    """Version string of this license file."""

    licenses: List[SpdxLicense]
    """The licenses."""

    @classmethod
    def load_internal(cls) -> SpdxFile:
        """Load an SpdxFile from Lander's package data.

        Returns
        -------
        spdx_file: `SpdxFile`
            The SpdxFile instance from the licenses.json file packaged in
            Lander. This file is a mirror of the canonical license database
            maintained at
            https://github.com/spdx/license-list-data/blob/master/json/licenses.json.
        """
        p = Path(__file__).parent / "data" / "licenses.json"
        return cls.parse_file(p, content_type="application/json")


@dataclass
class Licenses:
    """License database, with access by license ID."""

    licenses: Dict[str, SpdxLicense]
    """Internal license dictionary."""

    @classmethod
    def load(cls) -> Licenses:
        """Load licenses from the SPDX database packaged in Lander.

        Returns
        -------
        licenses : `Licenses`
            The license database instance.
        """
        spdx_file = SpdxFile.load_internal()
        licenses: Dict[str, SpdxLicense] = {
            license.license_id: license for license in spdx_file.licenses
        }
        return cls(licenses=licenses)

    def __getitem__(self, spdx_id: str) -> SpdxLicense:
        return self.licenses[spdx_id]

    def __contains__(self, spdx_id: str) -> bool:
        return spdx_id in self.licenses
