"""Utility functions and classes used in RFC.py"""

import configparser
import functools
import logging
import os
import re
import shutil
import tarfile
import time
from datetime import datetime, timedelta

import click
import requests
from peewee import IntegrityError

from rfcpy.helpers.config import Config
from rfcpy.models import db, Data, DataIndex, create_tables

logging.basicConfig(level=logging.INFO)


def timer(function):
    """
    Timer decorator for return a functions execution in seconds.

    Args:
        function: function to be timed

    Returns: time taken plus the original function executed.

    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = function(*args, **kwargs)
        click.echo(f"Download completed in {time.time() - t1:.2f} seconds")
        return result

    return wrapper


def get_categories(text):
    """Parse through each text file searching for the IETF's categories.

    :arg text: from rfc txt file

    :return any matched category, if not found or rfc not does not give a
            category return "uncategorised".
    """

    header = text[:500]
    categories = [
        "Standards Track",
        "Informational",
        "Experimental",
        "Historic",
        "Best Current Practice",
        "Proposed Standard",
        "Internet Standard",
    ]
    match = [
        x
        for x in [re.findall(x.title(), header.title()) for x in categories]
        if len(x) > 0
    ]
    try:
        return match[0][0]
    except IndexError:
        return "Uncategorised"


def get_title_list():
    """Parses all the current RFC titles from the rfc-index.txt file allowing
    the title to be written to the database easily.

    :return list of RFC title information
    """

    list_of_titles = []
    with open(os.path.join(Config.STORAGE_PATH, "rfc-index.txt"), "r") as f:
        f = f.read().strip()
        search_regex = "^([\d{1,4}])([^.]*)."
        result = re.finditer(search_regex, f, re.M)
        for title in result:
            list_of_titles.append(title[0])
    return list_of_titles


def map_title_from_list(number, title_list):
    """Used during the iterative inserts in fn:write_to_db - if number matches
    the number within title_list, write title to db.

    :arg number: string containing RFC number
    :arg title_list: list of all rfc titles from fn:get_title_list

    :returns result: string containing title of RFC.
    """

    result = [title for title in title_list if number in title]
    if result:
        return result[0]
    return None


def strip_extensions():
    """Strips away all non txt files from directory listing.

    :return clean_list: generator of files with unwanted items removed
    """

    _, _, files = next(os.walk(Config.STORAGE_PATH))
    dirty_extensions = ["a.txt", "rfc-index.txt", ".pdf", ".ps", ".ta", ".html"]
    clean_list = (x for x in files if not any(xs in x for xs in dirty_extensions))
    return clean_list


def remove_rfc_files():
    """Removes of downloaded and unzipped RFC files and folders after being
    written to the database."""

    shutil.rmtree(Config.STORAGE_PATH)


def sanitize_inputs(inputs):
    """Allows only a-zA-Z0-9 characters as safe for searching the database.

    :arg inputs: user provided search string to be sanitized.

    :return regex: replace any non-approved chars with ' '.
    """

    regex = re.compile("[^a-zA-Z0-9]")
    return regex.sub(" ", inputs)


def create_config(testing=False):
    """Create basic config file.

    options:    1. Database Name
                2. Last Update
    """

    if not os.path.exists(Config.ROOT_FOLDER):
        os.mkdir(Config.ROOT_FOLDER)
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "Database Name", f"{Config.DATABASE_PATH}")
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
    config.set("Settings", "Last Update", f"{now}")

    if testing is True:
        with open(os.path.join(Config.TESTS_FOLDER, "rfc.cfg"), "w") as config_file:
            config.write(config_file)
        return

    with open(os.path.join(Config.ROOT_FOLDER, Config.CONFIG_FILE), "w") as config_file:
        config.write(config_file)


def read_config(testing=False):
    """Check if config file exists, if not create it and prompt user to
    download the database.

    :return config: config file opened for reading."""

    config = configparser.ConfigParser()
    config.read(Config.CONFIG_FILE)

    if testing is True:
        config.read(os.path.join(Config.TESTS_FOLDER, "rfc.cfg"))
        return config
    if not os.path.exists(Config.CONFIG_FILE):
        create_config()
    if not os.path.exists(Config.DATABASE_PATH):
        first_run_update()
    return config


def read_last_conf_update(testing=False):
    """Reads the 'Last Update' value in config file."""

    config = read_config(testing)
    value = config.get("Settings", "Last Update")
    return value


def update_config(testing=False):
    """Updates the Last Update value once a new database has been initialised
    after initial install or weekly update.
    """

    config = read_config(testing)
    config.set("Settings", "Last Update", f"{datetime.utcnow()}")
    if testing is True:
        with open(os.path.join(Config.TESTS_FOLDER, "rfc.cfg"), "w") as config_file:
            config.write(config_file)
        return
    with open(Config.CONFIG_FILE, "w") as config_file:
        config.write(config_file)


def check_last_update():
    """Uses timedelta to see if one week has elapsed since last update,
    if so then prompt user to retrieve new list.
    """

    last_update = read_last_conf_update()
    to_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
    week = to_dt + timedelta(weeks=1)
    if datetime.utcnow() > week:
        ask_user_to_update()


def ask_user_to_update():
    """If update is available, give user the option to download new files."""

    print("[!] RFC's are updated weekly [!]")
    print("[!] Do you wish to check for updates?")
    answer = input("rfc.py ~# [Y/n] ")
    if answer == "y" or answer == "Y" or answer == "":
        print("updating...")
        download_rfc_tar()
        uncompress_tar()
        write_to_db()
        update_config()


def first_run_update():
    """Checks if database and/or config file exists and will ask user to update
    based on which variable is missing.

    Triggered on one conditions; no config file found. If cfg file is missing
    but database is found, user has option to update the database or not.
    """

    try:
        if not os.path.exists(Config.DATABASE):
            print("[!] Database Not Found! [!]")
            print("The database will now be setup...")
            download_rfc_tar()
            uncompress_tar()
            write_to_db()
            update_config()

    except OSError:
        raise


@timer
def download_rfc_tar():
    """
    Download all RFC's from IETF in a tar.gz for offline sorting.
    Download progress is tracked via click.progressbar.
    """

    r = requests.get(Config.URL, stream=True)
    dl_length = r.headers["Content-Length"]
    if r.status_code == 200:
        with open(
            os.path.join(Config.ROOT_FOLDER, Config.FILENAME), "wb"
        ) as f, click.progressbar(length=int(dl_length)) as bar:
            r.raw.decode_content = True
            for chunk in r.iter_content(1024):
                f.write(chunk)
                bar.update(len(chunk))

        print("..\n[*] Download complete [*]")


def uncompress_tar():
    """Uncompress the downloaded tarball into the folder and then delete it."""

    if os.path.exists(Config.STORAGE_PATH):
        remove_rfc_files()
    file_location = os.path.join(Config.ROOT_FOLDER, Config.FILENAME)
    print("..uncompressing tar.gz...")
    with tarfile.open(os.path.join(Config.ROOT_FOLDER, Config.FILENAME)) as f:
        f.extractall(Config.STORAGE_PATH)
    os.remove(file_location)
    print("..Done!")


def write_to_db():
    """Write the contents of files to sqlite database.

    function will run each time the database is updated. Relies on RFC number
    as the Primary Key to issue Unique Key Constraint which prohibits duplicate
    RFC's being written to DB.

    Writes the following to models.Data (and its Virtual Table; DataIndex)
        :arg number: RFC number taken from filename <rfc1918.txt>
        :arg title: RFC Title taken from rfc-index.txt and mapped against number
        :arg text: body of the document parsed for reading in terminal
        :arg category: category type taken from document
        :arg bookmark: boolean, if bookmarked returns 1 (True), default=0

    Removes folder containing all text files post write.
    """

    create_tables()
    print("..Beginning database writes..")
    title_list = get_title_list()
    for file in strip_extensions():
        with open(os.path.join(Config.STORAGE_PATH, file), errors="ignore") as f:
            f = f.read().strip()

            try:
                number = file.strip(".txt").strip("rfc")
                title = map_title_from_list(number, title_list)
                body = f
                category = get_categories(f)
                bookmark = False

                with db.atomic():
                    Data.create(
                        number=number,
                        title=title,
                        text=body,
                        category=category,
                        bookmark=bookmark,
                    )
                    DataIndex.create(
                        rowid=number, title=title, text=body, category=category
                    )

            except IntegrityError as e:
                logging.debug(f"Integrity Error: {e} Raised at {number}")
                pass
            except AttributeError or ValueError as e:
                logging.debug(f"{e}: hit at RFC {file}")
                pass
    else:
        remove_rfc_files()
        print("Successfully finished importing all files to database.")
        print("Now removing unnecessary files from disk....")
        print("...Done!")
