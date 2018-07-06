import time

import requests
import shutil
from bs4 import BeautifulSoup
from random import choice


def download_rfc_tar():
    """Download all RFC's from IETF in a tar.gz for offline sorting."""
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    # Takes ~ 130s to DL on my connection
    t1 = time.time()
    r = requests.get(URL, stream=True)
    if r.status_code == 200:
        with open('test.tar.gz', 'wb') as f:
            # replace test.tar.gz with ~/.rfc in future
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        print(f'Time taken in seconds: {time.time() - t1}')


def get_categories(text):
    header = get_header(text)
    categories = [
        "Standards Track", "Informational", "Experimental", "Historic",
        "Best Current Practice", "Proposed Standard", "Internet Standard"
    ]
    # link proposed and internet standard into Standards Track folder.
    for category in categories:
        if category.lower() in header:
            return category
        if category.lower() not in header:
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
