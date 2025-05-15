import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime, timezone, timedelta
from src.models import db, Restaurant, RestaurantPunishment
from src.services.restaurant_punishment_service import RestaurantPunishmentService


class TestRestaurantPunishmentService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.restaurant = Restaurant(
            id=1,
            owner_id=1,
            restaurantName="Test Restaurant",
            category="Test Category",
            longitude=28.979530,
            latitude=41.015137
        )
        db.session.add(self.restaurant)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.services.notification_service.NotificationService.send_notification_to_user')
    def test_issue_punishment_temporary(self, mock_notify):
        mock_notify.return_value = True
        punishment_data = {
            'duration_type': 'THREE_DAYS',
            'reason': 'Test Reason'
        }

        response, status_code = RestaurantPunishmentService.issue_punishment(1, punishment_data, 1)

        self.assertEqual(status_code, 201)
        self.assertTrue(response['success'])

        punishment = RestaurantPunishment.query.first()
        self.assertEqual(punishment.restaurant_id, 1)
        self.assertEqual(punishment.punishment_type, 'TEMPORARY')
        self.assertEqual(punishment.duration_days, 3)

    @patch('src.services.notification_service.NotificationService.send_notification_to_user')
    def test_issue_punishment_permanent(self, mock_notify):
        mock_notify.return_value = True
        punishment_data = {
            'duration_type': 'PERMANENT',
            'reason': 'Test Reason'
        }

        response, status_code = RestaurantPunishmentService.issue_punishment(1, punishment_data, 1)

        self.assertEqual(status_code, 201)
        self.assertTrue(response['success'])

        punishment = RestaurantPunishment.query.first()
        self.assertEqual(punishment.punishment_type, 'PERMANENT')
        self.assertIsNone(punishment.duration_days)

    def test_issue_punishment_invalid_restaurant(self):
        punishment_data = {
            'duration_type': 'THREE_DAYS',
            'reason': 'Test Reason'
        }

        response, status_code = RestaurantPunishmentService.issue_punishment(999, punishment_data, 1)
        self.assertEqual(status_code, 404)
        self.assertFalse(response['success'])

    def test_issue_punishment_invalid_duration(self):
        punishment_data = {
            'duration_type': 'INVALID',
            'reason': 'Test Reason'
        }

        response, status_code = RestaurantPunishmentService.issue_punishment(1, punishment_data, 1)
        self.assertEqual(status_code, 400)
        self.assertFalse(response['success'])

    def test_check_restaurant_status_no_punishment(self):
        status = RestaurantPunishmentService.check_restaurant_status(1)
        self.assertFalse(status['is_punished'])

    def test_check_restaurant_status_with_punishment(self):
        punishment = RestaurantPunishment(
            restaurant_id=1,
            reason='Test Reason',
            punishment_type='TEMPORARY',
            duration_days=3,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=3),
            created_by=1
        )
        db.session.add(punishment)
        db.session.commit()

        status = RestaurantPunishmentService.check_restaurant_status(1)
        self.assertTrue(status['is_punished'])
        self.assertEqual(status['punishment_type'], 'TEMPORARY')


if __name__ == '__main__':
    unittest.main()