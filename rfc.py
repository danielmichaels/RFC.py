#!/usr/bin/env python3
import time

import logging
import os
from peewee import *

from models import Data, db
from utils import strip_extensions

logging.basicConfig(level=logging.INFO)


class Config:
    STORAGE_PATH = 'test_rfc/'
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]


def main():
    start = time.time()
    try:
        write_to_db()

    except OSError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')

    finally:
        end = time.time()
        logging.info(f'This took: {end - start} to run!')




def write_to_db():
    """Write the contents of files to sqlite database."""

    for file in strip_extensions():
        with open(os.path.join(Config.STORAGE_PATH, file), encoding='utf-8',
                  errors='ignore') as f:
            f = f.read()

            try:
                number = file.strip('.txt').strip('rfc').strip('.pdf')
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


if __name__ == '__main__':
    main()
