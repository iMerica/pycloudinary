import random

import cloudinary
from cloudinary import uploader, utils, api
import time

import urllib3
import unittest
import tempfile
import zipfile
import cloudinary.poster.streaminghttp

TEST_TAG = "pycloudinary_test" + str(random.randint(10000, 99999))


class ArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        uploader.upload("tests/logo.png", tags=[TEST_TAG])
        uploader.upload("tests/logo.png", tags=[TEST_TAG], transformation=dict(width=10))

    @classmethod
    def tearDownClass(cls):
        api.delete_resources_by_tag(TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_archive(self):
        """should successfully generate an archive"""
        result = uploader.create_archive(tags=[TEST_TAG])
        self.assertEqual(2, result.get("file_count"))
        result = uploader.create_zip(tags=[TEST_TAG], transformations=[{"width": 0.5}, {"width": 2.0}])
        self.assertEqual(4, result.get("file_count"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_expires_at(self):
        """should successfully generate an archive"""
        expires_at = int(time.time()+3600)
        result = uploader.create_zip(tags=[TEST_TAG], expires_at=expires_at)
        self.assertEqual(2, result.get("file_count"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_archive_url(self):
        result = utils.download_zip_url(tags=[TEST_TAG], transformations=[{"width": 0.5}, {"width": 2.0}])
        http = urllib3.PoolManager()
        response = http.request('get', result)
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(response.data)
            temp_file.flush()
            with zipfile.ZipFile(temp_file_name, 'r') as zip_file:
                infos = zip_file.infolist()
                self.assertEqual(4, len(infos))
        http.clear()


if __name__ == '__main__':
    unittest.main()
