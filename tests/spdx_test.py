"""Tests for the lander.spdx module."""

from __future__ import annotations

from lander.spdx import Licenses, SpdxFile, SpdxLicense


def test_spdxfile() -> None:
    spdx_file = SpdxFile.load_internal()
    assert isinstance(spdx_file, SpdxFile)


def test_licenses() -> None:
    licenses = Licenses.load()

    assert "MIT" in licenses
    mit_license = licenses["MIT"]
    assert isinstance(mit_license, SpdxLicense)
    assert mit_license.name == "MIT License"
    assert mit_license.see_also[0] == "https://opensource.org/licenses/MIT"
