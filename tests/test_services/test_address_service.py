import unittest
from unittest.mock import Mock, patch
from datetime import datetime, UTC
from flask import Flask
from src.models import db, CustomerAddress
from src.services.address_service import (
    create_address,
    list_addresses,
    get_address,
    update_address,
    delete_address
)


class TestAddressService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize extensions
        db.init_app(self.app)

        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Sample valid address data
        self.valid_address_data = {
            'title': 'Home',
            'longitude': 28.979530,
            'latitude': 41.015137,
            'street': 'Test Street',
            'neighborhood': 'Test Neighborhood',
            'district': 'Test District',
            'province': 'Test Province',
            'country': 'Test Country',
            'postalCode': '34000',
            'apartmentNo': '4',
            'doorNo': '2',
            'is_primary': True
        }

        # Test user ID
        self.test_user_id = 1

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_address(self):
        """Helper method to create a test address in the database"""
        address = CustomerAddress(
            user_id=self.test_user_id,
            **self.valid_address_data
        )
        db.session.add(address)
        db.session.commit()
        return address

    def test_create_address_success(self):
        """Test successful address creation"""
        response, status_code = create_address(self.test_user_id, self.valid_address_data)

        self.assertEqual(status_code, 201)
        self.assertTrue(response["success"])
        self.assertIn("address", response)

        # Verify address was created in database
        address = CustomerAddress.query.filter_by(user_id=self.test_user_id).first()
        self.assertIsNotNone(address)
        self.assertEqual(address.title, self.valid_address_data["title"])

    def test_create_address_missing_required_fields(self):
        """Test address creation with missing required fields"""
        invalid_data = {
            'title': 'Home',
            # Missing required fields
        }

        response, status_code = create_address(self.test_user_id, invalid_data)

        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    def test_list_addresses_success(self):
        """Test successful address listing"""
        # Create a test address
        self.create_test_address()

        response, status_code = list_addresses(self.test_user_id)

        self.assertEqual(status_code, 200)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["title"], self.valid_address_data["title"])

    def test_list_addresses_empty(self):
        """Test listing addresses when user has none"""
        response, status_code = list_addresses(self.test_user_id)

        self.assertEqual(status_code, 404)
        self.assertIn("message", response)

    def test_get_address_success(self):
        """Test successful address retrieval"""
        # Create a test address
        address = self.create_test_address()

        response, status_code = get_address(self.test_user_id, address.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(response["title"], self.valid_address_data["title"])

    def test_get_address_not_found(self):
        """Test getting non-existent address"""
        response, status_code = get_address(self.test_user_id, 999)

        self.assertEqual(status_code, 404)
        self.assertIn("message", response)

    def test_update_address_success(self):
        """Test successful address update"""
        # Create a test address
        address = self.create_test_address()

        update_data = {
            'title': 'Updated Home',
            'street': 'Updated Street'
        }

        response, status_code = update_address(self.test_user_id, address.id, update_data)

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertEqual(response["address"]["title"], "Updated Home")
        self.assertEqual(response["address"]["street"], "Updated Street")

    def test_delete_address_success(self):
        """Test successful address deletion"""
        # Create a test address
        address = self.create_test_address()

        response, status_code = delete_address(self.test_user_id, address.id)

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])

        # Verify the address was deleted
        deleted_address = CustomerAddress.query.get(address.id)
        self.assertIsNone(deleted_address)

    def test_delete_primary_address_with_fallback(self):
        """Test deleting primary address with fallback to another address"""
        # Create primary address
        primary_address = self.create_test_address()

        # Create secondary address
        secondary_data = self.valid_address_data.copy()
        secondary_data["title"] = "Work"
        secondary_data["is_primary"] = False
        secondary_address = CustomerAddress(
            user_id=self.test_user_id,
            **secondary_data
        )
        db.session.add(secondary_address)
        db.session.commit()

        response, status_code = delete_address(self.test_user_id, primary_address.id)

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertEqual(response["new_primary_address_id"], secondary_address.id)

        # Verify the secondary address is now primary
        updated_address = CustomerAddress.query.get(secondary_address.id)
        self.assertTrue(updated_address.is_primary)


if __name__ == '__main__':
    unittest.main()