#!/bin/bash

git clone https://github.com/lsst-dm/DMTN-070 _tests/DMTN-070
cd _tests/DMTN-070
docker run --rm -v `pwd`:/workspace -w /workspace lsstsqre/lsst-texmf:latest sh -c 'make'
TRAVIS_COMMIT=2aafb1252b4d8b94342db3dfaa381c3d7e80bab7 TRAVIS_BRANCH=master TRAVIS_REPO_SLUG="lsst-dm/dmtn-070" TRAVIS_JOB_NUMBER=11.1 TRAVIS_PULL_REQUEST=false lander --pdf DMTN-070.pdf --lsstdoc DMTN-070.tex --env=travis --ltd-product dmtn-070
