#!/usr/bin/env python3
import sys
import time

import click
import logging
import os
from peewee import *

from models import Data, db
from utils import strip_extensions, Config, get_categories, \
    map_title_from_list, get_title_list

logging.basicConfig(level=logging.INFO)


def main():
    start = time.time()
    try:
        # update.main()
        # update.download_rfc_tar()
        # update.uncompress_tar()
        # create_tables()
        # write_to_db()
        # test_headers()
        home_page()


    except OSError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')

    finally:
        end = time.time()
        logging.info(f'This took: {end - start} to run!')


def write_to_db():
    """Write the contents of files to sqlite database."""

    print("..Beginning database writes..")
    title_list = get_title_list()
    for file in strip_extensions():
        with open(os.path.join(Config.STORAGE_PATH, file),
                  errors='ignore') as f:
            f = f.read().strip()

            try:
                number = file.strip('.txt').strip('rfc')
                title = map_title_from_list(number, title_list)
                body = f
                category = get_categories(f)
                bookmark = False

                with db.atomic():
                    Data.create(number=number, title=title, text=body,
                                category=category,
                                bookmark=bookmark)

            except IntegrityError as e:
                logging.error(f'Integrity Error: {e} Raised at {number}')
                pass
            except AttributeError or ValueError as e:
                logging.error(f'{e}: hit at RFC {file}')
                pass

    print('Successfully finished importing all files to database.')
    print('Now removing unnecessary files from disk....')
    # remove_rfc_files() # keep while testing
    print('...Done!')


def test_headers():
    with open('test_rfc/rfc-index.txt', 'r') as index:
        index = index.read().strip()
        pass  # here for manual testing


def clear_screen():
    os.system('clear')


class Color:
    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    LOGGING = '\33[34m'


logo = Color.HEADER + """
          ____  _____ ____               
 |  _ \|  ___/ ___|  _ __  _   _ 
 | |_) | |_ | |     | '_ \| | | |
 |  _ <|  _|| |___ _| |_) | |_| |
 |_| \_\_|   \____(_) .__/ \__, |
                    |_|    |___/ 
                    """ + Color.END
prompt = "rfc.py ~# "


def home_page():
    clear_screen()
    print(logo + """
    [1] -- Search by Number
    [2] -- Search by Keyword
    [3] -- Search by Category
    [4] -- Search through Bookmark
    [99] Quit!
    """)
    choice = input(prompt)
    # early testing model
    if choice == '1':
        # search num
        search_by_number()
    elif choice == '2':
        # search keyword
        pass
    elif choice == '3':
        # search category
        pass
    elif choice == '4':
        # search bookmarks
        pass
    elif choice == '99':
        sys.exit()
    # else:
    #     choice


def search_by_number():
    clear_screen()
    number = input('enter RFC by number: >> ')
    print('number:', number)
    result = Data.get_by_id(number).text
    # needs error checking index errors etc
    pager(result)


def search_by_keyword():
    pass


def search_by_category():
    pass


def bookmark_rfc():
    pass


def pager(data):
    click.echo_via_pager(data)
    input('Do you want to bookmark this? >> [y/N] ')
    # input will need routing to bookmark in future.
    # needs error checking such as 'isdigit' etc
    home_page()


if __name__ == '__main__':
    main()
