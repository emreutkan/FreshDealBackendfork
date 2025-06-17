import os
import unittest
import io
from src.utils.cloud_storage import allowed_file, compress_image

class BytesFile(io.BytesIO):
    def __init__(self, data: bytes, filename: str):
        super().__init__(data)
        self.filename = filename

class TestCloudStorageUtils(unittest.TestCase):
    def test_allowed_file(self):
        self.assertTrue(allowed_file('image.jpg'))
        self.assertTrue(allowed_file('photo.PNG'))
        self.assertFalse(allowed_file('document.pdf'))
        self.assertFalse(allowed_file('noextension'))

    def test_compress_image(self):
        fixture = os.path.join(os.path.dirname(__file__), 'fixtures', 'test.jpg')
        with open(fixture, 'rb') as f:
            data = f.read()
        bf = BytesFile(data, 'test.jpg')
        compressed, name = compress_image(bf)
        self.assertTrue(len(compressed.getvalue()) < len(data))
        self.assertEqual(name, 'test.jpg')

if __name__ == '__main__':
    unittest.main()
