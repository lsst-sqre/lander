from io import open
import os

from setuptools import setup
import versioneer


packagename = 'lander'
description = ('HTML landing page generator for LSST PDF documentation '
               'deployed from Git to LSST the Docs.')
author = 'Association of Universities for Research in Astronomy, Inc.'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/lander'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()


long_description = read('README.rst')


setup(
    name=packagename,
    version=versioneer.get_version(),
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
        'Programming Language :: Python :: 3.6',
    ],
    keywords='lsst',
    packages=['lander'],
    install_requires=[
        'python-dateutil>=2.6.0',
        'Jinja2==2.9.6',
        'structlog==17.1.0',
        'ltd-conveyor==0.3.1',
        'requests==2.14.2',
        'lsst-projectmeta-kit==0.3.0'
    ],
    extras_require={
        'dev': [
            # Development/testing dependencies
            'pytest==3.2.5',
            'pytest-cov==2.5.0',
            'pytest-flake8==0.9.1'
        ]},
    package_data={'lander': [
        'assets/*.svg',
        'assets/*.css',
        'assets/*.js',
        'templates/*'
    ]},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'lander = lander.main:main'
        ]
    },
    cmdclass=versioneer.get_cmdclass()
)
