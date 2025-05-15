import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from flask import Flask
from src.models import db, Purchase, Restaurant, Listing
from src.services.business_notification_service import BusinessNotificationService


class TestBusinessNotificationService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test data
        self.listing = Listing(title="Test Listing")
        db.session.add(self.listing)

        self.restaurant = Restaurant(
            id=1,
            restaurantName="Test Restaurant",
            owner_id=1
        )
        db.session.add(self.restaurant)

        self.purchase = Purchase(
            id=1,
            restaurant_id=1,
            listing=self.listing,
            total_price="25.00",
            quantity=2
        )
        db.session.add(self.purchase)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_send_purchase_notification_success(self):
        with patch(
                'src.services.web_push_notification_service.WebPushNotificationService.send_notification_to_user_web') as mock_web_push:
            mock_web_push.return_value = True

            result = BusinessNotificationService.send_purchase_notification(self.purchase.id)

            self.assertTrue(result)
            mock_web_push.assert_called_once_with(
                self.restaurant.owner_id,
                "New Order Received!",
                f"New order: {self.purchase.quantity}x {self.listing.title} at {self.restaurant.restaurantName}",
                {
                    'type': 'new_purchase',
                    'purchase_id': self.purchase.id,
                    'listing_title': self.listing.title,
                    'total_price': str(self.purchase.total_price),
                    'quantity': self.purchase.quantity,
                    'restaurant_id': self.restaurant.id,
                    'restaurant_name': self.restaurant.restaurantName
                },
                icon="/static/images/logo.png",
                tag=f"purchase_{self.purchase.id}",
                require_interaction=True
            )

    def test_send_purchase_notification_purchase_not_found(self):
        result = BusinessNotificationService.send_purchase_notification(999)
        self.assertFalse(result)

    def test_send_purchase_notification_restaurant_not_found(self):
        non_existent_restaurant_id = 999
        purchase = Purchase(
            id=2,
            restaurant_id=non_existent_restaurant_id,
            listing=self.listing,
            total_price="25.00",
            quantity=2
        )
        db.session.add(purchase)
        db.session.commit()

        result = BusinessNotificationService.send_purchase_notification(purchase.id)
        self.assertFalse(result)

    def test_send_purchase_notification_web_push_fails(self):
        with patch(
                'src.services.web_push_notification_service.WebPushNotificationService.send_notification_to_user_web') as mock_web_push:
            mock_web_push.return_value = False

            result = BusinessNotificationService.send_purchase_notification(self.purchase.id)

            self.assertFalse(result)
            mock_web_push.assert_called_once()

    def test_send_purchase_notification_exception_handling(self):
        with patch(
                'src.services.web_push_notification_service.WebPushNotificationService.send_notification_to_user_web') as mock_web_push:
            mock_web_push.side_effect = Exception("Test error")

            result = BusinessNotificationService.send_purchase_notification(self.purchase.id)

            self.assertFalse(result)
            mock_web_push.assert_called_once()


if __name__ == '__main__':
    unittest.main()