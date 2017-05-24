######
Lander
######

.. image:: https://img.shields.io/pypi/v/lander.svg
   :target: https://pypi.python.org/pypi/lander
   :alt: Python Package Index
.. image:: https://img.shields.io/travis/lsst-sqre/lander.svg
   :target: https://travis-ci.org/lsst-sqre/lander
   :alt: Travis CI build status

**HTML landing page generator for LSST PDF documentation deployed from Git to LSST the Docs.**

Installation
============

Lander works with Python 3.5 or above.
You can install it from PyPI::

  pip install lander

Run ``lander -h`` for command line help.

Usage
=====

Basic usage
-----------

To create a landing page website, run ``lander`` with the local PDF file's path::

  lander --pdf <path>

The built PDF landing page site is available, by default, from the ``_build`` directory.
View the site in a browser by running a Python web server::

   cd _build && python -m http.server 8000 --bind 127.0.0.1

Get metadata from an lsstdoc document
-------------------------------------

With the ``--lsstdoc <tex path>`` argument, Lander will attempt to scrape metadata from the source of a ``lsstdoc``-class LaTeX file, including:

- abstract
- authors
- document handle
- title

Note that Lander does not convert LaTeX commands to HTML.
In these cases, the metadata needs to be added explicitly.
We plan to address this in future releases.

See https://lsst-texmf.lsst.io for information about the ``lsstdoc`` class.

Get metadata from the Travis environment
----------------------------------------

If you're running on Travis CI, set the ``--env=travis`` to get metadata from Travis's environment variables:

- ``$TRAVIS_COMMIT``
- ``$TRAVIS_BRANCH``
- ``$TRAVIS_TAG``
- ``$TRAVIS_REPO_SLUG``
- ``$TRAVIS_JOB_NUMBER``

Overriding metadata
-------------------

Lander tries to get as much metadata from the environment as possible, but sometimes this isn't possible or usable.
For example, Lander can't (yet) convert LaTeX expressions into HTML.
In this case you can explicitly set metadata with these flags (see ``lander -h`` for more information):

- ``--abstract``
- ``--authors``
- ``--title``
- ``--handle`` (such as ``LDM-151``)
- ``--repo-url`` (such as ``https://github.com/lsst/ldm-151``)
- ``--repo-branch`` (such as ``master``)
- ``--date`` (such as ``2017-05-22``)
- ``--docushare-url`` (prefer the multi-version form, ``https://ls.st/ldm-151*``)

``--authors`` should be a JSON-formatted array, even for a single author.
For example::

  --authors "[\"First Author\", \"Second Author\"]"

Distributing extra files from the landing page
----------------------------------------------

To include ancillary files with the main PDF document, provide their file paths with the ``--extra-downloads`` argument.
These extra files are listed in the **Downloads** section of the landing page.
The main PDF is always included first in this list.

For example::

   --extra-downloads demo.ipynb

Uploading to LSST the Docs
--------------------------

Lander works well with LSST the Docs.
Lander can upload pages directly to LSST the Docs for you with these configurations:

- ``--upload`` — provide this flag to indicate a build should be uploaded.
- ``--ltd-product`` — Name of the product on LSST the Docs.
- ``--keeper-url`` or ``$LTD_KEEPER_URL``.
- ``--keeper-user`` or ``$LTD_KEEPER_USER``.
- ``--keeper-password`` or ``$LTD_KEEPER_PASSWORD``.
- ``--aws-id`` or ``$LTD_AWS_ID``.
- ``--aws-secret`` or ``$LTD_AWS_SECRET``.

Note: these are advanced configurations and are typically added to a CI configuration automatically or by a Documentation Engineer.
Reach out to `#dm-docs <https://lsstc.slack.com/messages/C2B6DQBAL/>`_ on Slack for help.

Development workflow
====================

You need both Python 3.5+ and `node.js`_ to develop Lander.

Initial set up
--------------

Clone and install dependencies (use a Python virtual environment of your choice)::

   git clone https://github.com/lsst-sqre/lander
   cd lander
   npm install
   gulp assets
   pip install -r requirements.txt
   python setup.py develop

Run Python tests and linting
----------------------------

We use pytest::

   pytest

Build a test site
-----------------

The default gulp_ workflow create website assets and generates a test website::

   gulp

This gulp task runs a browsersync_ server and refreshes the page whenever CSS, JavaScript, or HTML assets change.

Only build assets
-----------------

If you want to only build CSS, icon, and JavaScript assets, run this task::

   gulp assets --env=deploy

This is how assets are built on CI for releases of Lander.

Developing CSS/Sass with squared
--------------------------------

Lander uses squared_ for visual design.
All Lander CSS should be committed to the squared_ repo so that LSST SQuaRE web projects share a common visual language.

To make it easier to write Sass in squared_ while developing landing pages in Lander, we recommend linking a clone of squared_ to Lander's ``node_modules``. 
Assuming you're starting from the ``lander/`` root directory::

  git clone https://github.com/lsst-sqre/squared ../squared
  npm link ../squared

Some patterns:

- If you're working on a branch in squared_, then update squared's version in ``package.json`` to that branch.
  For example: ``"squared": "lsst-sqre/squared#tickets/DM-10503"``.
  This allows Travis to install the development version of squared_ when testing Lander.
  Remember to make a release of squared_ before releasing a new version of Lander, see below.

- ``scss/app.scss`` in the lander repo imports Sass partials from squared_ and other packages (including inuitcss_).

Release workflow
================

1. If squared_ was modified, create a squared_ release first.
2. Update ``package.json`` with the released version of squared_.
   Using tagged npm releases is preferred to GitHub branches to make builds of releases repeatable.
3. Create a signed tag: ``git tag -s 0.1.0 -m "v0.1.0"``. Use the `PEP 440`_ schema.
4. Push the tag: ``git push --tags``. This will automatically create a Lander release on PyPI.
5. Merge the development branch as necessary.

License
=======

This project is open sourced under the MIT license.
See `LICENSE <./LICENSE>`_ for details.

.. _squared: https://github.com/lsst-sqre/squared
.. _`PEP 440`: https://www.python.org/dev/peps/pep-0440/
.. _inuitcss: https://github.com/inuitcss/inuitcss
.. _browsersync: https://browsersync.io
.. _gulp: http://gulpjs.com
.. _node.js: https://nodejs.org/en/
