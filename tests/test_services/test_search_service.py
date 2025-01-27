import unittest
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, Restaurant, Listing, User
from src.services.search_service import search_restaurants, search_listings


class TestSearchService(unittest.TestCase):
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

        # Create test restaurants
        self.restaurants = [
            Restaurant(
                owner_id=self.test_user.id,
                restaurantName="Pizza Palace",
                restaurantDescription="Best pizza in town",
                image_url="http://example.com/pizza.jpg",
                rating=Decimal('4.5'),
                category="Italian",
                restaurantEmail="pizza@test.com",
                restaurantPhone="+1234567890",
                pickup=True,
                delivery=True,
                longitude=28.979530,
                latitude=41.015137,
                workingDays="Monday,Tuesday,Wednesday,Thursday,Friday",
                workingHoursStart="09:00",
                workingHoursEnd="22:00"
            ),
            Restaurant(
                owner_id=self.test_user.id,
                restaurantName="Burger Bar",
                restaurantDescription="Amazing burgers",
                image_url="http://example.com/burger.jpg",
                rating=Decimal('4.2'),
                category="American",
                restaurantEmail="burger@test.com",
                restaurantPhone="+1234567891",
                pickup=True,
                delivery=True,
                longitude=28.979531,
                latitude=41.015138,
                workingDays="Monday,Tuesday,Wednesday,Thursday,Friday,Saturday",
                workingHoursStart="10:00",
                workingHoursEnd="23:00"
            ),
            Restaurant(
                owner_id=self.test_user.id,
                restaurantName="Sushi Palace",
                restaurantDescription="Fresh sushi",
                image_url="http://example.com/sushi.jpg",
                rating=Decimal('4.8'),
                category="Japanese",
                restaurantEmail="sushi@test.com",
                restaurantPhone="+1234567892",
                pickup=True,
                delivery=True,
                longitude=28.979532,
                latitude=41.015139,
                workingDays="Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday",
                workingHoursStart="11:00",
                workingHoursEnd="22:00"
            )
        ]

        # Add restaurants to database
        for restaurant in self.restaurants:
            db.session.add(restaurant)
        db.session.commit()

        # Store the first restaurant's ID for listing tests
        self.test_restaurant_id = self.restaurants[0].id

        # Create test listings for the first restaurant
        self.listings = [
            Listing(
                restaurant_id=self.test_restaurant_id,
                title="Margherita Pizza",
                description="Classic pizza with tomato and mozzarella",
                image_url="http://example.com/margherita.jpg",
                original_price=Decimal('10.99'),
                pick_up_price=Decimal('10.99'),
                delivery_price=Decimal('12.99'),
                count=50,
                consume_within=2,
                available_for_pickup=True,
                available_for_delivery=True
            ),
            Listing(
                restaurant_id=self.test_restaurant_id,
                title="Pepperoni Pizza",
                description="Pizza with pepperoni",
                image_url="http://example.com/pepperoni.jpg",
                original_price=Decimal('12.99'),
                pick_up_price=Decimal('12.99'),
                delivery_price=Decimal('14.99'),
                count=40,
                consume_within=2,
                available_for_pickup=True,
                available_for_delivery=True
            ),
            Listing(
                restaurant_id=self.test_restaurant_id,
                title="Vegetarian Special",
                description="Pizza with vegetables",
                image_url="http://example.com/veggie.jpg",
                original_price=Decimal('11.99'),
                pick_up_price=Decimal('11.99'),
                delivery_price=Decimal('13.99'),
                count=30,
                consume_within=2,
                available_for_pickup=True,
                available_for_delivery=True
            )
        ]

        # Add listings to database
        for listing in self.listings:
            db.session.add(listing)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_search_restaurants_exact_match(self):
        """Test searching restaurants with exact name match"""
        results = search_restaurants("Pizza Palace")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Pizza Palace")
        self.assertEqual(results[0]["category"], "Italian")
        self.assertEqual(float(results[0]["rating"]), 4.5)

    def test_search_restaurants_partial_match(self):
        """Test searching restaurants with partial name match"""
        results = search_restaurants("Palace")

        self.assertEqual(len(results), 2)  # Should find both Pizza Palace and Sushi Palace
        restaurant_names = [r["name"] for r in results]
        self.assertIn("Pizza Palace", restaurant_names)
        self.assertIn("Sushi Palace", restaurant_names)

    def test_search_restaurants_case_insensitive(self):
        """Test case-insensitive restaurant search"""
        results = search_restaurants("pizza")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Pizza Palace")

    def test_search_restaurants_no_results(self):
        """Test searching restaurants with no matches"""
        results = search_restaurants("Nonexistent Restaurant")

        self.assertEqual(len(results), 0)




    def test_search_listings_no_results(self):
        """Test searching listings with no matches"""
        results = search_listings("Nonexistent Item", self.test_restaurant_id)

        self.assertEqual(len(results), 0)

    def test_search_listings_wrong_restaurant(self):
        """Test searching listings with wrong restaurant ID"""
        results = search_listings("Pizza", 999)

        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()