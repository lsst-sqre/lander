##########
Change Log
##########

[0.1.2] - (2017-06-27)
======================

- Detect if running from a Travis PR build (using the ``TRAVIS_PULL_REQUEST`` environment variable) and if so, abort the page build and upload.
  This is to prevent duplicate uploads from both branch and PR-based Travis jobs.
- Pin inuitcss to 6.0.0-beta4 because of the removal of rem functions in beta5.

[0.1.1] - (2017-06-17)
======================

- Update to ``metasrc>=0.1.1,<0.2``.
- Use ``remove_comments`` and ``remove_trailing_whitespace`` feature from metasrc.
  This improves the accuracy of metadata extraction from tex source.
  For example, comment characters won't appear in extract abstract content.

[0.1.0] - (2017-05-24)
======================

Initial version.

- Native PDF display via `PDFObject <https://pdfobject.com>`_.
- Multi-level metadata model for populating the landing page.
  Lander uses https://github.com/lsst-sqre/metasrc to extract content from the ``tex`` source (more work on this is needed).
  Otherwise, it gets data from environment variables (including Travis CI variables).
  Finally, metadata can be specified explicitly with command line arguments.
- Uses https://github.com/lsst-sqre/squared for CSS, icons, and logos.
  A Gulp and webpack workflow build these sources into deployable dependencies.
  Gulp and webpack are only needed by developers and CI; the deployable artifacts are included in PyPI releases.
- Release workflow is fully automated in Travis.
  Create a PEP 440 version tag, push it, and the release appears in PyPI.
- Includes an LSST the Docs upload client (via https://github.com/lsst-sqre/ltd-conveyor) built-in so that https://github.com/lsst-sqre/ltd-mason isn't required.
- Usage and development docs are currently in the README.
