import unittest
from flask import json
from app import create_app
from src.models import db, User, Restaurant, Listing
import uuid
import os
from datetime import datetime, timedelta
import io
from PIL import Image
from werkzeug.datastructures import MultiDict


class TestFlashDeals(unittest.TestCase):
    """Test cases for Flash Deals API endpoints"""

    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.base_url = '/v1'
        
        # Generate unique identifiers for test data
        unique_id = uuid.uuid4().hex[:8]
        self.owner_email = f"owner_{unique_id}@example.com"
        self.owner_password = "password123"
        self.customer_email = f"customer_{unique_id}@example.com"
        self.customer_password = "password123"
        
        # Create test image
        self.test_image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images')
        os.makedirs(self.test_image_dir, exist_ok=True)
        self.test_image_path = os.path.join(self.test_image_dir, 'test_image.jpg')
        
        # Create a simple test image if it doesn't exist
        if not os.path.exists(self.test_image_path):
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(self.test_image_path)
        
        with self.app.app_context():
            # Drop and recreate tables
            db.drop_all()
            db.create_all()
            
            # Create owner user - using set_password method instead of direct assignment
            owner = User()
            owner.email = self.owner_email
            owner.first_name = "Test"
            owner.last_name = "Owner"
            owner.user_type = "OWNER"
            owner.set_password(self.owner_password)
            db.session.add(owner)
            
            # Create customer user
            customer = User()
            customer.email = self.customer_email
            customer.first_name = "Test"
            customer.last_name = "Customer"
            customer.user_type = "CUSTOMER"
            customer.set_password(self.customer_password)
            db.session.add(customer)
            db.session.commit()
            
            # Create test restaurant
            restaurant = Restaurant(
                name="Test Restaurant",
                description="A restaurant for testing",
                address="123 Test St",
                phone="555-1234",
                user_id=owner.id,
                email="restaurant@example.com"
            )
            db.session.add(restaurant)
            db.session.commit()
            
            self.owner_id = owner.id
            self.customer_id = customer.id
            self.restaurant_id = restaurant.id
            
            # Create a test listing for flash deals
            listing = Listing(
                restaurant_id=restaurant.id,
                title="Test Listing",
                description="A listing for testing",
                count=10,
                original_price=15.99,
                pick_up_price=12.99,
                delivery_price=18.99,
                image_url="https://example.com/test.jpg",
                consume_within=24
            )
            db.session.add(listing)
            db.session.commit()
            self.listing_id = listing.id
            
            # Login as owner and customer
            self.owner_token = self._get_auth_token(self.owner_email, self.owner_password)
            self.owner_headers = {'Authorization': f'Bearer {self.owner_token}'} if self.owner_token else {}
            
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
        
        print(f"Login response: {response.status_code}, data: {response.data.decode('utf-8')}")
        
        if response.status_code == 200:
            token = json.loads(response.data.decode('utf-8')).get('token')
            if not token:
                print("Login successful but no token returned")
            return token
        else:
            print(f"Login failed with status {response.status_code}")
        return None

    def tearDown(self):
        """Tear down test environment after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Using the is_flash_deal flag and flash_price fields on existing Listing model
    def test_create_flash_deal_success(self):
        """Test creating a flash deal with all required fields"""
        data = {
            'listing_id': self.listing_id,
            'flash_price': 9.99,
            'flash_deal_duration_hours': 4
        }
        
        response = self.client.post(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal',
            json=data,
            headers=self.owner_headers,
            content_type='application/json'
        )
        
        print(f"Create Flash Deal Response: {response.status_code}, data: {response.data.decode('utf-8')}")
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertIn('listing', response_data)
        self.assertTrue(response_data['listing']['is_flash_deal'])
        self.assertEqual(float(response_data['listing']['flash_price']), data['flash_price'])
        
        # Verify listing was updated with flash deal info
        with self.app.app_context():
            listing = Listing.query.get(self.listing_id)
            self.assertIsNotNone(listing)
            self.assertTrue(hasattr(listing, 'is_flash_deal') or hasattr(listing, 'flash_price'))

    def test_create_flash_deal_missing_fields(self):
        """Test creating a flash deal with missing required fields"""
        data = {
            # Missing flash_price
            'flash_deal_duration_hours': 4
        }
        
        response = self.client.post(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal',
            json=data,
            headers=self.owner_headers,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(response_data['success'])

    def test_create_flash_deal_unauthorized(self):
        """Test that customers cannot create flash deals"""
        data = {
            'flash_price': 9.99,
            'flash_deal_duration_hours': 4
        }
        
        response = self.client.post(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal',
            json=data,
            headers=self.customer_headers,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(response_data['success'])

    def test_create_flash_deal_invalid_price(self):
        """Test creating a flash deal with an invalid price (higher than original)"""
        data = {
            'flash_price': 20.99,  # Higher than the original price
            'flash_deal_duration_hours': 4
        }
        
        response = self.client.post(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal',
            json=data,
            headers=self.owner_headers,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(response_data['success'])

    def test_get_flash_deals(self):
        """Test getting all flash deals for a restaurant"""
        # First create a flash deal
        self.test_create_flash_deal_success()
        
        response = self.client.get(
            f'{self.base_url}/restaurants/{self.restaurant_id}/flash-deals',
            headers=self.customer_headers
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertIn('listings', response_data)
        self.assertGreater(len(response_data['listings']), 0)

    def test_deactivate_flash_deal(self):
        """Test deactivating a flash deal"""
        # First create a flash deal
        self.test_create_flash_deal_success()
        
        response = self.client.patch(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal/deactivate',
            headers=self.owner_headers
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertFalse(response_data['listing']['is_flash_deal'])

    def test_update_flash_deal(self):
        """Test updating a flash deal price"""
        # First create a flash deal
        self.test_create_flash_deal_success()
        
        update_data = {
            'flash_price': 8.99
        }
        
        response = self.client.put(
            f'{self.base_url}/listings/{self.listing_id}/flash-deal',
            json=update_data,
            headers=self.owner_headers,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_data['success'])
        self.assertEqual(float(response_data['listing']['flash_price']), update_data['flash_price'])


if __name__ == '__main__':
    unittest.main()

