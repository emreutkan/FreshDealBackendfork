import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from decimal import Decimal
from flask import Flask
from src.models import db, Purchase, Listing, Restaurant, PurchaseStatus
from src.services.recommendation_system_service import RecommendationSystemService, \
    RestaurantRecommendationSystemService


class TestRecommendationSystemService(unittest.TestCase):
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
            longitude=Decimal('28.979530'),
            latitude=Decimal('41.015137')
        )

        self.listing1 = Listing(
            id=1,
            restaurant_id=1,
            title="Test Listing 1",
            price=Decimal('10.00'),
            original_price=Decimal('20.00')
        )

        self.listing2 = Listing(
            id=2,
            restaurant_id=1,
            title="Test Listing 2",
            price=Decimal('15.00'),
            original_price=Decimal('25.00')
        )

        self.purchase1 = Purchase(
            id=1,
            user_id=1,
            listing_id=1,
            restaurant_id=1,
            quantity=1,
            total_price=Decimal('10.00'),
            status=PurchaseStatus.COMPLETED,
            purchase_date=datetime.now(UTC)
        )

        self.purchase2 = Purchase(
            id=2,
            user_id=2,
            listing_id=2,
            restaurant_id=1,
            quantity=2,
            total_price=Decimal('30.00'),
            status=PurchaseStatus.COMPLETED,
            purchase_date=datetime.now(UTC)
        )

        db.session.add_all([self.restaurant, self.listing1, self.listing2, self.purchase1, self.purchase2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_initialize_model(self):
        service = RecommendationSystemService()
        result = service.initialize_model()
        self.assertTrue(result)
        self.assertTrue(service.is_initialized)

    def test_get_recommendations_for_listing(self):
        response, status_code = RecommendationSystemService.get_recommendations_for_listing(1)
        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)

    def test_get_recommendations_for_nonexistent_listing(self):
        response, status_code = RecommendationSystemService.get_recommendations_for_listing(999)
        self.assertEqual(status_code, 404)
        self.assertFalse(response['success'])

    def test_restaurant_initialize_model(self):
        service = RestaurantRecommendationSystemService()
        result = service.initialize_model()
        self.assertTrue(result)
        self.assertTrue(service.is_initialized)

    def test_get_restaurant_recommendations_by_user(self):
        response, status_code = RestaurantRecommendationSystemService.get_recommendations_by_user(1)
        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        self.assertIsInstance(response['data'], list)

    def test_get_restaurant_recommendations_nonexistent_user(self):
        response, status_code = RestaurantRecommendationSystemService.get_recommendations_by_user(999)
        self.assertEqual(status_code, 404)
        self.assertFalse(response['success'])


if __name__ == '__main__':
    unittest.main()