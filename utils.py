import logging
import os
import re
import shutil
from bs4 import BeautifulSoup
from random import choice

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


def get_header(text):
    soup = BeautifulSoup(text, 'lxml')
    header = soup.pre.next_element.strip()
    return header.lower()


def get_title(text):
    """Parse's HTML title from each RFC and extracts it for consumption
    elsewhere. Takes response.text has argument. """
    soup = BeautifulSoup(text, 'lxml')
    title = soup.title.text
    return title


def get_text(text):
    """Get only text from the HTML body of each RFC page."""
    soup = BeautifulSoup(text, 'lxml')
    clean_text = soup.body.get_text()
    return clean_text


def cleanup_character_escapes(text):
    """Remove / symbol to stop traversal errors when saving filenames."""
    text = text.replace('/', ' ')
    return text


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


def random_header():
    desktop_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
    return {'User-Agent': choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
