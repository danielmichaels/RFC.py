#!/usr/bin/env python3
from time import time

import asks
import logging
import os
import pathlib
import requests
from bs4 import BeautifulSoup
from peewee import *
from random import choice
from requests import ConnectionError
from requests_futures.sessions import FuturesSession

from models import Data, db

asks.init('trio')
logging.basicConfig(level=logging.INFO)


def main():
    try:
        total_rfc = get_rfc_total()
        start = time()
        iterate_over_rfcs(total_rfc)
        # iterate_over_rfcs(total_rfc=55)  # manual debug only
        end = time()
        logging.info(f'This took: {end - start} to run!')

    except OSError:
        raise

    except ConnectionError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')


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


def iterate_over_rfcs(total_rfc):
    """Iterate over the RFC list, checking to see if any RFC files already
    exist in the folder and if not download a copy into the specified folder.

    :arg takes in the total number of RFC's as the max_length in range()."""

    session = FuturesSession(max_workers=10)
    for num in range(1, total_rfc):
        # for num in range(50, total_rfc):
        url = f"https://tools.ietf.org/html/rfc{num}"
        # check if rfc already exists in db
        future = session.get(url, headers=random_header())
        resp = future.result()
        if resp.status_code == 200:
            text = resp.text
            logging.info(f'RFC{num} inserted')
            write_to_db(num, text)
        else:
            print(f"RFC {num:04d} Exists.. Skipping..")

    else:
        print(f"RFC {num:04d} DOES NOT EXIST")


def write_to_db(num, text):

    try:
        number = int(num)
        title = get_filename(text)
        body = get_text(text)
        category = get_categories(text)
        bookmark = False

        with db.atomic():
            Data.create(number=number, title=title, text=body,
                        category=category,
                        bookmark=bookmark)

    except IntegrityError as e:
        logging.error(f'Integrity Error: {e} Raised!')
    except AttributeError as e:
        # maybe needs a time out takes ~ 5-7s + before raising error (rfc51)
        logging.error(f'{e} hit at RFC {num}')
        pass


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


def get_filename(text):
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


def get_rfc_total():
    """Reach out to rfc-editor.org and scrape the table to get the total
    number of RFC's available for download. This is used as the max value in
    :func: iterate_over_rfcs

    :returns total number of RFC's according to RFC tabular data."""

    url = 'https://www.rfc-editor.org/rfc-index.html'
    resp = requests.get(url)
    text = resp.text
    soup = BeautifulSoup(text, 'lxml')
    tables = soup.find_all('table')
    rfc_table = tables[2].find_all('tr')
    logging.info(f'Number of RFC\'s available for download: {len(rfc_table)}')
    return len(rfc_table)


def check_folder_exists():
    # keep if need boiler plate for later
    """Create the folder that stores all the RFC files if it does not exist."""
    folder = os.path.join(pathlib.Path.home(), 'Code/RFC list')
    try:
        if not os.path.exists(folder):
            logging.info('Folder doesn\'t exist...')
            os.makedirs(folder)
            logging.info(f'Folder: {folder} created!')
        else:
            logging.info(f'{folder} already exists.')
    except OSError:
        raise


if __name__ == '__main__':
    main()
