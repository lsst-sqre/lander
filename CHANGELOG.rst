##########
Change Log
##########

0.1.16 (2019-07-04)
===================

- Update Jinja to >=2.10.1 to address CVE-2019-10906.
- Update asset build pipeline to Gulp 4 and update all other npm dependencies at the same time.

0.1.15 (2019-04-02)
===================

- Update to ``lsst-projectmeta-kit`` to 0.3.5 for better author parsing.
- Update ``requests`` to 2.20.0 (security).

0.1.14 (2019-02-18)
===================

- Lander will now cleanly abort when building on Travis CI, but the secure environment variables are not available.
  This happens if the build is triggered by a fork.
- Switched to use ``$TRAVIS_BUILD_WEB_URL`` to get a URL to the build.
  This is better than computing the build URL during the travis-ci.org to travis-ci.com transition.
- Updated test dependencies to pytest 4.2.1.
- Switched to ``setuptools_scm`` for version string management.

0.1.13 (2018-11-26)
===================

- Update to lsst-projectmeta-kit 0.3.3 for improved detection of ``\input`` and ``\include`` commands in TeX source.

0.1.12 (2018-02-10)
===================

- Update to ``lsst-projectmeta-kit`` 0.3.1 for more reliable ``metadata.jsonld`` generation (works around pandoc issues converting some documents to plain text).
  There's a new integration test ``make dmtn070`` that demos this.
- Improve the testing strategy:
  - Run ``make pytest`` to run pytest with the correct arguments instead of using ``--add-opts`` in setup.cfg.
    This lets us run ``pytest`` directly with ad hoc arguments.
  - Run ``make test`` to run both pytest and the integration tests.

0.1.11 (2018-02-07)
===================

- Lander now creates and uploads a ``metadata.jsonld`` document alongside the landing page content (e.g., ``index.html``).
  This content can be ingested by other tools into the LSST Projectmeta database.
- Switch from metasrc to lsst-projectmeta-kit 0.3.0.
  It's the same package, but the new and rebranded lsst-projectmeta-kit includes the ability to generate JSON-LD from an ``LsstLatexDoc`` object.

0.1.10 (2017-12-11)
===================

- Change known domain for DocuShare from ``docushare.lsstcorp.org`` to ``docushare.lsst.org``.
  This ensures that ``ls.st`` short links can continue to be verified.
- Create default values for ``abstract_plain`` and ``title_plain``.
  This fixes cases where the abstract is not set in the underlying LaTeX document.

0.1.9 (2017-11-20)
==================

- Update metasrc to 0.2.2 to resolve issues with auto-downloading Pandoc in Travis CI (`DM-12569 <https://jira.lsstcorp.org/browse/DM-12569>`_).
- Update pytest to 3.2.5 and pytest-flake8 to 0.9.1 to fix incompatibilities in the floating indirect dependencies.

0.1.8 (2017-10-09)
==================

- Update metasrc to 0.2.1
- Use metasrc's ``LsstLatexDoc.revision_datetime`` to obtain the date of a document.
  This method uses a combination of parsing the ``\date`` LaTeX command, looking at content
  Git commits, and falling back to 'now' to get an appropriate timestamp.

0.1.7 (2017-09-28)
==================

- Update metasrc to 0.2.0.
  This provides Pandoc integration for improved HTML rendering of content extracted from LaTeX documents.
- Improve how loggers are configured (warning level for third-party loggers, and info/debug levels for first-party LSST SQuaRE code).

0.1.6 (2017-09-07)
==================

- Update metasrc to 0.1.4.
  This update provides improved LaTeX command metadata extraction.
  (`DM-11821 <https://jira.lsstcorp.org/browse/DM-11821>`_)
- Temporarily skip ls.st and DocuShare-related unit tests because ls.st links to DocuShare are broken due to the DocuShare upgrade.

0.1.5 (2017-07-12)
==================

- Pin to metasrc 0.1.3
- Via metasrc, Lander has improved LaTeX source processing, including handling of referenced source files (``\input`` and ``\include``) and macros (``\def`` and ``\newcommand``).
- Improved treatment of draft status.
  The heuristic is that a document is considered a draft if the branch is not ``master`` and ``lsstdraft`` is not present in a lsstdoc document's options.

0.1.4 (2017-07-06)
==================

- Fix logic for determining it Lander is running in a Travis PR environment.
- Log the Lander version at startup.

0.1.3 (2017-07-02)
==================

- Fixed Travis deployment issue. Used ``skip_cleanup: true`` to ``.travis.yml`` to prevent CSS and JS assets from bring cleaned up before creating a release.

0.1.2 (2017-06-27)
==================

- Detect if running from a Travis PR build (using the ``TRAVIS_PULL_REQUEST`` environment variable) and if so, abort the page build and upload.
  This is to prevent duplicate uploads from both branch and PR-based Travis jobs.
- Pin inuitcss to 6.0.0-beta4 because of the removal of rem functions in beta5.

0.1.1 (2017-06-17)
==================

- Update to ``metasrc>=0.1.1,<0.2``.
- Use ``remove_comments`` and ``remove_trailing_whitespace`` feature from metasrc.
  This improves the accuracy of metadata extraction from tex source.
  For example, comment characters won't appear in extract abstract content.

0.1.0 (2017-05-24)
==================

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
