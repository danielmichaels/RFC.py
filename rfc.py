#!/usr/bin/env python3
import time

import logging
import requests
from bs4 import BeautifulSoup
from peewee import *
from requests import ConnectionError
from requests_futures.sessions import FuturesSession

from models import Data, db
from utils import download_rfc_tar, random_header, get_title, get_text, \
    get_categories

logging.basicConfig(level=logging.INFO)


def main():
    start = time.time()
    download_rfc_tar()
    try:
        total_rfc = get_rfc_total()
        iterate_over_rfcs(total_rfc)
        # iterate_over_rfcs(total_rfc=55)  # manual debug only

    except OSError:
        raise

    except ConnectionError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')

    finally:
        end = time.time()
        logging.info(f'This took: {end - start} to run!')




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
        title = get_title(text)
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


if __name__ == '__main__':
    main()
