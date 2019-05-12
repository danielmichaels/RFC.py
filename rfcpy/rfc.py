#!/usr/bin/env python3
"""
    RFC.py - A python module that downloads Request For Comments from the
    Internet Engineering Task Force into a Sqlite database for offline reading.

    Includes full text search, RFC number search and bookmarking capabilities
    and weekly updates inline with the IETF policy of weekly additions.

        Copyright (C) 2018-2019, Daniel Michaels
"""
import logging
import sys

import click
from peewee import OperationalError, DoesNotExist

from rfcpy.models import Data, DataIndex
from rfcpy.utils import (
    sanitize_inputs,
    read_config,
    check_last_update,
    clear_screen,
    print_by_number,
    logo,
    Color,
    print_by_keyword,
    print_by_bookmark,
    print_get_latest,
)

logging.basicConfig(level=logging.INFO)

prompt = "RFC.py ~# "

# TODO: list x latest rfc's


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
        print("User exited using CTRL-C")


def home_page():
    """Interactive home page which user can use to select their type of search.

    :options:   1. Search by RFC number
                2. Search by keyword (using Sqlite FTS5)
                3. Search bookmarks
                [q] or [Enter] to quit application
    """

    clear_screen()
    logo()
    print(
        """
    [1] -- Search by Number
    [2] -- Search by Keyword
    [3] -- Search through Bookmark
    [4] -- Latest 10 RFC's
    
    [0] -- User Options
    [q] or [Enter] - Quit!
    """
    )
    choice = input(prompt)
    if choice == "1":
        clear_screen()
        print_by_number()
        search_by_number()
    elif choice == "2":
        clear_screen()
        search_by_keyword()
    elif choice == "3":
        clear_screen()
        search_bookmarks()
    elif choice == "4":
        clear_screen()
        latest()
    elif choice == "0":
        clear_screen()
        settings_page()
    elif choice == "q" or choice == "":
        sys.exit()
    else:
        print("[!!] Please Select Options [1,2 or 3] [!!]")
        print("...exiting!")


def search_by_number():
    """User is to enter a valid RFC for retrieval from database."""

    try:
        print("[*] Enter RFC by number [eg. 8305]  [*]")
        print("[*] OR Press [Enter] for Home Page  [*]")
        number = input(f"{prompt}")
        if number == "":
            home_page()
        if not number.isdigit():
            print("[!!] Please enter rfc using numbers only i.e. 8305 [!!]")
            print("Exiting..")
            sys.exit(1)
        result = Data.get_by_id(number).text
        pager(result)
        bookmarker(number)

    except DoesNotExist:
        print(
            f"{Color.WARNING}[!!] Query not found! "
            f"Please check the rfc number and try again [!!]{Color.END}"
        )
    except OverflowError:
        print("Integer entered is too large.")


def search_by_keyword():
    """User can enter keywords to search for RFC's - only parses the title.

    Prints all matches with RFC number - user can then enter which RFC number
    to view, if any, or return to Home Page.
    """

    print_by_keyword()
    print("[*] Enter Keyword/s [http/2 hpack]")
    phrase = input(f"{prompt}")
    phrase = sanitize_inputs(phrase)
    query = (
        Data.select()
        .join(DataIndex, on=(Data.number == DataIndex.rowid))
        .where(DataIndex.match(phrase))
        .order_by(DataIndex.bm25())
    )
    try:
        for results in query:
            print(
                f"{Color.OKBLUE}Matches:{Color.NOTICE} RFC {results.title[:5]}"
                f"{Color.HEADER}- {results.title[5:]}{Color.END}"
            )
        print()
        search_by_number()
    except OperationalError:
        print("[!!] Database lookup error! [!!]")


def search_bookmarks():
    """Print list of bookmarked RFC's"""

    print_by_bookmark()
    print("[*] All Bookmarked RFC's[*]")
    print()
    query = Data.select().where(Data.bookmark == 1)
    for result in query:
        print(
            f"\t{Color.OKBLUE}RFC {result.number} - {Color.NOTICE}"
            f"{result.title[5:]}{Color.END}"
        )
    search_by_number()


def settings_page():
    """Print list of user adjustable settings."""
    print("[*] User Options\n")
    print(f"{Color.NOTICE}[1] Delete bookmarks{Color.END}\n")
    print("[Enter] Return to Home Page\n")
    choice = input(prompt)
    if choice == "1":
        clear_screen()
        update_bookmarks()
    elif choice == "":
        home_page()


def update_bookmarks():
    """Updates the Bookmark row in database for selected RFC."""
    print("[!] Select bookmark to delete [!]")
    print()
    query = Data.select().where(Data.bookmark == 1)
    for result in query:
        print(
            f"\t{Color.OKBLUE}RFC {result.number} - {Color.NOTICE}"
            f"{result.title[5:]}{Color.END}"
        )
    print()
    print("[*] Enter Bookmark to delete by number [eg. 8305]  [*]")
    print("[*] OR Press [Enter] for Home Page                 [*]")
    choice = input(prompt)

    if choice.isdigit():
        update = Data(number=choice, bookmark=0)
        update.save()
        update_bookmarks()
        print()
    elif choice == "" or choice == "q":
        home_page()
    else:
        print("\n[!] Please enter a valid number! [!]")
        print()
        update_bookmarks()


def bookmarker(number):
    """Give user the option to bookmark the last read RFC, defaults to No."""

    bookmark = input("Do you wish to bookmark this? [y/N] >> ")
    if bookmark == "y" or bookmark == "Y":
        print("YES", number)
        update = Data(number=number, bookmark=1)
        update.save()
    home_page()


def latest():
    """Get the most recent RFC's returning ten by default but the user can
    specify a set number to see.

    :arg number (default=10) user can set how many to retrieve."""
    print_get_latest()
    query = Data.select().order_by(Data.title.desc()).limit(10)
    for result in query:
        print(
            f"\t{Color.OKBLUE}RFC {result.number} - {Color.NOTICE}"
            f"{result.title[5:]}{Color.END}"
        )
    search_by_number()


def pager(data):
    """Utilise the safe work of Click.echo_via_pager to render RFC's using
    system pager.
    """

    return click.echo_via_pager(data)


if __name__ == "__main__":
    main()
