"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.p sdist
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    // ABOVE ONLY FOR TESTING
$ twine upload -r pypi dist/*
"""

from codecs import open
from os import path
from setuptools import setup, find_packages

NAME = 'RFC.py'
VERSION = '1.1'
DESCRIPTION = "A simple python client that offers users the ability to search" \
              " for, read and bookmark RFC's from the Internet Engineering " \
              "Task Force whilst offline."
URL = 'https://github.com/danielmichaels/RFC.py'
DOWNLOAD_URL = (URL + '/tarball/' + VERSION)
AUTHOR = 'Daniel Michaels'
AUTHOR_EMAIL = 'dans.address@outlook.com'
REQUIRES_PYTHON = '>= Python 3.6'

# Include what dependencies it requires:
REQUIRED = [
    'requests',
    'click',
    'peewee'
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    packages=find_packages(exclude=('tests')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ]
)
