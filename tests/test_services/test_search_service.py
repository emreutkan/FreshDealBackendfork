# tests/test_services/test_search_service.py

import unittest
from unittest.mock import patch, Mock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.services.search_service import search_restaurants, search_listings

# Mock the db to avoid using the real database
db = SQLAlchemy()

class TestSearchService(unittest.TestCase):
    def setUp(self):
        # Create a Flask app and configure the test database
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"  # In-memory SQLite database
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Initialize the SQLAlchemy instance with the Flask app
        db.init_app(self.app)

        # Push the application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all tables (mock setup)
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Remove the session and drop all tables after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

        # Pop the application context
        self.app_context.pop()

    @patch("app.models.Restaurant.query.filter")
    def test_search_restaurants(self, mock_filter):
        # Mock the database query
        mock_results = [
            Mock(
                id=1,
                restaurantName="Pizza Place",
                restaurantDescription="Best Pizza",
                image_url="url",
                rating=4.5,
                category="Italian",
            ),
            Mock(
                id=2,
                restaurantName="Burger Joint",
                restaurantDescription="Tasty Burgers",
                image_url="url",
                rating=4.0,
                category="Fast Food",
            ),
        ]
        mock_filter.return_value.all.return_value = mock_results

        results = search_restaurants("Pizza")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Pizza Place")

    @patch("app.models.Listing.query.filter")
    def test_search_listings(self, mock_filter):
        # Mock the database query
        mock_results = [
            Mock(
                id=1,
                restaurant_id=1,
                title="Pepperoni Pizza",
                description="Delicious pepperoni",
                image_url="url",
                price=12.99,
                count=10,
            ),
        ]
        mock_filter.return_value.all.return_value = mock_results

        results = search_listings("Pizza", 1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Pepperoni Pizza")


if __name__ == "__main__":
    unittest.main()
