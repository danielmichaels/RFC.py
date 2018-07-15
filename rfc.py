#!/usr/bin/env python3
import time

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
        write_to_db()
        # test_headers()

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


if __name__ == '__main__':
    main()
