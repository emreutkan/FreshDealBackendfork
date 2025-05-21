import unittest
from flask import json
from app import create_app
from src.models import db, User, Restaurant, Listing
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import MultiDict
import uuid
import os
from PIL import Image
from datetime import datetime, UTC
import io
import json as standard_json  # Standard json module for exception handling


class TestListings(unittest.TestCase):
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

            # Create test restaurant
            self.test_restaurant = Restaurant(
                owner_id=self.owner.id,
                restaurantName="Test Restaurant",
                restaurantDescription="Test Description",
                longitude=28.979530,
                latitude=41.015137,
                category="Test Category",
                workingDays="Monday,Tuesday",  # String format as expected by the model
                workingHoursStart="09:00",
                workingHoursEnd="22:00",
                pickup=True,
                delivery=True,
                restaurantEmail="restaurant@test.com",
                restaurantPhone="+1234567890",
                flash_deals_available=False,
                flash_deals_count=0
            )
            db.session.add(self.test_restaurant)
            db.session.commit()

            # Store the restaurant ID
            self.restaurant_id = self.test_restaurant.id

            # Login as owner and customer
            self.owner_token = self._get_auth_token(self.owner_email, self.owner_password)
            self.owner_headers = {'Authorization': f'Bearer {self.owner_token}'} if self.owner_token else {}

            if not self.owner_token:
                print("WARNING: Owner authentication failed. Tests will likely fail.")

            self.customer_token = self._get_auth_token(self.customer_email, self.customer_password)
            self.customer_headers = {'Authorization': f'Bearer {self.customer_token}'} if self.customer_token else {}

            if not self.customer_token:
                print("WARNING: Customer authentication failed. Tests will likely fail.")

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

        print(f"Login response: {response.status_code}, data: {response.data.decode('utf-8')}")

        if response.status_code == 200:
            token = json.loads(response.data.decode('utf-8')).get('token')
            if not token:
                print("Login successful but no token returned")
            return token
        else:
            print(f"Login failed with status {response.status_code}")
        return None

    def test_create_listing_success(self):
        """Test creating a listing with all required fields"""
        # Verify we have a valid token first
        if not self.owner_token:
            self.fail("Owner token is missing - authentication failed")

        # Read image into memory buffer
        with open(self.test_image_path, 'rb') as img_file:
            img_content = img_file.read()

        data = MultiDict([
            ('title', 'Test Listing'),
            ('description', 'Test Description'),
            ('original_price', '10.99'),
            ('pick_up_price', '8.99'),
            ('delivery_price', '12.99'),
            ('count', '5'),
            ('consume_within', '24')
        ])

        data.add('image', (io.BytesIO(img_content), 'test_image.jpg', 'image/jpeg'))

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/listings',
            data=data,
            content_type='multipart/form-data',
            headers=self.owner_headers
        )

        print(f"\nCreate Listing Response Status: {response.status_code}")
        print(f"Create Listing Response Data: {response.data.decode('utf-8')}")

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('listing', data)
        self.assertEqual(data['listing']['title'], 'Test Listing')

    def test_create_listing_missing_required_fields(self):
        """Test creating a listing with missing required fields"""
        # Verify we have a valid token first
        if not self.owner_token:
            self.fail("Owner token is missing - authentication failed")
            
        # Read image into memory buffer
        with open(self.test_image_path, 'rb') as img_file:
            img_content = img_file.read()
            
        # Create incomplete form data - missing title and prices
        data = MultiDict([
            ('description', 'Test Description'),
            ('count', '5')
        ])
        
        data.add('image', (io.BytesIO(img_content), 'test_image.jpg', 'image/jpeg'))
        
        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/listings',
            data=data,
            content_type='multipart/form-data',
            headers=self.owner_headers
        )
        
        print(f"Missing fields response: {response.status_code}, data: {response.data.decode('utf-8')}")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data['success'])

    def test_customer_cannot_create_listing(self):
        """Test that customers cannot create listings"""
        # Verify we have valid tokens
        if not self.customer_token:
            self.fail("Customer token is missing - authentication failed")

        # Read image into memory buffer
        with open(self.test_image_path, 'rb') as img_file:
            img_content = img_file.read()

        data = MultiDict([
            ('title', 'Test Listing'),
            ('description', 'Test Description'),
            ('original_price', '10.99'),
            ('pick_up_price', '8.99'),
            ('delivery_price', '12.99'),
            ('count', '5'),
            ('consume_within', '24')
        ])

        data.add('image', (io.BytesIO(img_content), 'test_image.jpg', 'image/jpeg'))

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant_id}/listings',
            data=data,
            content_type='multipart/form-data',
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_get_listings(self):
        """Test getting listings for a restaurant"""
        # First create a listing
        self.test_create_listing_success()
        
        print("Getting listings after creating one...")
        # Use the correct endpoint for getting listings
        response = self.client.get(
            f'{self.base_url}/listings?restaurant_id={self.restaurant_id}',  # Changed endpoint path
            headers=self.customer_headers
        )
        
        print(f"Get listings response: {response.status_code}, data: {response.data.decode('utf-8')}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertGreater(len(data['data']), 0)

    def test_update_listing(self):
        """Test updating a listing"""
        # First create a listing
        self.test_create_listing_success()

        # Get the listing ID from the database directly
        with self.app.app_context():
            listing = Listing.query.filter_by(restaurant_id=self.restaurant_id).first()
            if not listing:
                self.fail("No listing found to update")
            listing_id = listing.id
            
        # Update the listing
        update_data = {
            'title': 'Updated Listing',
            'description': 'Updated Description',
            'original_price': '15.99'
        }

        print(f"Updating listing with ID: {listing_id}")
        print(f"Update data: {update_data}")
        response = self.client.put(
            f'{self.base_url}/listings/{listing_id}',
            json=update_data,
            content_type='application/json',
            headers=self.owner_headers
        )
        
        print(f"Update response: {response.status_code}, data: {response.data.decode('utf-8')}")
        self.assertEqual(response.status_code, 200)
        
        try:
            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue(data['success'])
            # Check if the specific fields were updated in the response
            self.assertEqual(data['listing']['title'], update_data['title'], 
                            f"Title not updated correctly. Expected: {update_data['title']}, Got: {data['listing']['title']}")
            self.assertEqual(data['listing']['description'], update_data['description'])
            self.assertEqual(float(data['listing']['original_price']), float(update_data['original_price']))
        except Exception as e:
            self.fail(f"Error checking response: {str(e)}, Response: {response.data.decode('utf-8')}")

    def test_delete_listing(self):
        """Test deleting a listing"""
        # First create a listing
        self.test_create_listing_success()

        # Get the listing ID from the database directly
        with self.app.app_context():
            listing = Listing.query.filter_by(restaurant_id=self.restaurant_id).first()
            if not listing:
                self.fail("No listing found to delete")
            listing_id = listing.id

        # Delete the listing
        print(f"Deleting listing with ID: {listing_id}")
        response = self.client.delete(
            f'{self.base_url}/listings/{listing_id}',
            headers=self.owner_headers
        )
        
        print(f"Delete response: {response.status_code}, data: {response.data.decode('utf-8')}")
        self.assertEqual(response.status_code, 200)
        
        try:
            data = json.loads(response.data.decode('utf-8'))
            # Check for message field instead of success
            self.assertIn('message', data)
            self.assertEqual(data['message'], 'Listing deleted successfully')
        except Exception as e:
            self.fail(f"Error checking response: {str(e)}, Response: {response.data.decode('utf-8')}")

        # Verify listing is deleted
        with self.app.app_context():
            listing = Listing.query.get(listing_id)
            self.assertIsNone(listing, "Listing was not deleted from database")


if __name__ == '__main__':
    unittest.main()
