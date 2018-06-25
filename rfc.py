#!/usr/bin/env python3
# TODO: categorise into types
# TODO: change url and get html version
# TODO: parse html get Title & Number --> RFC {num} - {title}.txt
# TODO: categorise files and sort into folders by category
from random import choice
from time import time
from requests import ConnectionError
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

import logging
import os
import pathlib
import requests

logging.basicConfig(level=logging.INFO)


def main():
    try:
        total_rfc = get_rfc_total()
        logging.info(f'Current total of published RFC\'s: {total_rfc}')
        check_folder_exists()
        folder = os.path.join(pathlib.Path.home(), 'Code/RFC list')
        os.chdir(folder)
        logging.info(f'changed dir to: {folder}')
        start = time()
        iterate_over_rfcs(total_rfc)
        end = time()
        logging.info(f'This took: {end - start} to run!')

    except OSError:
        raise

    except ConnectionError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')

    finally:
        logging.info(f'Total number RFC text files: {len(os.listdir())}')
        cur_dir = pathlib.Path(__file__).parent
        logging.info(f'changed dir to: {cur_dir}')


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
        url = f"https://tools.ietf.org/html/rfc{num}"
        if not [file for file in os.listdir() if
                file.startswith(f"RFC {num}")]:
            future = session.get(url, headers=random_header())
            resp = future.result()
            if resp.status_code == 200:
                text = resp.text
                write_to_file(num, text)
        else:
            print(f"RFC {num:04d} Exists.. Skipping..")

    else:
        print(f"RFC {num:04d} DOES NOT EXIST")


def write_to_file(num, text):
    """Function that creates text files from the RFC website.

    :argument num: takes the RFC number as part of the filename
    :argument text: writes the response text from the webpage into the file.
    :argument filename: takes filename from :func: check_exists
    """
    try:
        filename = get_filename(text)
        filename = cleanup_character_escapes(filename)
        text = get_text(text)

        with open(filename, 'w') as fout:
            fout.write(text)
            print(f"RFC {num:04d} downloaded!")
    except FileNotFoundError or FileExistsError as e:
        logging.warning(f"{e} presented for {filename}")
        pass


def get_filename(text):
    # parse the soup and get title & category for filename creation
    soup = BeautifulSoup(text, 'lxml')
    title = soup.title.text
    return title


def get_text(text):
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
    soup = BeautifulSoup(text, 'html.parser')
    tables = soup.find_all('table')
    rfc_table = tables[2].find_all('tr')
    logging.info(f'Number of RFC\'s available for download: {len(rfc_table)}')
    return len(rfc_table)


def check_folder_exists():
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
