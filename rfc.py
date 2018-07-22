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
    map_title_from_list, get_title_list, sanitize_inputs, read_config, \
    check_last_update, clear_screen, number, logo, Color

logging.basicConfig(level=logging.INFO)

prompt = "rfc.py ~# "


def main():
    start = time.time()
    try:
        # update.main()
        # update.download_rfc_tar()
        # update.uncompress_tar()
        # create_tables()
        # write_to_db()
        # test_headers()
        # home_page()
        read_config()
        check_last_update()

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


def home_page():
    clear_screen()
    logo()
    print("""
    [1] -- Search by Number
    [2] -- Search by Keyword
    [3] -- Search through Bookmark
    
    [q] or [Enter] - Quit!
    """)
    choice = input(prompt)
    if choice == '1':
        clear_screen()
        number()
        search_by_number()
    elif choice == '2':
        clear_screen()
        search_by_keyword()
        pass
    elif choice == '3':
        clear_screen()
        pass
    elif choice == 'q' or choice == '':
        sys.exit()
    else:
        print('[!!] Please Select Options [1,2 or 3] [!!]')
        print('...exiting!')


def search_by_number():
    try:
        print('[*] Enter RFC by number [8305]  [*]')
        print('[*] Press [Enter] for Home Page [*]')
        number = input(f'{prompt}')
        if number == '':
            home_page()
        if not number.isdigit():
            print('[!!] Please enter rfc using numbers only i.e. 8305 [!!]')
            print('Exiting..')
            sys.exit(1)
        result = Data.get_by_id(number).text
        pager(result)
        bookmarker()

    except DoesNotExist:
        print(f'{Color.WARNING}[!!] Query not found! '
              f'Please check the rfc number and try again [!!]{Color.END}')
    except OverflowError:
        print('Integer enter is too large')


def search_by_keyword():
    print(Color.HEADER + '''
  ______     __  _  __________     ___          ______  _____  _____  
 |  _ \ \   / / | |/ /  ____\ \   / | \        / / __ \|  __ \|  __ \ 
 | |_) \ \_/ /  | ' /| |__   \ \_/ / \ \  /\  / / |  | | |__) | |  | |
 |  _ < \   /   |  < |  __|   \   /   \ \/  \/ /| |  | |  _  /| |  | |
 | |_) | | |    | . \| |____   | |     \  /\  / | |__| | | \ \| |__| |
 |____/  |_|    |_|\_\______|  |_|      \/  \/   \____/|_|  \_\_____/ 
                                                                      
    ''' + Color.END)
    print('[*] Enter Keyword/s [http/2 hpack]')
    phrase = sanitize_inputs(input(f'{prompt}'))
    query = (Data.select().join(DataIndex,
                                on=(Data.number == DataIndex.rowid)).where(
        DataIndex.match(phrase)).order_by(DataIndex.bm25()))
    try:
        for results in query:
            print(
                f'{Color.OKBLUE}Matches:{Color.NOTICE} RFC {results.title[:5]}'
                f'{Color.HEADER}- {results.title[5:]}{Color.END}')
        print()
        search_by_number()
    except OperationalError:
        print('[!!] Database lookup error! [!!]')


def bookmarker():
    bookmark = input('Do you wish to bookmark this? [y/N] >> ')
    # if yes then bookmark, else pass
    # something like peewee update data.bookmark = 1
    home_page()


def search_bookmarks():
    print(Color.HEADER + '''
  ______     __  ____   ____   ____  _  ____  __          _____  _  __
 |  _ \ \   / / |  _ \ / __ \ / __ \| |/ /  \/  |   /\   |  __ \| |/ /
 | |_) \ \_/ /  | |_) | |  | | |  | | ' /| \  / |  /  \  | |__) | ' / 
 |  _ < \   /   |  _ <| |  | | |  | |  < | |\/| | / /\ \ |  _  /|  <  
 | |_) | | |    | |_) | |__| | |__| | . \| |  | |/ ____ \| | \ \| . \ 
 |____/  |_|    |____/ \____/ \____/|_|\_\_|  |_/_/    \_\_|  \_\_|\_\\

    ''' + Color.END)
    pass


def pager(data):
    return click.echo_via_pager(data)


if __name__ == '__main__':
    main()
