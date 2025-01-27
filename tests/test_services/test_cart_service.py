# tests/test_services/test_cart_service.py

import unittest
from decimal import Decimal
from datetime import datetime, UTC
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, User, Restaurant, Listing, UserCart
from src.services.cart_service import (
    get_cart_items_service,
    add_to_cart_service,
    update_cart_item_service,
    remove_from_cart_service,
    reset_cart_service
)


class TestCartService(unittest.TestCase):
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

        # Create test users
        self.customer = User(
            name="Test Customer",
            email="customer@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password123"),
            role="customer",
            email_verified=True
        )
        db.session.add(self.customer)
        db.session.commit()

        # Create test restaurants
        self.restaurant1 = Restaurant(
            owner_id=1,  # Dummy owner ID
            restaurantName="Restaurant 1",
            restaurantDescription="Description 1",
            longitude=28.979530,
            latitude=41.015137,
            category="Test Category",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )
        self.restaurant2 = Restaurant(
            owner_id=1,  # Dummy owner ID
            restaurantName="Restaurant 2",
            restaurantDescription="Description 2",
            longitude=28.979531,
            latitude=41.015138,
            category="Test Category",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
        )
        db.session.add_all([self.restaurant1, self.restaurant2])
        db.session.commit()

        # Create test listings
        self.listing1 = Listing(
            restaurant_id=self.restaurant1.id,
            title="Test Item 1",
            description="Test Description 1",
            image_url="http://test.com/image1.jpg",
            original_price=Decimal('10.99'),
            pick_up_price=Decimal('9.99'),
            delivery_price=Decimal('12.99'),
            count=10,
            consume_within=2
        )
        self.listing2 = Listing(
            restaurant_id=self.restaurant1.id,
            title="Test Item 2",
            description="Test Description 2",
            image_url="http://test.com/image2.jpg",
            original_price=Decimal('15.99'),
            pick_up_price=Decimal('14.99'),
            delivery_price=Decimal('17.99'),
            count=5,
            consume_within=2
        )
        self.listing3 = Listing(
            restaurant_id=self.restaurant2.id,
            title="Test Item 3",
            description="Test Description 3",
            image_url="http://test.com/image3.jpg",
            original_price=Decimal('20.99'),
            pick_up_price=Decimal('19.99'),
            delivery_price=Decimal('22.99'),
            count=8,
            consume_within=2
        )
        db.session.add_all([self.listing1, self.listing2, self.listing3])
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_empty_cart(self):
        """Test getting an empty cart"""
        cart, status_code = get_cart_items_service(self.customer.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(cart), 0)

    def test_add_to_cart(self):
        """Test adding an item to cart"""
        response, status_code = add_to_cart_service(self.customer.id, self.listing1.id, 2)

        self.assertEqual(status_code, 201)
        self.assertEqual(response["message"], "Item added to cart")

        # Verify cart contents
        cart, _ = get_cart_items_service(self.customer.id)
        self.assertEqual(len(cart), 1)
        self.assertEqual(cart[0]["listing_id"], self.listing1.id)
        self.assertEqual(cart[0]["count"], 2)

    def test_add_to_cart_insufficient_stock(self):
        """Test adding more items than available stock"""
        response, status_code = add_to_cart_service(self.customer.id, self.listing1.id, 15)

        self.assertEqual(status_code, 400)
        self.assertIn("Insufficient stock", response["message"])

    def test_add_from_different_restaurant(self):
        """Test adding items from different restaurants"""
        # Add first item
        add_to_cart_service(self.customer.id, self.listing1.id, 1)

        # Try to add item from different restaurant
        response, status_code = add_to_cart_service(self.customer.id, self.listing3.id, 1)

        self.assertEqual(status_code, 400)
        self.assertIn("Cannot add item from a different restaurant", response["message"])

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        # Add item to cart first
        add_to_cart_service(self.customer.id, self.listing1.id, 1)

        # Update quantity
        response, status_code = update_cart_item_service(self.customer.id, self.listing1.id, 3)

        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Cart item updated")

        # Verify updated quantity
        cart, _ = get_cart_items_service(self.customer.id)
        self.assertEqual(cart[0]["count"], 3)

    def test_remove_from_cart(self):
        """Test removing an item from cart"""
        # Add item to cart first
        add_to_cart_service(self.customer.id, self.listing1.id, 1)

        # Remove item
        response, status_code = remove_from_cart_service(self.customer.id, self.listing1.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Item removed from cart")

        # Verify cart is empty
        cart, _ = get_cart_items_service(self.customer.id)
        self.assertEqual(len(cart), 0)

    def test_reset_cart(self):
        """Test resetting the entire cart"""
        # Add multiple items to cart
        add_to_cart_service(self.customer.id, self.listing1.id, 1)
        add_to_cart_service(self.customer.id, self.listing2.id, 2)

        # Reset cart
        response, status_code = reset_cart_service(self.customer.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Cart reset successfully")

        # Verify cart is empty
        cart, _ = get_cart_items_service(self.customer.id)
        self.assertEqual(len(cart), 0)

    def test_update_nonexistent_item(self):
        """Test updating an item that's not in the cart"""
        response, status_code = update_cart_item_service(self.customer.id, self.listing1.id, 1)

        self.assertEqual(status_code, 404)
        self.assertEqual(response["message"], "Item not found in cart")

    def test_remove_nonexistent_item(self):
        """Test removing an item that's not in the cart"""
        response, status_code = remove_from_cart_service(self.customer.id, self.listing1.id)

        self.assertEqual(status_code, 404)
        self.assertEqual(response["message"], "Item not found in cart")


if __name__ == '__main__':
    unittest.main()