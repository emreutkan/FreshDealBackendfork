# tests/test_services/test_purchase_service.py

import unittest
from decimal import Decimal
from datetime import datetime, UTC
from flask import Flask
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage, MultiDict
from io import BytesIO
from src.models import db, User, Restaurant, Listing, UserCart, Purchase
from src.models.purchase_model import PurchaseStatus
from src.services.purchase_service import (
    create_purchase_order_service,
    handle_restaurant_response_service,
    get_restaurant_purchases_service,
    get_user_active_orders_service,
    get_user_previous_orders_service,
    add_completion_image_service
)


class TestPurchaseService(unittest.TestCase):
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

        # Set up test timestamp
        self.test_timestamp = datetime(2025, 1, 27, 9, 23, 25, tzinfo=UTC)

        # Create test users
        self.owner = User(
            name="Test Owner",
            email="owner@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password123"),
            role="owner",
            email_verified=True
        )
        self.customer = User(
            name="Test Customer",
            email="customer@test.com",
            phone_number="+1234567891",
            password=generate_password_hash("password123"),
            role="customer",
            email_verified=True
        )
        db.session.add_all([self.owner, self.customer])
        db.session.commit()

        # Create test restaurant
        self.restaurant = Restaurant(
            owner_id=self.owner.id,
            restaurantName="Test Restaurant",
            restaurantDescription="Test Description",
            longitude=28.979530,
            latitude=41.015137,
            category="Test Category",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True,
            deliveryFee=Decimal('1.5')
        )
        db.session.add(self.restaurant)
        db.session.commit()

        # Create test listing
        self.listing = Listing(
            restaurant_id=self.restaurant.id,
            title="Test Item",
            description="Test Description",
            image_url="http://test.com/image.jpg",
            original_price=Decimal('10.99'),
            pick_up_price=Decimal('9.99'),
            delivery_price=Decimal('12.99'),
            count=10,
            consume_within=2
        )
        db.session.add(self.listing)
        db.session.commit()

        # Add item to customer's cart
        self.cart_item = UserCart(
            user_id=self.customer.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            count=2
        )
        db.session.add(self.cart_item)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_purchase_order_pickup(self):
        """Test creating a purchase order for pickup"""
        data = {
            "is_delivery": False,
            "pickup_notes": "Will pickup at 6 PM"
        }

        response, status_code = create_purchase_order_service(self.customer.id, data)

        self.assertEqual(status_code, 201)
        self.assertIn("Purchase order created successfully", response["message"])
        self.assertEqual(len(response["purchases"]), 1)
        self.assertEqual(response["purchases"][0]["quantity"], 2)
        self.assertEqual(float(response["purchases"][0]["total_price"]), 19.98)  # 2 * 9.99
        self.assertFalse(response["purchases"][0]["is_delivery"])

    def test_create_purchase_order_delivery(self):
        """Test creating a purchase order for delivery"""
        data = {
            "is_delivery": True,
            "delivery_address": "123 Test St",
            "delivery_notes": "Leave at door"
        }

        response, status_code = create_purchase_order_service(self.customer.id, data)

        self.assertEqual(status_code, 201)
        self.assertIn("Purchase order created successfully", response["message"])
        self.assertEqual(len(response["purchases"]), 1)
        self.assertEqual(response["purchases"][0]["quantity"], 2)
        self.assertEqual(float(response["purchases"][0]["total_price"]), 38.97)  # 2 * 12.99 * 1.5 (delivery fee)
        self.assertTrue(response["purchases"][0]["is_delivery"])

    def test_handle_restaurant_response_accept(self):
        """Test restaurant accepting an order"""
        # Create a pending purchase
        purchase = Purchase(
            user_id=self.customer.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=2,
            total_price=Decimal('25.98'),
            status=PurchaseStatus.PENDING,
            is_delivery=True,
            delivery_address="123 Test St"
        )
        db.session.add(purchase)
        db.session.commit()

        response, status_code = handle_restaurant_response_service(
            purchase.id,
            self.owner.id,
            'accept'
        )

        self.assertEqual(status_code, 200)
        self.assertIn("Purchase accepted successfully", response["message"])
        self.assertEqual(response["purchase"]["status"], PurchaseStatus.ACCEPTED.value)

    def test_handle_restaurant_response_reject(self):
        """Test restaurant rejecting an order"""
        # Create a pending purchase
        purchase = Purchase(
            user_id=self.customer.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=2,
            total_price=Decimal('25.98'),
            status=PurchaseStatus.PENDING,
            is_delivery=True,
            delivery_address="123 Test St"
        )
        db.session.add(purchase)
        db.session.commit()

        initial_stock = self.listing.count
        response, status_code = handle_restaurant_response_service(
            purchase.id,
            self.owner.id,
            'reject'
        )

        self.assertEqual(status_code, 200)
        self.assertIn("Purchase rejected successfully", response["message"])
        self.assertEqual(response["purchase"]["status"], PurchaseStatus.REJECTED.value)

        # Verify stock was restored
        self.listing = Listing.query.get(self.listing.id)
        self.assertEqual(self.listing.count, initial_stock + 2)

    def test_get_restaurant_purchases(self):
        """Test getting all purchases for a restaurant"""
        # Create test purchases
        purchases = [
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=2,
                total_price=Decimal('25.98'),
                status=PurchaseStatus.PENDING
            ),
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=1,
                total_price=Decimal('12.99'),
                status=PurchaseStatus.ACCEPTED
            )
        ]
        db.session.add_all(purchases)
        db.session.commit()

        response, status_code = get_restaurant_purchases_service(self.restaurant.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(response["purchases"]), 2)

    def test_add_completion_image(self):
        """Test adding a completion image to a purchase"""
        # Create an accepted purchase
        purchase = Purchase(
            user_id=self.customer.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=2,
            total_price=Decimal('25.98'),
            status=PurchaseStatus.ACCEPTED
        )
        db.session.add(purchase)
        db.session.commit()

        # Create a dummy image file
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        def mock_url_for(endpoint, filename=None, _external=False):
            return f"http://test.com/uploads/{filename}"

        response, status_code = add_completion_image_service(
            purchase.id,
            self.owner.id,
            image_file,
            mock_url_for
        )

        self.assertEqual(status_code, 200)
        self.assertIn("Completion image added successfully", response["message"])
        self.assertEqual(response["purchase"]["status"], PurchaseStatus.COMPLETED.value)
        self.assertTrue(response["purchase"]["completion_image_url"].startswith("http://test.com/uploads/"))

    def test_get_user_active_orders(self):
        """Test getting active orders for a user"""
        # Create some active orders
        purchases = [
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=2,
                total_price=Decimal('25.98'),
                status=PurchaseStatus.PENDING
            ),
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=1,
                total_price=Decimal('12.99'),
                status=PurchaseStatus.ACCEPTED
            )
        ]
        db.session.add_all(purchases)
        db.session.commit()

        response, status_code = get_user_active_orders_service(self.customer.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(response["active_orders"]), 2)

    def test_get_user_previous_orders(self):
        """Test getting previous orders for a user"""
        # Create some completed and rejected orders
        purchases = [
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=2,
                total_price=Decimal('25.98'),
                status=PurchaseStatus.COMPLETED
            ),
            Purchase(
                user_id=self.customer.id,
                listing_id=self.listing.id,
                restaurant_id=self.restaurant.id,
                quantity=1,
                total_price=Decimal('12.99'),
                status=PurchaseStatus.REJECTED
            )
        ]
        db.session.add_all(purchases)
        db.session.commit()

        response, status_code = get_user_previous_orders_service(self.customer.id, page=1, per_page=10)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(response["orders"]), 2)
        self.assertEqual(response["pagination"]["current_page"], 1)
        self.assertEqual(response["pagination"]["total_orders"], 2)


if __name__ == '__main__':
    unittest.main()