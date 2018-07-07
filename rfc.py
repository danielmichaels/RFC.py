#!/usr/bin/env python3
import time

import logging
import os
from peewee import *

from models import Data, db

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


def strip_extensions():
    """Strips away all non txt files from directory listing.

    :return clean_list: generator of files with unwanted items removed
                        note: time for listcomp = 45s v genexp = 24s
    """

    _, _, files = next(os.walk('test_rfc/'))
    print(type(files))
    dirty_extensions = ['a.txt', 'rfc-index.txt', '.pdf', '.ps', '.ta']
    clean_list = (x for x in files
                  if not any(xs in x for xs in dirty_extensions))
    print(type(clean_list))
    return clean_list


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
