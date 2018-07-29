import os
import pathlib


class Config:
    """Basic configuration settings."""

    ROOT_FOLDER = os.path.join(pathlib.Path.home(), '.rfc')
    STORAGE_PATH = os.path.join(ROOT_FOLDER, 'rfc_files/')
    DATABASE = 'database.db'
    DATABASE_PATH = os.path.join(ROOT_FOLDER, DATABASE)
    URL = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    FILENAME = URL.split('/')[-1]
    CONFIG_FILE = os.path.join(ROOT_FOLDER, 'rfc.cfg')
    TESTS_FOLDER = os.path.join(ROOT_FOLDER, 'tests')
