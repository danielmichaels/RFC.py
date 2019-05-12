"""
Publish a new version:
$ check README and setup.py are correctly versioned
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    // ABOVE ONLY FOR TESTING
$ twine upload -r pypi dist/*
"""

from setuptools import setup, find_packages

NAME = "RFC.py"
VERSION = "2019.5.1"
DESCRIPTION = (
    "A simple python client that offers users the ability to search"
    " for, read and bookmark RFC's from the Internet Engineering "
    "Task Force whilst offline."
)
URL = "https://github.com/danielmichaels/RFC.py"
DOWNLOAD_URL = URL + "/tarball/" + VERSION
AUTHOR = "Daniel Michaels"
AUTHOR_EMAIL = "dans.address@outlook.com"
REQUIRES_PYTHON = ">= Python 3.6"

# Include what dependencies it requires:
REQUIRED = ["requests", "click", "peewee", "responses"]

entry_points = {"console_scripts": [["rfc = rfcpy.rfc:main"]]}


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    install_requires=REQUIRED,
    entry_points=entry_points,
    include_package_data=True,
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
