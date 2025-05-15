import unittest
from flask import Flask
from src.models import db
from src.models.restaurant_badge_points_model import RestaurantBadgePoints
from src.services.restaurant_badge_services import (
    add_restaurant_badge_point,
    get_restaurant_badges,
    get_restaurant_badge_analytics,
    VALID_BADGES
)


class TestRestaurantBadgeServices(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_restaurant_id = 1

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_restaurant_badge_point(self):
        add_restaurant_badge_point(self.test_restaurant_id, 'fresh')
        badge_record = RestaurantBadgePoints.query.filter_by(restaurantID=self.test_restaurant_id).first()
        self.assertEqual(badge_record.freshPoint, 1)

    def test_add_invalid_badge_point(self):
        with self.assertRaises(ValueError):
            add_restaurant_badge_point(self.test_restaurant_id, 'invalid_badge')

    def test_get_restaurant_badges_empty(self):
        badges = get_restaurant_badges(self.test_restaurant_id)
        self.assertEqual(badges, [])

    def test_get_restaurant_badges_with_points(self):
        badge_points = RestaurantBadgePoints(
            restaurantID=self.test_restaurant_id,
            freshPoint=150,
            notFreshPoint=10,
            fastDeliveryPoint=200,
            slowDeliveryPoint=50,
            customerFriendlyPoint=90,
            notCustomerFriendlyPoint=10
        )
        db.session.add(badge_points)
        db.session.commit()

        badges = get_restaurant_badges(self.test_restaurant_id)
        self.assertIn('fresh', badges)
        self.assertIn('fast_delivery', badges)

    def test_get_restaurant_badge_analytics(self):
        badge_points = RestaurantBadgePoints(
            restaurantID=self.test_restaurant_id,
            freshPoint=100,
            notFreshPoint=20,
            fastDeliveryPoint=150,
            slowDeliveryPoint=30,
            customerFriendlyPoint=80,
            notCustomerFriendlyPoint=10
        )
        db.session.add(badge_points)
        db.session.commit()

        analytics = get_restaurant_badge_analytics(self.test_restaurant_id)

        self.assertEqual(analytics['freshness']['fresh'], 100)
        self.assertEqual(analytics['freshness']['not_fresh'], 20)
        self.assertEqual(analytics['delivery']['fast_delivery'], 150)
        self.assertEqual(analytics['delivery']['slow_delivery'], 30)
        self.assertEqual(analytics['customer_service']['customer_friendly'], 80)
        self.assertEqual(analytics['customer_service']['not_customer_friendly'], 10)

    def test_get_restaurant_badge_analytics_nonexistent(self):
        analytics = get_restaurant_badge_analytics(999)
        self.assertEqual(analytics['freshness']['fresh'], 0)
        self.assertEqual(analytics['delivery']['fast_delivery'], 0)
        self.assertEqual(analytics['customer_service']['customer_friendly'], 0)

    def test_valid_badges_constant(self):
        self.assertEqual(len(VALID_BADGES), 6)
        self.assertIn('fresh', VALID_BADGES)
        self.assertIn('fast_delivery', VALID_BADGES)
        self.assertIn('customer_friendly', VALID_BADGES)
        self.assertIn('not_fresh', VALID_BADGES)
        self.assertIn('slow_delivery', VALID_BADGES)
        self.assertIn('not_customer_friendly', VALID_BADGES)


if __name__ == '__main__':
    unittest.main()