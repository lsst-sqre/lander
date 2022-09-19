###################################
GitHub v4 (GraphQL) Query Templates
###################################

This directory contains GraphQL queries for the GitHub v4 API.

technote_repo
=============

Get information about an LSST technote's GitHub repository.
Used by ``lsstprojectmeta.technote``.

Variables
---------

- ``org_name``: Repository owner or organization (``str``).
- ``repo_name``: Repository name (``str``).
