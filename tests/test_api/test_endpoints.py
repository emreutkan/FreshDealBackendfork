import unittest
from flask import Flask, json
from app import create_app
from src.models import db, User, Restaurant, Listing
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, UTC
from decimal import Decimal
import uuid
from werkzeug.datastructures import MultiDict


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

            unique_id = str(uuid.uuid4())[:8]
            self.test_email = f"test_{unique_id}@example.com"
            self.test_password = "password123"
            self.test_user = User(
                name="Test User",
                email=self.test_email,
                phone_number="+1234567890",
                password=generate_password_hash(self.test_password),
                role="owner",
                email_verified=True
            )
            db.session.add(self.test_user)
            db.session.commit()

            login_data = {
                'email': self.test_email,
                'password': self.test_password,
                'login_type': 'email',
                'password_login': True
            }

            response = self.client.post(
                f'{self.base_url}/login',
                json=login_data,
                content_type='application/json'
            )

            if response.status_code == 200:
                response_data = json.loads(response.data.decode('utf-8'))
                self.auth_token = response_data.get('token')
                self.headers = {
                    'Authorization': f'Bearer {self.auth_token}'
                }
            else:
                print(f"Login failed with status code: {response.status_code}")

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_restaurants_endpoint(self):
        """Test GET /v1/restaurants endpoint"""
        response = self.client.get(
            f'{self.base_url}/restaurants',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "No restaurant found for the owner")

    def test_create_restaurant(self):
        """Test POST /v1/restaurants endpoint"""
        if not hasattr(self, 'auth_token'):
            self.skipTest("Auth token not available")

        # Create form data
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

        print("\nSending restaurant creation request...")
        print(f"Headers: {self.headers}")
        print(f"Form Data: {form_data}")

        response = self.client.post(
            f'{self.base_url}/restaurants',
            data=form_data,  # Use data instead of json for form data
            headers=self.headers
        )

        print(f"\nCreate Restaurant Response Status: {response.status_code}")
        print(f"Create Restaurant Response Headers: {dict(response.headers)}")
        print(f"Create Restaurant Response Data: {response.data.decode('utf-8')}")

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data['restaurant'])

    def test_user_profile(self):
        """Test GET /v1/user endpoint"""
        if not hasattr(self, 'auth_token'):
            self.skipTest("Auth token not available")

        response = self.client.get(
            f'{self.base_url}/user',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['user_data']['email'], self.test_email)
        self.assertEqual(data['user_data']['role'], 'owner')
        self.assertTrue(data['user_data']['email_verified'])

    def test_unauthorized_access(self):
        """Test endpoints with unauthorized access"""
        protected_endpoints = [
            ('POST', f'{self.base_url}/restaurants'),
            ('GET', f'{self.base_url}/user'),
            ('POST', f'{self.base_url}/cart'),
            ('GET', f'{self.base_url}/addresses')
        ]

        for method, endpoint in protected_endpoints:
            response = self.client.open(
                endpoint,
                method=method
            )
            self.assertEqual(
                response.status_code,
                401,
                f"Expected 401 for {method} {endpoint}, got {response.status_code}"
            )


if __name__ == '__main__':
    unittest.main()