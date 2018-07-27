import os
import requests
import responses
import shutil
import unittest
from datetime import datetime
from requests import ConnectionError, ConnectTimeout

from rfcpy.utils import Config, create_config, update_config, get_categories, \
    read_last_conf_update, sanitize_inputs


class TestUtils(unittest.TestCase):
    """Testing utility functions."""

    def setUp(self):
        test_folder = os.path.dirname(os.path.abspath(__file__))
        if os.getcwd() != test_folder:
            os.chdir(test_folder)
            create_config()
        create_config()

    def tearDown(self):
        path = os.path.join(os.getcwd())
        os.remove(os.path.join(path, 'rfc.cfg'))

    def test_configs(self):
        self.assertEqual(Config.CONFIG_FILE, 'rfc.cfg')
        self.assertEqual(Config.DATABASE, 'database.db')

    def test_categories(self):
        text = "Historic: once upon a time"
        result = get_categories(text)
        self.assertTrue(result, 'Historic')
        self.assertEqual(result, 'Historic')
        self.assertNotEqual(result, 'Informational')

    def test_strip_extensions(self):
        files = ['rfc1918.txt', 'a.txt', 'rfc400.pdf', 'rfc8305.txt',
                 'rfc111.ta', 'rfc1.txt', 'rfc-index.txt', 'rfc.ps']
        dirty_extensions = ['a.txt', 'rfc-index.txt', '.pdf', '.ps', '.ta']
        clean_list = (x for x in files
                      if not any(xs in x for xs in dirty_extensions))
        expected = ['rfc1918.txt', 'rfc8305.txt', 'rfc1.txt']
        actual = list()
        for items in clean_list:
            actual.append(items)
            self.assertTrue(items, 'rfc1918.txt')
            self.assertNotIn(items, 'rfc400.pdf')
        self.assertCountEqual(expected, actual)
        self.assertNotEqual(clean_list, files, 'Lists are equal')
        self.assertTrue(set(actual) == set(expected),
                        'the lists are not equal')

    def test_remove_rfc_files(self):
        os.mkdir('test_path')
        test_path = os.path.join(os.getcwd(), 'test_path')
        shutil.rmtree(test_path)
        self.assertRaises(AssertionError)  # test assertion if no longer exist
        self.assertFalse(os.path.exists(test_path))

    def test_create_config(self):
        cfg = os.path.join(os.getcwd(), 'rfc.cfg')
        self.assertTrue(os.path.exists(cfg))

    def test_read_config(self):
        # need to mock this call
        tests = os.getcwd()
        os.chdir("..")
        reader = read_last_conf_update()
        self.assertIsInstance(reader, str)
        self.assertNotIsInstance(reader, int)
        self.assertNotIsInstance(reader, list)
        os.chdir(tests)

    def test_update_config(self):
        # mock this call as it creates db
        tests = os.getcwd()
        os.chdir("..")
        update = update_config()
        read = read_last_conf_update()
        self.assertNotEqual(update, read)
        self.assertIn(datetime.strftime(datetime.utcnow(),
                                        "%Y-%m-%d %H:%M"), read)
        os.chdir(tests)

    def test_sanitize_inputs(self):
        input1 = 'HTTP/2'
        input2 = '802.3'
        self.assertEqual(sanitize_inputs(" ", ), ' ')
        self.assertEqual(sanitize_inputs(input1), 'HTTP 2')
        self.assertEqual(sanitize_inputs(input2), '802 3')
        self.assertNotEqual(sanitize_inputs(input1), 'HTTP/2')

    def test_uncompress_tar(self):
        pass

    @responses.activate
    def test_download_rfc(self):
        responses.add(responses.GET, Config.URL, json=None,
                      status=200, stream=True, content_type='application/json')
        resp = requests.get(Config.URL)
        self.assertTrue(resp.status_code == 200)

    @responses.activate
    def test_connection_error(self):
        responses.add(responses.GET, Config.URL, body=ConnectionError())
        with self.assertRaises(ConnectionError):
            requests.get(Config.URL)

    @responses.activate
    def test_connection_timeout(self):
        responses.add(responses.GET, Config.URL, body=ConnectTimeout())
        with self.assertRaises(ConnectTimeout):
            requests.get(Config.URL)


if __name__ == '__main__':
    unittest.main()
