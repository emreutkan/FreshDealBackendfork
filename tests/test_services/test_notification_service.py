# tests/test_services/test_notification_service.py


import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, User, UserDevice
from src.services.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):
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

        # Set specific test datetime
        self.test_datetime = datetime(2025, 1, 27, 9, 42, 15, tzinfo=UTC)

        # Create test user
        self.user = User(
            name="emreutkan",
            email="emreutkan@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password123"),
            role="customer",
            email_verified=True
        )
        db.session.add(self.user)
        db.session.commit()

        # Test data with exact expected formats
        self.raw_token = "test-token-123"  # The token without any wrapper
        self.expo_token = "ExponentPushToken[test-token-123]"  # The token with Expo wrapper

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_format_expo_token(self):
        """Test token formatting functionality"""
        # Test with cleaned token
        formatted = NotificationService.format_expo_token(self.raw_token)
        self.assertEqual(formatted, self.expo_token)

        # Test with already formatted token
        formatted = NotificationService.format_expo_token(self.expo_token)
        self.assertEqual(formatted, self.expo_token)



    @patch('requests.post')
    def test_send_push_notification(self, mock_post):
        """Test sending push notifications"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_post.return_value = mock_response

        success = NotificationService.send_push_notification(
            [self.raw_token],
            "Test Title",
            "Test Body",
            {"custom": "data"}
        )

        self.assertTrue(success)
        mock_post.assert_called_once()

        # Verify the request payload
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], NotificationService.EXPO_PUSH_API)
        self.assertIn('json', call_args[1])
        self.assertEqual(len(call_args[1]['json']), 1)
        notification = call_args[1]['json'][0]
        self.assertEqual(notification['title'], "Test Title")
        self.assertEqual(notification['body'], "Test Body")
        self.assertEqual(notification['data'], {"custom": "data"})

    def test_update_push_token(self):
        """Test updating push token"""
        success, message = NotificationService.update_push_token(
            self.user.id,
            self.expo_token,
            "ios",
            "14.0"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Push token updated successfully")

        # Update: Use clean_token to get the correct format for searching
        cleaned_token = NotificationService.clean_token(self.expo_token)
        device = UserDevice.query.filter_by(
            user_id=self.user.id,
            push_token=cleaned_token
        ).first()

        self.assertIsNotNone(device)
        self.assertEqual(device.device_type, "ios")
        self.assertEqual(device.platform, "14.0")
        self.assertTrue(device.is_active)

    def test_deactivate_token(self):
        """Test token deactivation"""
        # Update: Use clean_token to store the token in the correct format
        cleaned_token = NotificationService.clean_token(self.expo_token)

        # Create test device
        device = UserDevice(
            user_id=self.user.id,
            push_token=cleaned_token,  # Store the cleaned token
            device_type="ios",
            platform="14.0",
            is_active=True,
            created_at=datetime.now(UTC),
            last_used=datetime.now(UTC)
        )
        db.session.add(device)
        db.session.commit()

        # Test deactivation with Expo formatted token
        success = NotificationService.deactivate_token(self.expo_token)
        self.assertTrue(success)

        # Verify device was deactivated using the cleaned token
        device = UserDevice.query.filter_by(push_token=cleaned_token).first()
        self.assertIsNotNone(device, "Device should exist in database")
        self.assertFalse(device.is_active)

    def test_clean_inactive_tokens(self):
        """Test cleaning inactive tokens"""
        # Create test devices
        old_date = datetime.now(UTC) - timedelta(days=31)
        current_date = datetime.now(UTC)

        devices = [
            UserDevice(  # Should be cleaned
                user_id=self.user.id,
                push_token="token1",
                device_type="ios",
                platform="14.0",
                is_active=False,
                created_at=old_date,
                last_used=old_date
            ),
            UserDevice(  # Should not be cleaned (active)
                user_id=self.user.id,
                push_token="token2",
                device_type="ios",
                platform="14.0",
                is_active=True,
                created_at=old_date,
                last_used=old_date
            ),
            UserDevice(  # Should not be cleaned (recent)
                user_id=self.user.id,
                push_token="token3",
                device_type="ios",
                platform="14.0",
                is_active=False,
                created_at=current_date,
                last_used=current_date
            )
        ]
        db.session.add_all(devices)
        db.session.commit()

        cleaned_count = NotificationService.clean_inactive_tokens(30)
        self.assertEqual(cleaned_count, 1)

        # Verify only the old inactive device was cleaned
        remaining_devices = UserDevice.query.all()
        self.assertEqual(len(remaining_devices), 2)
        self.assertIn("token2", [d.push_token for d in remaining_devices])
        self.assertIn("token3", [d.push_token for d in remaining_devices])

    def test_get_user_devices(self):
        """Test getting user devices"""
        current_date = datetime.now(UTC)
        # Create test devices
        devices = [
            UserDevice(
                user_id=self.user.id,
                push_token=f"token{i}",
                device_type="ios",
                platform="14.0",
                is_active=True,
                created_at=current_date,
                last_used=current_date
            )
            for i in range(3)
        ]
        db.session.add_all(devices)
        db.session.commit()

        user_devices = NotificationService.get_user_devices(self.user.id)
        self.assertEqual(len(user_devices), 3)

        # Verify device information
        for device in user_devices:
            self.assertIn('id', device)
            self.assertIn('device_type', device)
            self.assertIn('platform', device)
            self.assertIn('created_at', device)
            self.assertIn('last_used', device)
            self.assertIn('is_active', device)


if __name__ == '__main__':
    unittest.main()