##########
Change Log
##########

[0.1.5] - (2017-07-12)
======================

- Pin to metasrc 0.1.3
- Via metasrc, Lander has improved LaTeX source processing, including handling of referenced source files (``\input`` and ``\include``) and macros (``\def`` and ``\newcommand``).
- Improved treatment of draft status.
  The heuristic is that a document is considered a draft if the branch is not ``master`` and ``lsstdraft`` is not present in a lsstdoc document's options.

[0.1.4] - (2017-07-06)
======================

- Fix logic for determining it Lander is running in a Travis PR environment.
- Log the Lander version at startup.

[0.1.3] - (2017-07-02)
======================

- Fixed Travis deployment issue. Used ``skip_cleanup: true`` to ``.travis.yml`` to prevent CSS and JS assets from bring cleaned up before creating a release.

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
