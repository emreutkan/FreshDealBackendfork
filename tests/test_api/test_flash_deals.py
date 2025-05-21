import unittest
from flask import json
from app import create_app
from src.models import db, User, Restaurant, Listing, FlashDeal
from werkzeug.security import generate_password_hash
import uuid
import os
from PIL import Image
from datetime import datetime, timedelta, UTC


class TestFlashDeals(unittest.TestCase):
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

            # Create customer user
            self.customer_email = f"customer_{unique_id}@example.com"
            self.customer_password = "password123"
            self.customer = User(
                name="Test Customer",
                email=self.customer_email,
                phone_number="+1234567891",
                password=generate_password_hash(self.customer_password),
                role="customer",
                email_verified=True
            )

            db.session.add(self.owner)
            db.session.add(self.customer)
            db.session.commit()

            # Create test restaurant with flash deals enabled
            self.test_restaurant = Restaurant(
                owner_id=self.owner.id,
                restaurantName="Flash Deal Restaurant",
                restaurantDescription="Test Description",
                longitude=28.979530,
                latitude=41.015137,
                category="Test Category",
                workingDays="Monday,Tuesday",
                workingHoursStart="09:00",
                workingHoursEnd="22:00",
                pickup=True,
                delivery=True,
                restaurantEmail="restaurant@test.com",
                restaurantPhone="+1234567890",
                flash_deals_available=True,
                flash_deals_count=0
            )
            db.session.add(self.test_restaurant)
            db.session.commit()

            self.restaurant_id = self.test_restaurant.id

            # Create a regular listing that can be converted to flash deal
            self._create_test_listing()

            # Login as owner and customer
            self.owner_token = self._get_auth_token(self.owner_email, self.owner_password)
            self.owner_headers = {'Authorization': f'Bearer {self.owner_token}'} if self.owner_token else {}

            self.customer_token = self._get_auth_token(self.customer_email, self.customer_password)
            self.customer_headers = {'Authorization': f'Bearer {self.customer_token}'} if self.customer_token else {}

    def _create_test_listing(self):
        """Helper method to create a test listing"""
        with open(self.test_image_path, 'rb') as img:
            data = {
                'title': 'Regular Listing',
                'description': 'Test Description',
                'original_price': '20.99',
                'pick_up_price': '18.99',
                'delivery_price': '22.99',
                'count': '10',
                'consume_within': '48'
            }

            files = {
                'image': (os.path.basename(self.test_image_path), img, 'image/jpeg')
            }

            response = self.client.post(
                f'{self.base_url}/restaurants/{self.restaurant_id}/listings',
                data=data,
                files=files,
                headers=self.owner_headers
            )

            response_data = json.loads(response.data.decode('utf-8'))
            self.listing_id = response_data['listing']['id']

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

    def test_create_flash_deal(self):
        """Test creating a new flash deal"""
        data = {
            'title': 'Flash Deal',
            'description': 'Limited time offer',
            'original_price': '20.99',
            'flash_price': '10.99',
            'quantity': '5',
            'duration_hours': '2'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            json=data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertIn('flash_deal', response_data)
        self.assertEqual(response_data['flash_deal']['title'], data['title'])

    def test_convert_listing_to_flash_deal(self):
        """Test converting a regular listing to a flash deal"""
        data = {
            'flash_price': '15.99',
            'duration_hours': '2'
        }

        response = self.client.post(
            f'{self.base_url}/listings/{self.listing_id}/convert-to-flash-deal',
            json=data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertLess(float(response_data['flash_deal']['flash_price']),
                        float(response_data['flash_deal']['original_price']))

    def test_get_active_flash_deals(self):
        """Test getting active flash deals"""
        # First create a flash deal
        self.test_create_flash_deal()

        response = self.client.get(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertGreater(len(response_data['flash_deals']), 0)

    def test_get_flash_deals_by_location(self):
        """Test getting flash deals near a location"""
        # First create a flash deal
        self.test_create_flash_deal()

        params = {
            'latitude': '41.015137',
            'longitude': '28.979530',
            'radius': '10'  # km
        }

        response = self.client.get(
            f'{self.base_url}/flash-deals',
            query_string=params,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertIn('flash_deals', response_data)

    def test_flash_deal_expiration(self):
        """Test flash deal expiration"""
        # Create a flash deal with short duration
        data = {
            'title': 'Quick Flash Deal',
            'description': 'Expires soon',
            'original_price': '20.99',
            'flash_price': '10.99',
            'quantity': '5',
            'duration_hours': '1'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            json=data,
            headers=self.owner_headers
        )

        response_data = json.loads(response.data.decode('utf-8'))
        flash_deal_id = response_data['flash_deal']['id']

        # Check it's active initially
        response = self.client.get(
            f'{self.base_url}/flash-deals/{flash_deal_id}',
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['flash_deal']['active'])

    def test_flash_deal_purchase(self):
        """Test purchasing a flash deal"""
        # Create a flash deal
        data = {
            'title': 'Flash Deal',
            'description': 'Limited time offer',
            'original_price': '20.99',
            'flash_price': '10.99',
            'quantity': '5',
            'duration_hours': '2'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            json=data,
            headers=self.owner_headers
        )

        response_data = json.loads(response.data.decode('utf-8'))
        flash_deal_id = response_data['flash_deal']['id']

        # Try to purchase the flash deal
        purchase_data = {
            'quantity': 1
        }

        response = self.client.post(
            f'{self.base_url}/flash-deals/{flash_deal_id}/purchase',
            json=purchase_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])

    def test_flash_deal_remaining_quantity(self):
        """Test flash deal quantity updates after purchase"""
        # Create a flash deal with limited quantity
        data = {
            'title': 'Limited Flash Deal',
            'description': 'Only few available',
            'original_price': '20.99',
            'flash_price': '10.99',
            'quantity': '3',
            'duration_hours': '2'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            json=data,
            headers=self.owner_headers
        )

        response_data = json.loads(response.data.decode('utf-8'))
        flash_deal_id = response_data['flash_deal']['id']
        initial_quantity = response_data['flash_deal']['quantity']

        # Purchase one item
        purchase_data = {
            'quantity': 1
        }

        response = self.client.post(
            f'{self.base_url}/flash-deals/{flash_deal_id}/purchase',
            json=purchase_data,
            headers=self.customer_headers
        )

        # Check remaining quantity
        response = self.client.get(
            f'{self.base_url}/flash-deals/{flash_deal_id}',
            headers=self.customer_headers
        )

        response_data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response_data['flash_deal']['quantity'], initial_quantity - 1)


if __name__ == '__main__':
    unittest.main()