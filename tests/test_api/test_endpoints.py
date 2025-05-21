import unittest
from flask import Flask, json
from app import create_app
from src.models import db, User, Restaurant, Listing
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, UTC
from decimal import Decimal
import uuid
from werkzeug.datastructures import MultiDict
from io import BytesIO


class TestAPIEndpoints(unittest.TestCase):
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

            # Login as owner
            self.owner_token = self._get_auth_token(self.owner_email, self.owner_password)
            self.owner_headers = {'Authorization': f'Bearer {self.owner_token}'} if self.owner_token else {}

            # Login as customer
            self.customer_token = self._get_auth_token(self.customer_email, self.customer_password)
            self.customer_headers = {'Authorization': f'Bearer {self.customer_token}'} if self.customer_token else {}

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

    def _create_test_restaurant(self):
        """Helper method to create a test restaurant"""
        form_data = {
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

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=form_data,
            headers=self.owner_headers
        )

        if response.status_code == 201:
            return json.loads(response.data.decode('utf-8'))['restaurant']
        return None

    def _create_test_listing(self, restaurant_id):
        """Helper method to create a test listing"""
        # Create a dummy image
        image = (BytesIO(b'dummy image data'), 'test_image.jpg')

        form_data = {
            'title': 'Test Listing',
            'description': 'Test Description',
            'original_price': '10.99',
            'pick_up_price': '8.99',
            'delivery_price': '12.99',
            'count': '5',
            'consume_within': '24',
            'image': image
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{restaurant_id}/listings',
            data=form_data,
            headers=self.owner_headers,
            content_type='multipart/form-data'
        )

        if response.status_code == 201:
            return json.loads(response.data.decode('utf-8'))['listing']
        return None

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Authentication Tests
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            f'{self.base_url}/login',
            json={
                'email': self.owner_email,
                'password': self.owner_password,
                'login_type': 'email',
                'password_login': True
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('token', data)

    def test_login_failure(self):
        """Test login with wrong password"""
        response = self.client.post(
            f'{self.base_url}/login',
            json={
                'email': self.owner_email,
                'password': 'wrongpassword',
                'login_type': 'email',
                'password_login': True
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    # Restaurant Tests
    def test_create_restaurant_success(self):
        """Test creating a restaurant with all required fields"""
        form_data = {
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

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=form_data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('restaurant', data)
        self.assertEqual(data['restaurant']['restaurantName'], form_data['restaurantName'])

    def test_create_restaurant_missing_required_fields(self):
        """Test creating a restaurant with missing required fields"""
        form_data = {
            'restaurantDescription': 'Test Description',
            'pickup': 'true',
            'delivery': 'true'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=form_data,
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_create_restaurant(self):
        """Test that customers cannot create restaurants"""
        form_data = {
            'restaurantName': 'Test Restaurant',
            'category': 'Test Category',
            'longitude': '28.979530',
            'latitude': '41.015137'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=form_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    # Listing Tests
    def test_create_listing(self):
        """Test creating a listing for a restaurant"""
        # First create a restaurant
        restaurant = self._create_test_restaurant()
        self.assertIsNotNone(restaurant)

        # Create a listing
        image = (BytesIO(b'dummy image data'), 'test_image.jpg')
        form_data = {
            'title': 'Test Listing',
            'description': 'Test Description',
            'original_price': '10.99',
            'pick_up_price': '8.99',
            'delivery_price': '12.99',
            'count': '5',
            'consume_within': '24',
            'image': image
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{restaurant["id"]}/listings',
            data=form_data,
            headers=self.owner_headers,
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('listing', data)

    # User Profile Tests
    def test_get_user_profile(self):
        """Test getting user profile"""
        response = self.client.get(
            f'{self.base_url}/user',
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['user_data']['email'], self.owner_email)

    def test_update_user_profile(self):
        """Test updating user profile"""
        new_username = "Updated Username"
        response = self.client.put(
            f'{self.base_url}/user/username',
            json={'username': new_username},
            headers=self.owner_headers
        )

        self.assertEqual(response.status_code, 200)

    # Search Tests
    def test_search_restaurants(self):
        """Test searching restaurants"""
        # First create a restaurant
        self._create_test_restaurant()

        response = self.client.get(
            f'{self.base_url}/search',
            query_string={
                'type': 'restaurant',
                'query': 'Test'
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(data['results']) > 0)

    # Flash Deals Tests
    def test_get_flash_deals(self):
        """Test getting flash deals"""
        # Create a restaurant with flash deals
        restaurant = self._create_test_restaurant()

        response = self.client.post(
            f'{self.base_url}/flash-deals',
            json={
                'latitude': 41.015137,
                'longitude': 28.979530,
                'radius': 10
            },
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()