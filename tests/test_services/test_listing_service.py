# tests/test_services/test_listings_service.py

import unittest
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import MultiDict, FileStorage
from io import BytesIO
from src.models import db, Restaurant, Listing, User
from src.services.listings_service import (
    create_listing_service,
    get_listings_service,
    search_service,
    edit_listing_service,
    delete_listing_service
)


class TestListingsService(unittest.TestCase):
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

        # Create a test user (restaurant owner)
        self.test_user = User(
            name="Test Owner",
            email="owner@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password123"),
            role="owner",
            email_verified=True
        )
        db.session.add(self.test_user)
        db.session.commit()

        # Create test restaurant
        self.test_restaurant = Restaurant(
            owner_id=self.test_user.id,
            restaurantName="Test Restaurant",
            restaurantDescription="Test Description",
            longitude=28.979530,
            latitude=41.015137,
            category="Test Category",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )
        db.session.add(self.test_restaurant)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def mock_url_for(self, endpoint, filename=None, _external=False):
        """Mock url_for function for testing"""
        return f"http://test.com/uploads/{filename}"

    def test_create_listing(self):
        """Test creating a new listing"""
        form_data = MultiDict({
            'title': 'Test Listing',
            'description': 'A test listing',
            'original_price': '10.99',
            'pick_up_price': '9.99',
            'delivery_price': '12.99',
            'count': '5',
            'consume_within': '2'
        })

        # Create a dummy image file
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        response, status_code = create_listing_service(
            self.test_restaurant.id,
            self.test_user.id,
            form_data,
            image_file,
            self.mock_url_for
        )

        self.assertEqual(status_code, 201)
        self.assertTrue(response['success'])
        self.assertEqual(response['listing']['title'], 'Test Listing')
        self.assertEqual(float(response['listing']['original_price']), 10.99)

    def test_get_listings(self):
        """Test retrieving listings"""
        # Create some test listings
        listing1 = Listing(
            restaurant_id=self.test_restaurant.id,
            title="Listing 1",
            description="Description 1",
            image_url="http://test.com/image1.jpg",
            original_price=Decimal('10.99'),
            pick_up_price=Decimal('9.99'),
            delivery_price=Decimal('12.99'),
            count=5,
            consume_within=2
        )
        listing2 = Listing(
            restaurant_id=self.test_restaurant.id,
            title="Listing 2",
            description="Description 2",
            image_url="http://test.com/image2.jpg",
            original_price=Decimal('15.99'),
            pick_up_price=Decimal('14.99'),
            delivery_price=Decimal('17.99'),
            count=3,
            consume_within=3
        )

        db.session.add_all([listing1, listing2])
        db.session.commit()

        response, status_code = get_listings_service(
            self.test_restaurant.id,
            page=1,
            per_page=10,
            url_for_func=self.mock_url_for
        )

        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 2)
        self.assertEqual(response['data'][0]['title'], 'Listing 1')
        self.assertEqual(response['data'][1]['title'], 'Listing 2')

    def test_edit_listing(self):
        """Test editing an existing listing"""
        # Create a test listing
        listing = Listing(
            restaurant_id=self.test_restaurant.id,
            title="Original Title",
            description="Original Description",
            image_url="http://test.com/image.jpg",
            original_price=Decimal('10.99'),
            pick_up_price=Decimal('9.99'),
            delivery_price=Decimal('12.99'),
            count=5,
            consume_within=2
        )
        db.session.add(listing)
        db.session.commit()

        # Update the listing
        form_data = MultiDict({
            'title': 'Updated Title',
            'description': 'Updated Description',
            'original_price': '15.99',
            'count': '10'
        })

        response, status_code = edit_listing_service(
            listing.id,
            self.test_user.id,
            form_data,
            None,
            self.mock_url_for
        )

        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        self.assertEqual(response['listing']['title'], 'Updated Title')
        self.assertEqual(float(response['listing']['original_price']), 15.99)
        self.assertEqual(response['listing']['count'], 10)

    def test_delete_listing(self):
        """Test deleting a listing"""
        # Create a test listing
        listing = Listing(
            restaurant_id=self.test_restaurant.id,
            title="Test Listing",
            description="Test Description",
            image_url="http://test.com/image.jpg",
            original_price=Decimal('10.99'),
            pick_up_price=Decimal('9.99'),
            delivery_price=Decimal('12.99'),
            count=5,
            consume_within=2
        )
        db.session.add(listing)
        db.session.commit()

        response, status_code = delete_listing_service(listing.id)

        self.assertEqual(status_code, 200)
        self.assertIn('message', response)

        # Verify listing is deleted
        deleted_listing = Listing.query.get(listing.id)
        self.assertIsNone(deleted_listing)



if __name__ == '__main__':
    unittest.main()