# tests/test_services/test_comment_analysis_service.py

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, Restaurant, RestaurantComment, User
from src.AI_services.comment_analysis_service import CommentAnalysisService, get_restaurant_comments


class TestCommentAnalysisService(unittest.TestCase):
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
        self.owner = User(
            name="Restaurant Owner",
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

        # Current time for comment timestamps
        self.now = datetime.now()

        # Create test comments (less than 3 months old)
        self.comment1 = RestaurantComment(
            restaurant_id=self.restaurant.id,
            user_id=self.customer.id,
            purchase_id=1,
            comment="The food was excellent and delivery was quick!",
            rating=Decimal('4.5'),
            timestamp=self.now - timedelta(days=10)
        )

        self.comment2 = RestaurantComment(
            restaurant_id=self.restaurant.id,
            user_id=self.customer.id,
            purchase_id=2,
            comment="Service was slow but food was great",
            rating=Decimal('3.5'),
            timestamp=self.now - timedelta(days=20)
        )

        # Create an old comment (more than 3 months old) that should be filtered out
        self.old_comment = RestaurantComment(
            restaurant_id=self.restaurant.id,
            user_id=self.customer.id,
            purchase_id=3,
            comment="Old comment that should be filtered out",
            rating=Decimal('3.0'),
            timestamp=self.now - timedelta(days=100)
        )

        db.session.add_all([self.comment1, self.comment2, self.old_comment])
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_restaurant_comments(self):
        """Test getting restaurant comments from the last 3 months"""
        comments = get_restaurant_comments(self.restaurant.id)

        # Check that we only get 2 comments (the 2 recent ones, not the old one)
        self.assertEqual(len(comments), 2)

        # Check that the comments have the expected text
        comment_texts = [c["text"] for c in comments]
        self.assertIn("The food was excellent and delivery was quick!", comment_texts)
        self.assertIn("Service was slow but food was great", comment_texts)
        self.assertNotIn("Old comment that should be filtered out", comment_texts)

        # Check that the comments have the expected structure
        for comment in comments:
            self.assertIn("text", comment)
            self.assertIn("rating", comment)
            self.assertIn("timestamp", comment)
            self.assertIn("user_id", comment)

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_with_no_api_key(self, mock_post, mock_os):
        """Test analyze_comments when the API key is missing"""
        # Mock the environment variable to be empty
        mock_os.getenv.return_value = None

        # This should raise a ValueError
        with self.assertRaises(ValueError):
            CommentAnalysisService()

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_with_no_comments(self, mock_post, mock_os):
        """Test analyze_comments when there are no comments"""
        # Remove all comments for the test restaurant
        RestaurantComment.query.filter_by(restaurant_id=self.restaurant.id).delete()
        db.session.commit()

        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        # Create the service and analyze comments
        service = CommentAnalysisService()
        result = service.analyze_comments(self.restaurant.id)

        # No API call should be made
        mock_post.assert_not_called()

        # Check the result
        self.assertEqual(result["restaurant_id"], self.restaurant.id)
        self.assertEqual(result["restaurant_name"], self.restaurant.restaurantName)
        self.assertEqual(result["good_aspects"], [])
        self.assertEqual(result["bad_aspects"], [])
        self.assertIn("message", result)

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_success_json_response(self, mock_post, mock_os):
        """Test analyze_comments with a successful response in JSON format"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        # Mock successful API response with JSON content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "good_aspects": ["Excellent food", "Quick delivery"],
                            "bad_aspects": ["Slow service"]
                        })
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Create the service and analyze comments
        service = CommentAnalysisService()
        result = service.analyze_comments(self.restaurant.id)

        # Check that the API was called with the right parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_api_key")
        self.assertEqual(kwargs["json"]["model"], "meta-llama/llama-4-scout-17b-16e-instruct")

        # Check the result
        self.assertEqual(result["restaurant_id"], self.restaurant.id)
        self.assertEqual(result["restaurant_name"], self.restaurant.restaurantName)
        self.assertEqual(result["comment_count"], 2)
        self.assertEqual(result["good_aspects"], ["Excellent food", "Quick delivery"])
        self.assertEqual(result["bad_aspects"], ["Slow service"])

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_success_markdown_json(self, mock_post, mock_os):
        """Test analyze_comments with a successful response in markdown JSON format"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        # Mock successful API response with JSON content wrapped in markdown
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """
                        Here is the analysis of the customer comments:

                        ```json
                        {
                          "good_aspects": ["Excellent food", "Quick delivery"],
                          "bad_aspects": ["Slow service"]
                        }
                        ```
                        """
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Create the service and analyze comments
        service = CommentAnalysisService()
        result = service.analyze_comments(self.restaurant.id)

        # Check the result
        self.assertEqual(result["good_aspects"], ["Excellent food", "Quick delivery"])
        self.assertEqual(result["bad_aspects"], ["Slow service"])

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_success_text_format(self, mock_post, mock_os):
        """Test analyze_comments with a successful response in text format"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        # Mock successful API response with text content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """
                        Analysis of customer comments:

                        Good aspects:
                        - Excellent food quality
                        - Fast delivery times

                        Bad aspects:
                        - Service could be slow at times
                        """
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Create the service and analyze comments
        service = CommentAnalysisService()
        result = service.analyze_comments(self.restaurant.id)

        # Check the result
        self.assertEqual(result["good_aspects"], ["Excellent food quality", "Fast delivery times"])
        self.assertEqual(result["bad_aspects"], ["Service could be slow at times"])

    @patch('src.AI_services.comment_analysis_service.os')
    @patch('src.AI_services.comment_analysis_service.requests.post')
    def test_analyze_comments_api_error(self, mock_post, mock_os):
        """Test analyze_comments with an API error"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API key"
        mock_response.raise_for_status.side_effect = Exception("401 Client Error: Unauthorized")
        mock_post.return_value = mock_response

        # Create the service and analyze comments
        service = CommentAnalysisService()
        result = service.analyze_comments(self.restaurant.id)

        # Check the result
        self.assertIn("error", result)
        self.assertEqual(result["restaurant_id"], self.restaurant.id)
        self.assertEqual(result["restaurant_name"], self.restaurant.restaurantName)

    def test_analyze_comments_nonexistent_restaurant(self):
        """Test analyze_comments with a nonexistent restaurant ID"""
        # Create the service
        service = CommentAnalysisService()

        # Test with a nonexistent restaurant ID
        result = service.analyze_comments(999)

        # Check the result
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Restaurant with ID 999 not found")

    @patch('src.AI_services.comment_analysis_service.os')
    def test_extract_json_from_markdown(self, mock_os):
        """Test the _extract_json_from_markdown method"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        service = CommentAnalysisService()

        # Test with JSON code block with language specifier
        content = """
        Here is the analysis:

        ```json
        {"good_aspects": ["Quality food"], "bad_aspects": ["Slow service"]}
        ```
        """
        extracted = service._extract_json_from_markdown(content)
        self.assertEqual(extracted, '{"good_aspects": ["Quality food"], "bad_aspects": ["Slow service"]}')

        # Test with code block without language specifier
        content = """
        Here is the analysis:

        ```
        {"good_aspects": ["Quality food"], "bad_aspects": ["Slow service"]}
        ```
        """
        extracted = service._extract_json_from_markdown(content)
        self.assertEqual(extracted, '{"good_aspects": ["Quality food"], "bad_aspects": ["Slow service"]}')

        # Test with no code block
        content = """
        Good aspects:
        - Quality food

        Bad aspects:
        - Slow service
        """
        extracted = service._extract_json_from_markdown(content)
        self.assertEqual(extracted, '')

    @patch('src.AI_services.comment_analysis_service.os')
    def test_extract_aspects_from_text(self, mock_os):
        """Test the _extract_aspects_from_text method"""
        # Mock the API key
        mock_os.getenv.return_value = "test_api_key"

        service = CommentAnalysisService()

        # Test with bullet points
        content = """
        Good aspects:
        - Quality food
        - Fast delivery

        Bad aspects:
        - Slow service
        - High prices
        """
        extracted = service._extract_aspects_from_text(content)
        self.assertEqual(extracted["good_aspects"], ["Quality food", "Fast delivery"])
        self.assertEqual(extracted["bad_aspects"], ["Slow service", "High prices"])

        # Test with asterisks instead of dashes
        content = """
        Positive aspects:
        * Quality food
        * Fast delivery

        Negative aspects:
        * Slow service
        * High prices
        """
        extracted = service._extract_aspects_from_text(content)
        self.assertEqual(extracted["good_aspects"], ["Quality food", "Fast delivery"])
        self.assertEqual(extracted["bad_aspects"], ["Slow service", "High prices"])

        # Test with numbered lists
        content = """
        Good aspects:
        1. Quality food
        2. Fast delivery

        Bad aspects:
        1. Slow service
        2. High prices
        """
        extracted = service._extract_aspects_from_text(content)
        self.assertEqual(extracted["good_aspects"], ["Quality food", "Fast delivery"])
        self.assertEqual(extracted["bad_aspects"], ["Slow service", "High prices"])


if __name__ == '__main__':
    unittest.main()