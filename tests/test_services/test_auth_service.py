import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_jwt_extended import JWTManager
from src.models import db
from email_validator import EmailNotValidError


class TestAuthService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['BASE_URL'] = 'http://test.com'

        # Initialize extensions
        JWTManager(self.app)
        db.init_app(self.app)

        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Set up mock user
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.phone_number = "+1234567890"
        self.mock_user.password = generate_password_hash("password123")
        self.mock_user.email_verified = False
        self.mock_user.reset_token = None
        self.mock_user.reset_token_expires = None
        self.mock_user.name = "Test User"
        self.mock_user.role = "customer"

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()



    @patch('src.services.auth_service.get_user_by_email')
    @patch('flask_jwt_extended.utils.create_access_token')
    def test_login_user_success(self, mock_create_token, mock_get_user):
        """Test successful user login with password"""
        from src.services.auth_service import login_user

        mock_get_user.return_value = self.mock_user
        mock_create_token.return_value = "test-token"

        data = {
            "email": "test@example.com",
            "password": "password123",
            "login_type": "email",
            "password_login": True,
            "step": "skip_verification"
        }

        response, status_code = login_user(data, "127.0.0.1")

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertIn("token", response)


    @patch('src.models.User.query')
    @patch('src.models.db.session.commit')
    def test_reset_password_success(self, mock_commit, mock_query):
        """Test successful password reset"""
        from src.services.auth_service import reset_password

        self.mock_user.reset_token = "valid_token"
        self.mock_user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        mock_query.filter_by.return_value.first.return_value = self.mock_user

        data = {
            "token": "valid_token",
            "new_password": "new_password123"
        }

        response, status_code = reset_password(data)

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertIsNone(self.mock_user.reset_token)
        self.assertIsNone(self.mock_user.reset_token_expires)
        mock_commit.assert_called_once()

    def test_register_user_missing_required_fields(self):
        """Test registration with missing required fields"""
        from src.services.auth_service import register_user

        data = {
            "name_surname": "John Doe"
            # Missing email and password
        }

        response, status_code = register_user(data)

        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    def test_login_user_missing_credentials(self):
        """Test login without required credentials"""
        from src.services.auth_service import login_user

        data = {
            "login_type": "email"
            # Missing email and password
        }

        response, status_code = login_user(data, "127.0.0.1")

        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    def test_register_user_invalid_phone_number(self):
        """Test registration with invalid phone number"""
        from src.services.auth_service import register_user

        data = {
            "name_surname": "John Doe",
            "phone_number": "invalid-number",
            "password": "password123",
            "role": "customer"
        }

        response, status_code = register_user(data)

        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    @patch('src.services.auth_service.get_user_by_email')
    @patch('src.services.communication.auth_code_generator.generate_verification_code')
    def test_login_user_send_code_success(self, mock_gen_code, mock_get_user):
        """Test successful login with code generation step"""
        from src.services.auth_service import login_user

        mock_get_user.return_value = self.mock_user
        mock_gen_code.return_value = (True, "123456")

        data = {
            "email": "test@example.com",
            "login_type": "email",
            "step": "send_code"
        }

        response, status_code = login_user(data, "127.0.0.1")

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])

    def test_reset_password_expired_token(self):
        """Test password reset with expired token"""
        from src.services.auth_service import reset_password

        # Create a mock user with an expired token
        self.mock_user.reset_token = "expired_token"
        self.mock_user.reset_token_expires = datetime.now(UTC) - timedelta(hours=1)

        with patch('src.models.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = self.mock_user

            data = {
                "token": "expired_token",
                "new_password": "new_password123"
            }

            response, status_code = reset_password(data)

            self.assertEqual(status_code, 400)
            self.assertFalse(response["success"])

    @patch('src.services.auth_service.validate_email')  # Change the patch path
    @patch('src.services.auth_service.get_user_by_email', return_value=None)
    @patch('src.models.db.session.commit')
    @patch('src.models.db.session.add')
    @patch('src.services.communication.email_service.send_email')
    @patch('src.services.communication.auth_code_generator.set_verification_code')
    def test_register_user_success(self, mock_code_gen, mock_email,
                                   mock_db_add, mock_db_commit, mock_get_user, mock_validate_email):
        """Test successful user registration"""
        from src.services.auth_service import register_user

        # Configure validate_email mock to return the email
        mock_validate_email.return_value = {"email": "john@example.com"}
        mock_code_gen.return_value = "123456"

        data = {
            "name_surname": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "customer"
        }

        response, status_code = register_user(data)

        self.assertEqual(status_code, 201)
        self.assertTrue(response["success"])
        mock_db_add.assert_called_once()
        mock_db_commit.assert_called_once()

    @patch('src.services.auth_service.validate_email')  # Add this patch
    @patch('src.services.auth_service.get_user_by_email')
    @patch('src.services.communication.auth_code_generator.verify_code')
    @patch('src.models.db.session.commit')
    def test_verify_email_code_success(self, mock_commit, mock_verify, mock_get_user, mock_validate_email):
        """Test successful email verification"""
        from src.services.auth_service import verify_email_code

        mock_get_user.return_value = self.mock_user
        mock_verify.return_value = True
        mock_validate_email.return_value = {"email": "test@example.com"}

        data = {
            "email": "test@example.com",
            "verification_code": "123456"
        }

        response, status_code = verify_email_code(data, "127.0.0.1")

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertTrue(self.mock_user.email_verified)
        mock_commit.assert_called_once()

    @patch('src.services.auth_service.validate_email')  # Add this patch
    @patch('src.services.auth_service.get_user_by_email')
    @patch('src.services.communication.email_service.send_email')
    @patch('src.models.db.session.commit')
    def test_initiate_password_reset_success(self, mock_commit, mock_email, mock_get_user, mock_validate_email):
        """Test successful password reset initiation"""
        from src.services.auth_service import initiate_password_reset

        mock_get_user.return_value = self.mock_user
        mock_validate_email.return_value = {"email": "test@example.com"}

        data = {
            "email": "test@example.com"
        }

        response, status_code = initiate_password_reset(data)

        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        mock_commit.assert_called_once()
        mock_email.assert_called_once()



if __name__ == '__main__':
    unittest.main()