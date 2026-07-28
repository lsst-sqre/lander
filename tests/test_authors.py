"""Tests for author extraction (DM-55645).

Covers LaTeX author parsing from AASTeX-class documents and author
resolution through authors.yaml and the Ook API.

Test data:

- ``tests/data/rtn-126``: AASTeX7, one author with a ``\\c{c}`` cedilla.
- ``tests/data/dmtn-324``: AASTeX 6.3, two authors declared with separate
  ``\\author`` commands.
"""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, Optional

import pytest

from lander import ook
from lander.config import _get_lsstdoc_configuration
from lander.lsstprojectmeta.tex.lsstdoc import LsstLatexDoc

RTN126_DIR = os.path.join(os.path.dirname(__file__), "data", "rtn-126")
DMTN324_DIR = os.path.join(os.path.dirname(__file__), "data", "dmtn-324")

FAKE_AUTHOR_DB: Dict[str, Dict[str, Optional[str]]] = {
    "legetp": {
        "given_name": "Pierre-François",
        "family_name": "Léget",
    },
    "saundersc": {
        "given_name": "Clare",
        "family_name": "Saunders",
    },
    "RubinBuilderPaper": {
        "given_name": None,
        "family_name": "Vera C. Rubin Observatory Team",
    },
}


class FakeResponse:
    def __init__(self, status_code: int, data: Any = None) -> None:
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        return self._data


class FakeSession:
    """Stand-in for requests.Session backed by FAKE_AUTHOR_DB."""

    def get(self, url: str, timeout: Any = None) -> FakeResponse:
        author_id = url.rstrip("/").split("/")[-1]
        try:
            data = dict(FAKE_AUTHOR_DB[author_id])
        except KeyError:
            return FakeResponse(404, {"detail": "not found"})
        data["internal_id"] = author_id
        return FakeResponse(200, data)


@pytest.fixture
def fake_ook_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ook.requests, "Session", FakeSession)


def test_rtn126_latex_authors() -> None:
    """AASTeX7 author with \\c{c} is extracted and accents are converted."""
    doc = LsstLatexDoc.read(os.path.join(RTN126_DIR, "RTN-126.tex"))
    assert doc.authors == ["Pierre-Fran\\c{c}ois L\\'eget"]
    assert doc.plain_authors == ["Pierre-François Léget"]
    assert doc.html_authors == ["Pierre-François Léget"]


def test_dmtn324_latex_authors() -> None:
    """All \\author commands in an AASTeX doc are parsed, not just the
    first.
    """
    doc = LsstLatexDoc.read(os.path.join(DMTN324_DIR, "DMTN-324.tex"))
    assert doc.authors == [
        "Clare Saunders",
        "Pierre-Fran\\c{c}ois L\\'eget",
    ]
    assert doc.plain_authors == [
        "Clare Saunders",
        "Pierre-François Léget",
    ]


def test_load_author_ids() -> None:
    ids = ook._load_author_ids(os.path.join(RTN126_DIR, "authors.yaml"))
    assert ids == ["legetp"]

    ids = ook._load_author_ids(os.path.join(DMTN324_DIR, "authors.yaml"))
    assert ids == ["saundersc", "legetp"]


def test_load_author_ids_missing_file(tmp_path: Any) -> None:
    assert ook._load_author_ids(str(tmp_path / "authors.yaml")) is None


def test_get_authors_from_authors_yaml(fake_ook_api: None) -> None:
    authors = ook.get_authors_from_authors_yaml(DMTN324_DIR)
    assert authors == [
        {"plain": "Clare Saunders", "html": "Clare Saunders"},
        {"plain": "Pierre-François Léget", "html": "Pierre-François Léget"},
    ]


def test_get_authors_family_name_only(
    fake_ook_api: None, tmp_path: Any
) -> None:
    """Pseudo-authors like RubinBuilderPaper have no given name."""
    (tmp_path / "authors.yaml").write_text("- RubinBuilderPaper\n")
    authors = ook.get_authors_from_authors_yaml(str(tmp_path))
    assert authors == [
        {
            "plain": "Vera C. Rubin Observatory Team",
            "html": "Vera C. Rubin Observatory Team",
        }
    ]


def test_get_authors_html_escaping(
    fake_ook_api: None,
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        FAKE_AUTHOR_DB,
        "escapee",
        {"given_name": "A <B>", "family_name": "C & D"},
    )
    (tmp_path / "authors.yaml").write_text("- escapee\n")
    authors = ook.get_authors_from_authors_yaml(str(tmp_path))
    assert authors == [
        {"plain": "A <B> C & D", "html": "A &lt;B&gt; C &amp; D"}
    ]


