import unittest
from flask import Flask
from datetime import datetime, UTC
from decimal import Decimal
from src.models import db, Restaurant, RestaurantComment, Purchase, CommentBadge, User, Listing
from src.services.restaurant_comment_service import add_comment_service


class TestRestaurantCommentService(unittest.TestCase):
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

        self.listing = Listing(
            id=1,
            restaurant_id=1,
            title="Test Listing",
            price=Decimal('10.00'),
            original_price=Decimal('20.00')
        )

        self.purchase = Purchase(
            id=1,
            user_id=1,
            listing_id=1,
            restaurant_id=1,
            quantity=1,
            total_price=Decimal('10.00'),
            status='COMPLETED',
            purchase_date=datetime.now(UTC)
        )

        db.session.add_all([self.user, self.restaurant, self.listing, self.purchase])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_comment_success(self):
        data = {
            "comment": "Great food!",
            "rating": 4.5,
            "purchase_id": 1,
            "badge_names": ["fresh", "fast_delivery"]
        }

        response, status_code = add_comment_service(1, 1, data)
        self.assertEqual(status_code, 201)
        self.assertTrue(response["success"])

        comment = RestaurantComment.query.first()
        self.assertEqual(comment.comment, "Great food!")
        self.assertEqual(float(comment.rating), 4.5)

        badges = CommentBadge.query.all()
        self.assertEqual(len(badges), 2)

    def test_add_comment_invalid_restaurant(self):
        data = {
            "comment": "Great food!",
            "rating": 4.5,
            "purchase_id": 1
        }

        response, status_code = add_comment_service(999, 1, data)
        self.assertEqual(status_code, 404)
        self.assertFalse(response["success"])

    def test_add_comment_missing_rating(self):
        data = {
            "comment": "Great food!",
            "purchase_id": 1
        }

        response, status_code = add_comment_service(1, 1, data)
        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    def test_add_comment_invalid_rating(self):
        data = {
            "comment": "Great food!",
            "rating": 6,
            "purchase_id": 1
        }

        response, status_code = add_comment_service(1, 1, data)
        self.assertEqual(status_code, 400)
        self.assertFalse(response["success"])

    def test_add_comment_duplicate_purchase(self):
        data = {
            "comment": "Great food!",
            "rating": 4.5,
            "purchase_id": 1
        }

        add_comment_service(1, 1, data)
        response, status_code = add_comment_service(1, 1, data)
        self.assertEqual(status_code, 403)
        self.assertFalse(response["success"])

    def test_add_comment_invalid_purchase(self):
        data = {
            "comment": "Great food!",
            "rating": 4.5,
            "purchase_id": 999
        }

        response, status_code = add_comment_service(1, 1, data)
        self.assertEqual(status_code, 403)
        self.assertFalse(response["success"])


if __name__ == '__main__':
    unittest.main()