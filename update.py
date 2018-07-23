"""
Update script for rfc.py package that downloads a complete listing of all
rfc's and writes them to the database, once done it deletes those files.
"""
import time

import logging
import os
import requests
import shutil
import tarfile
from peewee import IntegrityError

from models import db, Data, DataIndex
from utils import Config, get_title_list, strip_extensions, \
    map_title_from_list, get_categories, create_tables


def main():
    try:
        if check_database():
            create_tables()
            write_to_db()
        return
    except ConnectionError:
        print("Connection Error raised")


def check_database():
    """Check if database exists, if not download the RFC's and write them
    to database, otherwise do nothing."""
    print("Checking if database has been initialised...")
    if Config.DATABASE_PATH:
        print("Database exists")
        print("Skipping update...")
        return
    print("Database not found...")
    print("RFC.py will now download the files and load them into"
          " the database")
    print("This may take several minutes...")
    download_rfc_tar()
    uncompress_tar()


def download_rfc_tar():
    """Download all RFC's from IETF in a tar.gz for offline sorting."""
    t1 = time.time()
    r = requests.get(Config.URL, stream=True)
    if r.status_code == 200:
        # add error checking
        with open(Config.FILENAME, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        print("..\n..Download complete..")
    logging.info(f'Time taken in seconds: {time.time() - t1}')


def uncompress_tar():
    """Uncompress the downloaded tarball into the folder and then delete it."""
    file_location = os.path.join('.', Config.FILENAME)
    print("..uncompressing tar.gz...")
    with tarfile.open(Config.FILENAME) as tar:
        tar.extractall(Config.STORAGE_PATH)
    os.remove(file_location)
    print("..Done!")


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

# if __name__ == '__main__':
#     main()
