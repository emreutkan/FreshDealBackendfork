import unittest
from flask import json
from app import create_app
from src.models import db, User
from werkzeug.security import generate_password_hash
import uuid
import os
from PIL import Image


class TestRestaurant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Create test image directory
        cls.test_dir = os.path.join(os.path.dirname(__file__), 'test_files')
        if not os.path.exists(cls.test_dir):
            os.makedirs(cls.test_dir)

        # Create test image
        cls.test_image_path = os.path.join(cls.test_dir, 'test_image.jpg')
        cls._create_test_image(cls.test_image_path)

    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456789@127.0.0.1:3306/freshdealtest'
        self.client = self.app.test_client()
        self.base_url = '/v1'

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create owner user
            unique_id = str(uuid.uuid4())[:8]
            self.owner_email = f"owner_{unique_id}@example.com"
            self.owner_password = "password123"
            self.owner = User(
                name="Test Owner",
                email=self.owner_email,
                phone_number="+1234567890",
                password=generate_password_hash(self.owner_password),
                role="owner",
                email_verified=True
            )

            db.session.add(self.owner)
            db.session.commit()

            # Login as owner
            self.owner_token = self._get_auth_token(self.owner_email, self.owner_password)
            self.owner_headers = {'Authorization': f'Bearer {self.owner_token}'} if self.owner_token else {}

        self.base_restaurant_data = {
            'restaurantName': 'Test Restaurant',
            'restaurantDescription': 'Test Description',
            'restaurantEmail': 'restaurant@test.com',
            'restaurantPhone': '+1234567890',
            'category': 'Test Category',
            'longitude': '28.979530',
            'latitude': '41.015137',
            'workingDays': 'Monday,Tuesday',
            'workingHoursStart': '09:00',
            'workingHoursEnd': '22:00',
            'pickup': 'true',
            'delivery': 'true'
        }

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @staticmethod
    def _create_test_image(path):
        """Create a test image file"""
        img = Image.new('RGB', (100, 100), color='red')
        img.save(path)

    def _get_auth_token(self, email, password):
        """Helper method to get auth token"""
        login_data = {
            'email': email,
            'password': password,
            'login_type': 'email',
            'password_login': True
        }

        response = self.client.post(
            f'{self.base_url}/login',
            json=login_data,
            content_type='application/json'
        )

        if response.status_code == 200:
            return json.loads(response.data.decode('utf-8')).get('token')
        return None

    def test_create_restaurant_success(self):
        """Test creating a restaurant with all required fields"""
        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=self.base_restaurant_data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('restaurant', data)
        self.assertEqual(data['restaurant']['restaurantName'], self.base_restaurant_data['restaurantName'])

    def test_create_restaurant_with_image(self):
        """Test creating a restaurant with image upload"""
        with open(self.test_image_path, 'rb') as img:
            data = dict(self.base_restaurant_data)
            files = {
                'image': (os.path.basename(self.test_image_path), img, 'image/jpeg')
            }

            response = self.client.post(
                f'{self.base_url}/restaurants',
                data=data,
                files=files,
                headers=self.owner_headers
            )

            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue(data['success'])
            self.assertIn('image_url', data['restaurant'])
            self.assertIsNotNone(data['restaurant']['image_url'])

    def test_create_restaurant_missing_required_fields(self):
        """Test creating a restaurant with missing required fields"""
        data = {
            'restaurantDescription': 'Test Description',
            'pickup': 'true',
            'delivery': 'true'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()