def test_get_authors_no_yaml(fake_ook_api: None, tmp_path: Any) -> None:
    assert ook.get_authors_from_authors_yaml(str(tmp_path)) is None


def test_get_authors_unknown_id_falls_back(
    fake_ook_api: None, tmp_path: Any
) -> None:
    """An ID the Ook API can't resolve triggers full fallback (None) so a
    partial author list is never exported.
    """
    (tmp_path / "authors.yaml").write_text("- saundersc\n- nosuchid\n")
    assert ook.get_authors_from_authors_yaml(str(tmp_path)) is None


def test_get_authors_malformed_yaml(fake_ook_api: None, tmp_path: Any) -> None:
    (tmp_path / "authors.yaml").write_text("key: value\n")
    assert ook.get_authors_from_authors_yaml(str(tmp_path)) is None


def test_lsstdoc_configuration_prefers_ook(fake_ook_api: None) -> None:
    """The document configuration uses Ook-resolved authors when
    authors.yaml is present.
    """
    config = _get_lsstdoc_configuration(
        os.path.join(DMTN324_DIR, "DMTN-324.tex")
    )
    assert config["authors"] == [
        {"plain": "Clare Saunders", "html": "Clare Saunders"},
        {"plain": "Pierre-François Léget", "html": "Pierre-François Léget"},
    ]


def _git_init_and_commit(tmp_path: Any) -> None:
    """Make tmp_path a Git repo with one commit (the revision-date
    fallback requires the document to be in a Git repo).
    """
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, env=env, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "init"],
        cwd=tmp_path,
        env=env,
        check=True,
    )


def test_lsstdoc_configuration_latex_fallback(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without authors.yaml, authors come from the LaTeX source."""
    for name in ("RTN-126.tex", "authors.tex", "abstract.tex", "body.tex"):
        (tmp_path / name).write_text(
            open(os.path.join(RTN126_DIR, name)).read()
        )
    _git_init_and_commit(tmp_path)
    config = _get_lsstdoc_configuration(str(tmp_path / "RTN-126.tex"))
    assert config["authors"] == [
        {"plain": "Pierre-François Léget", "html": "Pierre-François Léget"}
    ]


def test_uses_generated_authors() -> None:
    assert ook.uses_generated_authors(os.path.join(RTN126_DIR, "RTN-126.tex"))
    assert ook.uses_generated_authors(
        os.path.join(DMTN324_DIR, "DMTN-324.tex")
    )


def test_uses_generated_authors_variants(tmp_path: Any) -> None:
    doc = tmp_path / "doc.tex"

    doc.write_text("\\input{authors.tex}\n")
    assert ook.uses_generated_authors(str(doc))

    doc.write_text("\\input { authors }\n")
    assert ook.uses_generated_authors(str(doc))

    # Commented-out input does not count
    doc.write_text("%\\input{authors}\n\\author{Someone Else}\n")
    assert not ook.uses_generated_authors(str(doc))

    doc.write_text("\\author{A. Author}\n")
    assert not ook.uses_generated_authors(str(doc))

    assert not ook.uses_generated_authors(str(tmp_path / "missing.tex"))


def test_lsstdoc_configuration_stale_authors_yaml(
    fake_ook_api: None, tmp_path: Any
) -> None:
    """A document with a hand-written \\author command and a stale
    authors.yaml (input of authors.tex commented out) uses the LaTeX
    authors, not the Ook resolution.
    """
    for name in ("RTN-126.tex", "authors.tex", "abstract.tex", "body.tex"):
        (tmp_path / name).write_text(
            open(os.path.join(RTN126_DIR, name)).read()
        )
    source = (tmp_path / "RTN-126.tex").read_text()
    source = source.replace(
        "\\input{authors}",
        "%\\input{authors}\n\\author{NSF-DOE Vera C. Rubin Observatory}",
    )
    (tmp_path / "RTN-126.tex").write_text(source)
    (tmp_path / "authors.yaml").write_text("- legetp\n")
    _git_init_and_commit(tmp_path)
    config = _get_lsstdoc_configuration(str(tmp_path / "RTN-126.tex"))
    assert config["authors"] == [
        {
            "plain": "NSF-DOE Vera C. Rubin Observatory",
            "html": "NSF-DOE Vera C. Rubin Observatory",
        }
    ]
