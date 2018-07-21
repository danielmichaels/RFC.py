import logging
import os
import re
import shutil
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


class Config:
    STORAGE_PATH = 'test_rfc/'
    DATABASE = 'database.db'
    DATABASE_PATH = os.path.join(os.getcwd(), DATABASE)
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]


def get_categories(text):
    """Parse through each text file searching for the IETF's categories.

    :arg text from rfc txt file

    :return any matched category, if not found or rfc not does not give a
            category return "uncategorised".
    """
    header = text[:500]
    categories = [
        "Standards Track", "Informational", "Experimental", "Historic",
        "Best Current Practice", "Proposed Standard", "Internet Standard"
    ]
    match = [x for x in [re.findall(x.title(), header.title())
                         for x in categories] if len(x) > 0]
    try:
        return match[0][0]
    except IndexError:
        return "Uncategorised"


def get_title_list():
    list_of_tiles = list()
    with open(os.path.join(Config.STORAGE_PATH, 'rfc-index.txt'), 'r') as f:
        f = f.read().strip()
        search_regex = '^([\d{1,4}])([^.]*).'
        result = re.finditer(search_regex, f, re.M)
        for title in result:
            list_of_tiles.append(title[0])
    return list_of_tiles


def map_title_from_list(number, title_list):
    result = [title for title in title_list if number in title]
    if result:
        return result[0]
    return None


def get_text(text):
    """Get only text from the HTML body of each RFC page."""
    soup = BeautifulSoup(text, 'lxml')
    clean_text = soup.body.get_text()
    return clean_text


def strip_extensions():
    """Strips away all non txt files from directory listing.

    :return clean_list: generator of files with unwanted items removed
                        note: time for listcomp = 45s v genexp = 24s
    """

    _, _, files = next(os.walk('test_rfc/'))
    dirty_extensions = ['a.txt', 'rfc-index.txt', '.pdf', '.ps', '.ta']
    clean_list = (x for x in files
                  if not any(xs in x for xs in dirty_extensions))
    return clean_list


def remove_rfc_files():
    shutil.rmtree(Config.STORAGE_PATH)


def sanitize_inputs(inputs):
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub(' ', inputs)
