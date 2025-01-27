import unittest
from unittest.mock import Mock, patch
from datetime import datetime, UTC
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, User, CustomerAddress, UserFavorites
from src.services.user_service import (
    fetch_user_data,
    change_password,
    change_username,
    change_email,
    add_favorite,
    remove_favorite,
    get_favorites,
    authenticate_user
)


class TestUserService(unittest.TestCase):
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

        # Create test user
        self.test_password = "password123"
        self.test_user = User(
            name="Test User",
            email="test@example.com",
            phone_number="+1234567890",
            password=generate_password_hash(self.test_password),
            role="customer",
            email_verified=False
        )
        db.session.add(self.test_user)
        db.session.commit()

        # Store the user ID
        self.test_user_id = self.test_user.id

        # Create test address
        self.test_address = CustomerAddress(
            user_id=self.test_user_id,
            title="Home",
            longitude=28.979530,
            latitude=41.015137,
            street="Test Street",
            neighborhood="Test Neighborhood",
            district="Test District",
            province="Test Province",
            country="Test Country",
            postalCode="34000",
            apartmentNo="4",
            doorNo="2",
            is_primary=True
        )
        db.session.add(self.test_address)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_fetch_user_data_success(self):
        """Test successful user data fetching"""
        response, error = fetch_user_data(self.test_user_id)

        self.assertIsNone(error)
        self.assertIn("user_data", response)
        self.assertIn("user_address_list", response)
        self.assertEqual(response["user_data"]["email"], "test@example.com")
        self.assertEqual(len(response["user_address_list"]), 1)
        self.assertEqual(response["user_address_list"][0]["title"], "Home")

    def test_fetch_user_data_not_found(self):
        """Test fetching data for non-existent user"""
        response, error = fetch_user_data(999)

        self.assertIsNone(response)
        self.assertEqual(error, "User not found")

    def test_change_password_success(self):
        """Test successful password change"""
        success, message = change_password(
            self.test_user_id,
            self.test_password,
            "newpassword123"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Password updated successfully")

    def test_change_password_incorrect_old(self):
        """Test password change with incorrect old password"""
        success, message = change_password(
            self.test_user_id,
            "wrongpassword",
            "newpassword123"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Old password is incorrect")

    def test_change_username_success(self):
        """Test successful username change"""
        success, message = change_username(
            self.test_user_id,
            "New Username"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Username updated successfully")

        # Verify the change in database
        user = User.query.get(self.test_user_id)
        self.assertEqual(user.name, "New Username")

    def test_change_email_success(self):
        """Test successful email change"""
        success, message = change_email(
            self.test_user_id,
            "test@example.com",
            "newemail@example.com"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Email updated successfully")

        # Verify the change in database
        user = User.query.get(self.test_user_id)
        self.assertEqual(user.email, "newemail@example.com")

    def test_change_email_incorrect_old(self):
        """Test email change with incorrect old email"""
        success, message = change_email(
            self.test_user_id,
            "wrong@example.com",
            "newemail@example.com"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Old email is incorrect")

    def test_add_favorite_success(self):
        """Test adding a restaurant to favorites"""
        success, message = add_favorite(self.test_user_id, 1)

        self.assertTrue(success)
        self.assertEqual(message, "Restaurant added to favorites")

        # Verify in database
        favorite = UserFavorites.query.filter_by(
            user_id=self.test_user_id,
            restaurant_id=1
        ).first()
        self.assertIsNotNone(favorite)

    def test_add_favorite_duplicate(self):
        """Test adding a duplicate favorite restaurant"""
        # First add
        add_favorite(self.test_user_id, 1)

        # Try to add again
        success, message = add_favorite(self.test_user_id, 1)

        self.assertFalse(success)
        self.assertEqual(message, "Restaurant is already in your favorites")

    def test_remove_favorite_success(self):
        """Test removing a restaurant from favorites"""
        # First add a favorite
        add_favorite(self.test_user_id, 1)

        # Then remove it
        success, message = remove_favorite(self.test_user_id, 1)

        self.assertTrue(success)
        self.assertEqual(message, "Restaurant removed from favorites")

        # Verify in database
        favorite = UserFavorites.query.filter_by(
            user_id=self.test_user_id,
            restaurant_id=1
        ).first()
        self.assertIsNone(favorite)

    def test_get_favorites_success(self):
        """Test getting user's favorite restaurants"""
        # Add some favorites first
        add_favorite(self.test_user_id, 1)
        add_favorite(self.test_user_id, 2)

        favorites = get_favorites(self.test_user_id)

        self.assertEqual(len(favorites), 2)
        self.assertIn(1, favorites)
        self.assertIn(2, favorites)

    def test_authenticate_user_success_email(self):
        """Test successful user authentication with email"""
        success, message, user = authenticate_user(
            email="test@example.com",
            password=self.test_password
        )

        self.assertTrue(success)
        self.assertEqual(message, "Authenticated successfully.")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.test_user_id)

    def test_authenticate_user_success_phone(self):
        """Test successful user authentication with phone number"""
        success, message, user = authenticate_user(
            phone_number="+1234567890",
            password=self.test_password
        )

        self.assertTrue(success)
        self.assertEqual(message, "Authenticated successfully.")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.test_user_id)

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        success, message, user = authenticate_user(
            email="test@example.com",
            password="wrongpassword"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Incorrect password.")
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()