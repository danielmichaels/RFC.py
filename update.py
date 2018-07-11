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

from models import create_tables
from rfc import write_to_db
from utils import Config, random_header


def main():
    try:
        if not check_database():
            create_tables()
            write_to_db()
        return
    except ConnectionError:
        print("Connection Error raised")


def check_database():
    """Check if database exists, if not download the RFC's and write them
    to database, otherwise do nothing."""
    print("Checking if database has been initialised...")
    if Config.DATABASE_PATH in os.getcwd():
        print(Config.DATABASE_PATH)
        print("Database exists")
        return
    print("Database not found...")
    print("RFC.py will now download the files and load them into"
          " the database")
    print("This may take several minutes...")
    download_rfc_tar()
    uncompress_tar()


def download_rfc_tar():
    """Download all RFC's from IETF in a tar.gz for offline sorting."""
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]
    # Takes ~ 130s to DL on my connection
    t1 = time.time()
    r = requests.get(URL, stream=True, headers=random_header())
    if r.status_code == 200:
        # add error checking
        with open(FILENAME, 'wb') as f:
            # replace test.tar.gz with ~/.rfc in future
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        print("....\n..Download complete..")
    logging.info(f'Time taken in seconds: {time.time() - t1}')


def uncompress_tar():
    """Uncompress the downloaded tarball into the folder and then delete it."""
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]
    file_location = os.path.join('.', FILENAME)
    print("..uncompressing tar.gz...")
    with tarfile.open(FILENAME) as tar:
        tar.extractall(Config.STORAGE_PATH)
    os.remove(file_location)
    print("..Done!")


if __name__ == '__main__':
    main()
