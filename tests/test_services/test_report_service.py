# tests/test_services/test_report_service.py

import unittest
from datetime import datetime, UTC
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage
from io import BytesIO
from src.models import db, User, Restaurant, Listing, Purchase, PurchaseReport
from src.models.purchase_model import PurchaseStatus
from src.services.report_service import (
    create_purchase_report_service,
    get_user_reports_service
)


class TestReportService(unittest.TestCase):
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
        self.test_timestamp = datetime(2025, 1, 27, 9, 36, 8, tzinfo=UTC)

        # Create test user
        self.user = User(
            name="Test User",
            email="user@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password123"),
            role="customer",
            email_verified=True
        )
        db.session.add(self.user)
        db.session.commit()

        # Create test restaurant
        self.restaurant = Restaurant(
            owner_id=1,  # Dummy owner ID
            restaurantName="Test Restaurant",
            restaurantDescription="Test Description",
            longitude=28.979530,
            latitude=41.015137,
            category="Test Category",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="22:00",
            pickup=True,
            delivery=True
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

        # Create test purchase
        self.purchase = Purchase(
            user_id=self.user.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=2,
            total_price=Decimal('25.98'),
            status=PurchaseStatus.COMPLETED,
            is_delivery=False
        )
        db.session.add(self.purchase)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def mock_url_for(self, endpoint, filename=None, _external=False):
        """Mock url_for function for testing"""
        return f"http://test.com/uploads/{filename}"

    def test_create_purchase_report(self):
        """Test creating a purchase report"""
        # Create a dummy image file
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        description = "Food quality was not as expected"

        response, status_code = create_purchase_report_service(
            self.user.id,
            self.purchase.id,
            image_file,
            description,
            self.mock_url_for
        )

        self.assertEqual(status_code, 201)
        self.assertIn("Report created successfully", response["message"])
        self.assertIn("report_id", response)

        # Verify report was created in database
        report = PurchaseReport.query.get(response["report_id"])
        self.assertIsNotNone(report)
        self.assertEqual(report.user_id, self.user.id)
        self.assertEqual(report.purchase_id, self.purchase.id)
        self.assertEqual(report.description, description)
        self.assertTrue(report.image_url.startswith("http://test.com/uploads/"))

    def test_create_duplicate_report(self):
        """Test attempting to create a duplicate report"""
        # Create first report
        image_file1 = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test1.jpg",
            content_type="image/jpeg"
        )
        create_purchase_report_service(
            self.user.id,
            self.purchase.id,
            image_file1,
            "First report",
            self.mock_url_for
        )

        # Try to create second report
        image_file2 = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test2.jpg",
            content_type="image/jpeg"
        )
        response, status_code = create_purchase_report_service(
            self.user.id,
            self.purchase.id,
            image_file2,
            "Second report",
            self.mock_url_for
        )

        self.assertEqual(status_code, 400)
        self.assertIn("already reported", response["message"])

    def test_create_report_invalid_purchase(self):
        """Test creating a report for an invalid purchase"""
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        response, status_code = create_purchase_report_service(
            self.user.id,
            999999,  # Non-existent purchase ID
            image_file,
            "Test description",
            self.mock_url_for
        )

        self.assertEqual(status_code, 404)
        self.assertIn("Purchase not found", response["message"])

    def test_create_report_invalid_file(self):
        """Test creating a report with an invalid file type"""
        image_file = FileStorage(
            stream=BytesIO(b"dummy content"),
            filename="test.txt",  # Invalid extension
            content_type="text/plain"
        )

        response, status_code = create_purchase_report_service(
            self.user.id,
            self.purchase.id,
            image_file,
            "Test description",
            self.mock_url_for
        )

        self.assertEqual(status_code, 400)
        self.assertIn("Invalid file type", response["message"])

    def test_get_user_reports(self):
        """Test getting all reports for a user"""
        # Create some test reports
        image_file = FileStorage(
            stream=BytesIO(b"dummy image content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        # Create multiple reports for different purchases
        purchase2 = Purchase(
            user_id=self.user.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=1,
            total_price=Decimal('12.99'),
            status=PurchaseStatus.COMPLETED,
            is_delivery=False
        )
        db.session.add(purchase2)
        db.session.commit()

        create_purchase_report_service(
            self.user.id,
            self.purchase.id,
            image_file,
            "Report 1",
            self.mock_url_for
        )

        image_file.seek(0)  # Reset file pointer
        create_purchase_report_service(
            self.user.id,
            purchase2.id,
            image_file,
            "Report 2",
            self.mock_url_for
        )

        response, status_code = get_user_reports_service(self.user.id)

        self.assertEqual(status_code, 200)
        self.assertIn("reports", response)
        self.assertEqual(len(response["reports"]), 2)

        # Verify report contents
        self.assertEqual(response["reports"][0]["description"], "Report 1")
        self.assertEqual(response["reports"][1]["description"], "Report 2")


if __name__ == '__main__':
    unittest.main()