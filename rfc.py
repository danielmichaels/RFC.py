#!/usr/bin/env python3
import sys
import time

import click
import logging
import os
from peewee import OperationalError, DoesNotExist, \
    IntegrityError

from models import Data, db, DataIndex
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
                    DataIndex.create(rowid=number, title=title, text=body,
                                     category=category)

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
        search_by_keyword()
        pass
    elif choice == '3':
        # search category
        search_by_category()
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
    try:
        number = input('enter RFC by number: >> ')
        if not number.isdigit():
            print('[!!] Please enter rfc using numbers only i.e. 8305 [!!]')
            print('Exiting..')
            sys.exit(1)
        result = Data.get_by_id(number).text
        # result = Data.get_or_none(number).text
        pager(result)
        bookmarker()

    except DoesNotExist:
        print(f'{Color.WARNING}[!!] Query not found! '
              f'Please check the rfc number and try again [!!]{Color.END}')
    except OverflowError:
        print('Integer enter is too large')



def search_by_keyword():
    clear_screen()
    phrase = input('enter keywords >> ')  # '/' causes error.
    query = (Data.select().join(DataIndex,
                                on=(Data.number == DataIndex.rowid)).where(
        DataIndex.match(phrase)).order_by(DataIndex.bm25()))
    try:
        for results in query:
            print(f'{Color.OKBLUE}Matches:{Color.END} {results.title}')
        print()
        choice = input('Enter rfc number you would like to view >> ')
        result = Data.get_by_id(choice).text
        pager(result)
        bookmarker()
    except OperationalError:
        print('[!!] Database lookup error! [!!]')

    # pager(f'Matches: {query.title}')


def search_by_category():
    clear_screen()
    print('TESTING ONLY')
    phrase = input('enter category >> ')
    query = (Data.select().join(DataIndex, on=(Data.number == DataIndex.rowid))
             .where(DataIndex.match(phrase)).order_by(DataIndex.bm25()))
    for result in query:
        print(result.title, result.category)


def bookmark_rfc():
    pass


def pager(data):
    return click.echo_via_pager(data)


def bookmarker():
    bookmark = input('Do you wish to bookmark this? [y/N] >> ')
    # if yes then bookmark, else pass
    # something like peewee update data.bookmark = 1
    home_page()


if __name__ == '__main__':
    main()
