#!/usr/bin/env python3
import time

import logging
import os
from peewee import *

from cli import less
from models import Data, db, create_tables
from utils import strip_extensions, remove_rfc_files, Config, check_database

logging.basicConfig(level=logging.INFO)


def main():
    start = time.time()
    try:
        if not check_database():
            create_tables()
            write_to_db()
        print('try block finished')
        # read_body_from_db(8268)

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
    for file in strip_extensions():
        with open(os.path.join(Config.STORAGE_PATH, file),
                  errors='ignore') as f:
            f = f.read()

            try:
                number = file.strip('.txt').strip('rfc')
                title = ''
                body = f.strip()
                category = ''
                bookmark = False

                with db.atomic():
                    Data.create(number=number, title=title, text=body,
                                category=category,
                                bookmark=bookmark)

            except IntegrityError as e:
                logging.error(f'Integrity Error: {e} Raised!')
                pass
            except AttributeError or ValueError as e:
                logging.error(f'{e}: hit at RFC {file}')
                pass

    print('Successfully finished importing all files to database.')
    print('Now removing unnecessary files from disk....')
    remove_rfc_files()
    print('...Done!')


def read_body_from_db(rfc):
    select = Data.get_by_id(rfc).text
    print(type(select))
    return less(select.encode('utf-8'))


if __name__ == '__main__':
    main()
