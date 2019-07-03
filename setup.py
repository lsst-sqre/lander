from pathlib import Path

from setuptools import setup


packagename = 'lander'
description = ('HTML landing page generator for LSST PDF documentation '
               'deployed from Git to LSST the Docs.')
author = 'Association of Universities for Research in Astronomy, Inc.'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/lander'
long_description = (Path(__file__).parent / 'README.rst').read_text()


setup(
    name=packagename,
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
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'python-dateutil>=2.6.0',
        'Jinja2>=2.10.1',
        'structlog==17.1.0',
        'ltd-conveyor==0.3.1',
        'requests==2.20.0',
        'lsst-projectmeta-kit==0.3.5'
    ],
    extras_require={
        'dev': [
            # Development/testing dependencies
            'pytest==4.2.1',
            'pytest-cov==2.6.1',
            'pytest-flake8==1.0.4'
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
    }
)
