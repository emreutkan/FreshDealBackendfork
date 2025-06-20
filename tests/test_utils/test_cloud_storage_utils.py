import os
import io
import unittest
from PIL import Image

from src.utils.cloud_storage import allowed_file, compress_image, delete_file, UPLOAD_FOLDER

class TestCloudStorageUtils(unittest.TestCase):
    def test_allowed_file(self):
        self.assertTrue(allowed_file('photo.jpg'))
        self.assertTrue(allowed_file('image.PNG'))
        self.assertFalse(allowed_file('document.pdf'))

    def test_compress_image(self):
        # create a simple red image
        img = Image.new('RGB', (1024, 768), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        buffer.filename = 'sample.jpg'

        compressed, new_name = compress_image(buffer)
        self.assertIsInstance(compressed, io.BytesIO)
        self.assertEqual(new_name, 'sample.jpg')
        self.assertLess(len(compressed.getvalue()), len(buffer.getvalue()))

    def test_delete_file_local(self):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        path = os.path.join(UPLOAD_FOLDER, 'temp.jpg')
        with open(path, 'wb') as f:
            f.write(b'data')

        success, _ = delete_file(f'http://local/{os.path.basename(path)}')
        self.assertTrue(success)
        self.assertFalse(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
