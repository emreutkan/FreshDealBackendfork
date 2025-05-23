import unittest
from flask import json
from app import create_app
from src.models import db, User
from werkzeug.security import generate_password_hash
import uuid


class TestAuth(unittest.TestCase):
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

            # Create test user
            unique_id = str(uuid.uuid4())[:8]
            self.test_email = f"test_{unique_id}@example.com"
            self.test_password = "password123"

            test_user = User(
                name="Test User",
                email=self.test_email,
                phone_number="+1234567890",
                password=generate_password_hash(self.test_password),
                role="owner",
                email_verified=True
            )

            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_success(self):
        """Test successful login"""
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

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('token', data)
        self.assertTrue(data['success'])

    def test_login_failure_wrong_password(self):
        """Test login with wrong password"""
        login_data = {
            'email': self.test_email,
            'password': 'wrongpassword',
            'login_type': 'email',
            'password_login': True
        }

        response = self.client.post(
            f'{self.base_url}/login',
            json=login_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data['success'])

    def test_register_success(self):
        """Test successful user registration"""
        register_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'phone_number': '+1234567892',
            'role': 'customer'
        }

        response = self.client.post(
            f'{self.base_url}/register',
            json=register_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        register_data = {
            'name': 'Duplicate User',
            'email': self.test_email,  # Using existing email
            'password': 'password123',
            'phone_number': '+1234567893',
            'role': 'customer'
        }

        response = self.client.post(
            f'{self.base_url}/register',
            json=register_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()