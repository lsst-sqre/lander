DMTN-324 test data
==================

Frozen snapshot of https://github.com/lsst-dm/dmtn-324 at commit
``6398df1603126a2816a1fe34c9327515af870177`` (2026-07-28) for DM-55645
regression tests.

This is an AASTeX 6.3-class document with two authors, each declared with
its own ``\author[orcid]{name}`` command (unlike lsstdoc's single
``\author{A, B, and C}`` command). The second author's name uses LaTeX
accents (``Pierre-Fran\c{c}ois L\'eget``).

``authors.tex`` is not in the source repository; it was generated from
``authors.yaml`` exactly as the document's CI does::

    python lsst-texmf/bin/db2authors.py > authors.tex
