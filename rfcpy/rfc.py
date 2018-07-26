#!/usr/bin/env python3
"""
    RFC.py - A python module that downloads Request For Comments from the
    Internet Engineering Task Force into a Sqlite database for offline reading.

    Includes full text search, RFC number search and bookmarking capabilities
    and weekly updates inline with the IETF policy of weekly additions.

        Copyright (C) 2018, Daniel Michaels
"""
import sys

import click
import logging
from peewee import OperationalError, DoesNotExist

from .models import Data, DataIndex
from .utils import sanitize_inputs, read_config, \
    check_last_update, clear_screen, number, logo, Color, keyword

logging.basicConfig(level=logging.INFO)

prompt = "rfc.py ~# "


def main():
    try:
        clear_screen()
        logo()
        read_config()
        check_last_update()
        home_page()

    except OSError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')


def home_page():
    """Interactive home page which user can use to select their type of search.

    :options:   1. Search by RFC number
                2. Search by keyword (using Sqlite FTS5)
                3. Search bookmarks
                [q] or [Enter] to quit application
    """
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
    """User is to enter a valid RFC for retrieval from database."""
    try:
        print('[*] Enter RFC by number [eg. 8305]  [*]')
        print('[*] OR Press [Enter] for Home Page  [*]')
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
    keyword()
    print('[*] Enter Keyword/s [http/2 hpack]')
    phrase = input(f'{prompt}')
    phrase = sanitize_inputs(phrase)
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
