import time

import configparser
import logging
import os
import re
import requests
import shutil
import tarfile
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from peewee import IntegrityError

from rfcpy.models import db, Data, DataIndex

logging.basicConfig(level=logging.INFO)


class Config:
    STORAGE_PATH = 'test_rfc/'
    DATABASE = 'database.db'
    DATABASE_PATH = os.path.join(os.getcwd(), DATABASE)
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]
    CONFIG_FILE = 'rfc.cfg'


def get_categories(text):
    """Parse through each text file searching for the IETF's categories.

    :arg text from rfc txt file

    :return any matched category, if not found or rfc not does not give a
            category return "uncategorised".
    """
    header = text[:500]
    categories = [
        "Standards Track", "Informational", "Experimental", "Historic",
        "Best Current Practice", "Proposed Standard", "Internet Standard"
    ]
    match = [x for x in [re.findall(x.title(), header.title())
                         for x in categories] if len(x) > 0]
    try:
        return match[0][0]
    except IndexError:
        return "Uncategorised"


def get_title_list():
    list_of_tiles = list()
    with open(os.path.join(Config.STORAGE_PATH, 'rfc-index.txt'), 'r') as f:
        f = f.read().strip()
        search_regex = '^([\d{1,4}])([^.]*).'
        result = re.finditer(search_regex, f, re.M)
        for title in result:
            list_of_tiles.append(title[0])
    return list_of_tiles


def map_title_from_list(number, title_list):
    result = [title for title in title_list if number in title]
    if result:
        return result[0]
    return None


def get_text(text):
    """Get only text from the HTML body of each RFC page."""
    soup = BeautifulSoup(text, 'lxml')
    clean_text = soup.body.get_text()
    return clean_text


def strip_extensions():
    """Strips away all non txt files from directory listing.

    :return clean_list: generator of files with unwanted items removed
                        note: time for listcomp = 45s v genexp = 24s
    """

    _, _, files = next(os.walk('test_rfc/'))
    dirty_extensions = ['a.txt', 'rfc-index.txt', '.pdf', '.ps', '.ta']
    clean_list = (x for x in files
                  if not any(xs in x for xs in dirty_extensions))
    return clean_list


def remove_rfc_files():
    shutil.rmtree(Config.STORAGE_PATH)


def sanitize_inputs(inputs):
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub(' ', inputs)


def create_config():
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "Database Name", f"{Config.DATABASE_PATH}")
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
    config.set("Settings", "Last Update", f"{now}")

    with open(Config.CONFIG_FILE, 'w') as config_file:
        config.write(config_file)


def read_config():
    if not os.path.exists(Config.CONFIG_FILE):
        create_config()
        first_run_update()
    config = configparser.ConfigParser()
    config.read(Config.CONFIG_FILE)
    return config


def read_last_conf_update():
    config = read_config()
    value = config.get('Settings', 'Last Update')
    return value


def update_config():
    config = read_config()
    config.set('Settings', 'Last Update', f'{datetime.utcnow()}')
    with open(Config.CONFIG_FILE, 'w') as config_file:
        config.write(config_file)


def check_last_update():
    last_update = read_last_conf_update()
    to_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
    week = to_dt + timedelta(weeks=1)
    ten_seconds = to_dt + timedelta(seconds=30)
    if datetime.utcnow() > ten_seconds:
        ask_user_to_update()


def ask_user_to_update():
    print("[!] RFC's are updated weekly [!]")
    print("[!] Do you wish to check for updates?")
    answer = input("rfc.py ~# [Y/n] ")
    if answer == 'y' or answer == 'Y' or answer == '':
        print("updating...")
        download_rfc_tar()
        uncompress_tar()
        write_to_db()
        update_config()


def first_run_update():
    print("[!] Database Not Found! [!]")
    print("The database will now be setup...")
    try:
        download_rfc_tar()
        uncompress_tar()
        write_to_db()
        update_config()
    except OSError:
        raise


def download_rfc_tar():
    """Download all RFC's from IETF in a tar.gz for offline sorting."""
    t1 = time.time()
    r = requests.get(Config.URL, stream=True)
    if r.status_code == 200:
        # add error checking
        with open(Config.FILENAME, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        print("..\n[*] Download complete [*]")
    logging.info(f'Time taken in seconds: {time.time() - t1}')


def uncompress_tar():
    """Uncompress the downloaded tarball into the folder and then delete it."""
    if os.path.exists(Config.STORAGE_PATH):
        remove_rfc_files()
    file_location = os.path.join('.', Config.FILENAME)
    print("..uncompressing tar.gz...")
    with tarfile.open(Config.FILENAME) as tar:
        tar.extractall(Config.STORAGE_PATH)
    os.remove(file_location)
    print("..Done!")


def write_to_db():
    """Write the contents of files to sqlite database."""
    create_tables()
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
    remove_rfc_files()  # keep while testing
    print('...Done!')


def update_bookmarks():
    # if user wants to bookmark update that id's bookmark with a 1
    pass


def create_tables():
    with db:
        db.create_tables([Data, DataIndex], safe=True)


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


def logo():
    print(Color.HEADER + """
  _____  ______ _____               
 |  __ \|  ____/ ____|              
 | |__) | |__ | |       _ __  _   _ 
 |  _  /|  __|| |      | '_ \| | | |
 | | \ \| |   | |____ _| |_) | |_| |
 |_|  \_\_|    \_____(_) .__/ \__, |
                       | |     __/ |
                       |_|    |___/ 

                    """ + Color.END)


def number():
    print(Color.HEADER + '''
  ______     __  _   _ _    _ __  __ ____  ______ _____  
 |  _ \ \   / / | \ | | |  | |  \/  |  _ \|  ____|  __ \ 
 | |_) \ \_/ /  |  \| | |  | | \  / | |_) | |__  | |__) |
 |  _ < \   /   | . ` | |  | | |\/| |  _ <|  __| |  _  / 
 | |_) | | |    | |\  | |__| | |  | | |_) | |____| | \ \ 
 |____/  |_|    |_| \_|\____/|_|  |_|____/|______|_|  \_\\
 
  ''' + Color.END)


def keyword():
    print(Color.HEADER + '''
  ______     __  _  __________     ___          ______  _____  _____  
 |  _ \ \   / / | |/ /  ____\ \   / | \        / / __ \|  __ \|  __ \ 
 | |_) \ \_/ /  | ' /| |__   \ \_/ / \ \  /\  / / |  | | |__) | |  | |
 |  _ < \   /   |  < |  __|   \   /   \ \/  \/ /| |  | |  _  /| |  | |
 | |_) | | |    | . \| |____   | |     \  /\  / | |__| | | \ \| |__| |
 |____/  |_|    |_|\_\______|  |_|      \/  \/   \____/|_|  \_\_____/ 
                                                                      
    ''' + Color.END)
