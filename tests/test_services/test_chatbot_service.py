import unittest
from datetime import datetime, timedelta
from flask import Flask
from src.models import db, User, Purchase, CustomerAddress
from src.services.chatbot_service import ChatbotService


class TestChatbotService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user with the correct field names from your User model
        self.test_user = User(
            name="Test User",
            email="test@example.com",
            phone_number="1234567890",
            password="hashed_password",
            role="customer"
        )
        db.session.add(self.test_user)
        db.session.commit()
        self.user_id = self.test_user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_start_conversation(self):
        response = ChatbotService.start_conversation(self.user_id)

        self.assertTrue(response['success'])
        self.assertIn('message', response)
        self.assertIn('options', response)
        self.assertEqual(len(response['options']), 3)
        self.assertIn('order status', response['options'][0].lower())
        self.assertIn('cancel', response['options'][1].lower())
        self.assertIn('address', response['options'][2].lower())

    def test_get_order_status_with_no_orders(self):
        response = ChatbotService.get_order_status(self.user_id)

        self.assertFalse(response['success'])
        self.assertIn('message', response)
        self.assertIn('No active orders', response['message'])

    def test_get_order_status_with_active_order(self):
        # Create a test purchase
        purchase = Purchase(
            user_id=self.user_id,
            listing_id=1,
            status="PROCESSING",
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(purchase)
        db.session.commit()

        response = ChatbotService.get_order_status(self.user_id)

        self.assertTrue(response['success'])
        self.assertEqual(response['order_status'], 'PROCESSING')
        self.assertEqual(response['listing_id'], 1)

    def test_get_order_status_with_canceled_order(self):
        # Create a canceled purchase
        purchase = Purchase(
            user_id=self.user_id,
            listing_id=1,
            status="CANCELED",
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(purchase)
        db.session.commit()

        response = ChatbotService.get_order_status(self.user_id)

        self.assertFalse(response['success'])
        self.assertIn('No active orders', response['message'])

    def test_cancel_order_with_no_orders(self):
        response = ChatbotService.cancel_order(self.user_id)

        self.assertFalse(response['success'])
        self.assertIn('No active order', response['message'])

    def test_cancel_order_with_active_order(self):
        # Create a test purchase
        purchase = Purchase(
            user_id=self.user_id,
            listing_id=1,
            status="PROCESSING",
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(purchase)
        db.session.commit()

        response = ChatbotService.cancel_order(self.user_id)

        self.assertTrue(response['success'])
        self.assertIn('successfully canceled', response['message'])

        # Verify the order was actually canceled in the database
        updated_purchase = Purchase.query.get(purchase.id)
        self.assertEqual(updated_purchase.status, 'CANCELED')
        self.assertIsNotNone(updated_purchase.canceled_at)

    def test_update_user_address(self):
        address_data = {
            "title": "Home",
            "longitude": 34.123456,
            "latitude": 41.987654,
            "street": "Test Street",
            "neighborhood": "Test Neighborhood",
            "district": "Test District",
            "province": "Test Province",
            "country": "Test Country",
            "postalCode": "12345",
            "apartmentNo": "5",
            "doorNo": "10",
            "is_primary": True
        }

        response = ChatbotService.update_user_address(self.user_id, address_data)

        self.assertTrue(response['success'])
        self.assertIn('successfully updated', response['message'])

        # Verify the address was actually added in the database
        address = CustomerAddress.query.filter_by(user_id=self.user_id).first()
        self.assertIsNotNone(address)
        self.assertEqual(address.title, "Home")
        self.assertEqual(address.street, "Test Street")
        self.assertEqual(address.postalCode, "12345")
        self.assertTrue(address.is_primary)

    def test_update_user_address_nonexistent_user(self):
        address_data = {
            "title": "Home",
            "longitude": 34.123456,
            "latitude": 41.987654
        }

        response = ChatbotService.update_user_address(999, address_data)

        self.assertFalse(response['success'])
        self.assertIn('User not found', response['message'])


if __name__ == '__main__':
    unittest.main()
