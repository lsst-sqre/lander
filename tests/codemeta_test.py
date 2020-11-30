"""Tests for the lander.codemeta module."""

from __future__ import annotations

import json

from lander.codemeta import CodemetaData, CodemetaPerson


def test_json_export() -> None:
    cmdata = CodemetaData(
        at__id="https://example.com/1234/",
        name="Test document",
        author=[CodemetaPerson(name="Jonathan Sick")],
    )
    # It seems this needs to be set manually; the alias prevents it from
    # being set during the constructor
    cmdata.at__id = "https://example.com/1234/"
    json_str = cmdata.jsonld()

    unencoded = json.loads(json_str)
    assert unencoded["@type"] == ["Report", "SoftwareSourceCode"]
    assert unencoded["@context"] == [
        "https://raw.githubusercontent.com/codemeta/codemeta/2.0-rc/"
        "codemeta.jsonld",
        "http://schema.org",
    ]
    assert unencoded["@id"] == "https://example.com/1234/"
    assert unencoded["author"][0] == {
        "@type": "Person",
        "name": "Jonathan Sick",
    }
