RTN-126 test data
=================

Frozen snapshot of https://github.com/lsst/rtn-126 at commit
``f36d5f3c5dd2a66098078ce0ed378c4410212a63`` (2026-07-28) for DM-55645
regression tests.

This is an AASTeX7-class document with a single author whose name uses the
``\c{c}`` cedilla accent (``Pierre-Fran\c{c}ois L\'eget``).

``authors.tex`` is not in the source repository; it was generated from
``authors.yaml`` exactly as the document's CI does::

    python lsst-texmf/bin/db2authors.py -m aas7 > authors.tex
