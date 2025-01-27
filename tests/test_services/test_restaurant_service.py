# tests/test_services/test_restaurant_service.py

import unittest
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, Restaurant, User
from src.services.restaurant_service import (
    create_restaurant_service,
    get_restaurants_service,
    get_restaurant_service,
    get_restaurants_proximity_service
)
from werkzeug.datastructures import MultiDict, FileStorage
from io import BytesIO

class TestRestaurantService(unittest.TestCase):
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

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_restaurant(self):
        """Test creating a new restaurant"""
        form_data = MultiDict({
            'restaurantName': 'Test Restaurant',
            'restaurantDescription': 'A test restaurant',
            'longitude': '28.979530',
            'latitude': '41.015137',
            'category': 'Test Category',
            'workingDays': ['Monday', 'Tuesday'],
            'workingHoursStart': '09:00',
            'workingHoursEnd': '22:00',
            'pickup': 'true',
            'delivery': 'true'
        })

        # Create a dummy image file
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )
        files = {'image': image_file}

        def mock_url_for(endpoint, filename=None, _external=False):
            return f"http://test.com/uploads/{filename}"

        response, status_code = create_restaurant_service(
            self.test_user.id,
            form_data,
            files,
            mock_url_for
        )

        self.assertEqual(status_code, 201)
        self.assertTrue(response['success'])
        self.assertEqual(response['restaurant']['restaurantName'], 'Test Restaurant')

    def test_get_restaurants(self):
        """Test retrieving restaurants for an owner"""
        # Create test restaurants
        restaurant1 = Restaurant(
            owner_id=self.test_user.id,
            restaurantName="Restaurant 1",
            restaurantDescription="Description 1",
            longitude=28.979530,
            latitude=41.015137,
            category="Category 1",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )
        restaurant2 = Restaurant(
            owner_id=self.test_user.id,
            restaurantName="Restaurant 2",
            restaurantDescription="Description 2",
            longitude=28.979531,
            latitude=41.015138,
            category="Category 2",
            workingDays="Wednesday,Thursday",
            workingHoursStart="10:00",
            workingHoursEnd="23:00",
            pickup=True,
            delivery=False
        )

        db.session.add_all([restaurant1, restaurant2])
        db.session.commit()

        restaurants, status_code = get_restaurants_service(self.test_user.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(restaurants), 2)
        self.assertEqual(restaurants[0]['restaurantName'], 'Restaurant 1')
        self.assertEqual(restaurants[1]['restaurantName'], 'Restaurant 2')

    def test_get_single_restaurant(self):
        """Test retrieving a single restaurant"""
        restaurant = Restaurant(
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
        db.session.add(restaurant)
        db.session.commit()

        response, status_code = get_restaurant_service(restaurant.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(response['restaurantName'], 'Test Restaurant')
        self.assertEqual(response['owner_id'], self.test_user.id)

    def test_get_restaurants_proximity(self):
        """Test retrieving restaurants based on proximity"""
        restaurant1 = Restaurant(
            owner_id=self.test_user.id,
            restaurantName="Near Restaurant",
            restaurantDescription="Near",
            longitude=28.979530,
            latitude=41.015137,
            category="Test",
            workingDays="Monday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )
        restaurant2 = Restaurant(
            owner_id=self.test_user.id,
            restaurantName="Far Restaurant",
            restaurantDescription="Far",
            longitude=29.979530,  # Much further away
            latitude=42.015137,
            category="Test",
            workingDays="Monday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )

        db.session.add_all([restaurant1, restaurant2])
        db.session.commit()

        # Search with a small radius around the first restaurant
        response, status_code = get_restaurants_proximity_service(
            41.015137,  # Same as restaurant1
            28.979530,  # Same as restaurant1
            radius=1  # 1km radius
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(response['restaurants']), 1)  # Should only find the near restaurant
        self.assertEqual(response['restaurants'][0]['restaurantName'], 'Near Restaurant')

if __name__ == '__main__':
    unittest.main()