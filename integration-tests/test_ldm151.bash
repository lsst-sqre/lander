#!/bin/bash

git clone https://github.com/lsst/LDM-151 _tests/LDM-151
cd _tests/LDM-151
docker run --rm -v `pwd`:/workspace -w /workspace lsstsqre/lsst-texmf:latest sh -c 'make'
TRAVIS_COMMIT=2aafb1252b4d8b94342db3dfaa381c3d7e80bab7 TRAVIS_BRANCH=master TRAVIS_REPO_SLUG="lsst/LDM-151" TRAVIS_JOB_NUMBER=11.1 TRAVIS_PULL_REQUEST=false lander --pdf LDM-151.pdf --lsstdoc LDM-151.tex --env=travis --ltd-product ldm-151
