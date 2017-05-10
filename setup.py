from io import open
import os

from setuptools import setup, find_packages


packagename = 'lander'
description = ('HTML landing page generator for LSST PDF documentation '
               'deployed from Git to LSST the Docs.')
author = 'Association of Universities for Research in Astronony, Inc.'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/'
version = '0.1.0'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()


long_description = read('README.rst')


setup(
    name=packagename,
    version=version,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    install_requires=[],
    # package_data={},
    entry_points={
        'console_scripts': [
            'lander = lander.main:main'
        ]
    }
)
