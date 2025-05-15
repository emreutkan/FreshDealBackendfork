import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from flask import Flask
from datetime import datetime, UTC
from src.models import db, User, CustomerAddress, Restaurant
from src.services.restaurant_notification_service import notify_users_about_new_restaurant, calculate_distance


class TestRestaurantNotificationService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            id=1,
            email='test@test.com',
            phone_number='+901234567890',
            name='Test User',
            password='hashedpassword',
            role='customer'
        )

        self.restaurant = Restaurant(
            id=1,
            owner_id=2,
            restaurantName="Test Restaurant",
            category="Test Category",
            longitude=Decimal('28.979530'),
            latitude=Decimal('41.015137')
        )

        self.address = CustomerAddress(
            id=1,
            user_id=1,
            address='Test Address',
            longitude=Decimal('28.979540'),
            latitude=Decimal('41.015140'),
            is_primary=True
        )

        db.session.add_all([self.user, self.restaurant, self.address])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.services.notification_service.NotificationService.send_notification_to_user')
    def test_notify_users_about_new_restaurant(self, mock_send_notification):
        mock_send_notification.return_value = True
        result = notify_users_about_new_restaurant(1)
        self.assertEqual(result, 1)
        mock_send_notification.assert_called_once()

    def test_notify_users_nonexistent_restaurant(self):
        result = notify_users_about_new_restaurant(999)
        self.assertEqual(result, 0)

    def test_calculate_distance(self):
        distance = calculate_distance(
            float(self.restaurant.latitude),
            float(self.restaurant.longitude),
            float(self.address.latitude),
            float(self.address.longitude)
        )
        self.assertIsInstance(distance, float)
        self.assertLess(distance, 1)


if __name__ == '__main__':
    unittest.main()