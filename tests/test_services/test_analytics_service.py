import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from decimal import Decimal
from flask import Flask
from src.models import db, Restaurant, Purchase, PurchaseStatus, RestaurantComment
from src.services.analytics_service import RestaurantAnalyticsService


class TestRestaurantAnalyticsService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_owner_analytics_no_restaurants(self):
        with patch('src.services.analytics_service.Restaurant.query') as mock_restaurant_query:
            mock_restaurant_query.filter_by.return_value.all.return_value = []

            response, status = RestaurantAnalyticsService.get_owner_analytics(1)

            self.assertEqual(status, 404)
            self.assertFalse(response['success'])
            self.assertEqual(response['message'], 'No restaurants found for this owner')

    def test_get_owner_analytics_with_data(self):
        test_date = datetime(2025, 5, 15, 11, 19, 48, tzinfo=UTC)

        with patch('src.services.analytics_service.Restaurant.query') as mock_restaurant_query, \
                patch('src.services.analytics_service.Purchase.query') as mock_purchase_query, \
                patch('src.services.analytics_service.RestaurantComment.query') as mock_comment_query, \
                patch('src.services.analytics_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = test_date

            mock_restaurant = MagicMock()
            mock_restaurant.id = 1
            mock_restaurant.restaurantName = "Test Restaurant"
            mock_restaurant.rating = 4.5
            mock_restaurant.ratingCount = 10

            mock_restaurant_query.filter_by.return_value.all.return_value = [mock_restaurant]

            mock_purchase = MagicMock()
            mock_purchase.quantity = 2
            mock_purchase.total_price = "25.00"
            mock_purchase.delivery_district = "Test District"

            mock_purchase_query.filter.return_value.all.return_value = [mock_purchase]

            mock_comment = MagicMock()
            mock_comment.user.name = "Test User"
            mock_comment.rating = 4.5
            mock_comment.comment = "Great food!"
            mock_comment.timestamp = "2025-05-15T11:19:48+00:00"

            mock_comment_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_comment]

            response, status = RestaurantAnalyticsService.get_owner_analytics(1)

            self.assertEqual(status, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['monthly_stats']['total_products_sold'], 2)
            self.assertEqual(response['data']['monthly_stats']['total_revenue'], "25.00")
            self.assertEqual(response['data']['monthly_stats']['period'], "2025-05")
            self.assertEqual(response['data']['regional_distribution']["Test District"], 1)
            self.assertEqual(response['data']['restaurant_ratings']["Test Restaurant"]["average_rating"], 4.5)

    def test_get_restaurant_analytics_not_found(self):
        with patch('src.services.analytics_service.Restaurant.query') as mock_restaurant_query:
            mock_restaurant_query.get.return_value = None

            response, status = RestaurantAnalyticsService.get_restaurant_analytics(1)

            self.assertEqual(status, 404)
            self.assertFalse(response['success'])
            self.assertEqual(response['message'], 'Restaurant with ID 1 not found')

    def test_get_restaurant_analytics_with_data(self):
        test_date = datetime(2025, 5, 15, 11, 19, 48, tzinfo=UTC)

        with patch('src.services.analytics_service.Restaurant.query') as mock_restaurant_query, \
                patch('src.services.analytics_service.Purchase.query') as mock_purchase_query, \
                patch('src.services.analytics_service.RestaurantComment.query') as mock_comment_query, \
                patch('src.services.analytics_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = test_date

            mock_restaurant = MagicMock()
            mock_restaurant.id = 1
            mock_restaurant.restaurantName = "Test Restaurant"
            mock_restaurant.rating = 4.5
            mock_restaurant.ratingCount = 10

            mock_restaurant_query.get.return_value = mock_restaurant

            mock_purchase = MagicMock()
            mock_purchase.quantity = 2
            mock_purchase.total_price = "25.00"
            mock_purchase.delivery_district = "Test District"

            mock_purchase_query.filter.return_value.all.return_value = [mock_purchase]

            mock_comment = MagicMock()
            mock_comment.user.name = "Test User"
            mock_comment.rating = 4.5
            mock_comment.comment = "Great food!"
            mock_comment.timestamp = "2025-05-15T11:19:48+00:00"
            mock_comment.badges = []

            mock_comment_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_comment]

            response, status = RestaurantAnalyticsService.get_restaurant_analytics(1)

            self.assertEqual(status, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['monthly_stats']['total_products_sold'], 2)
            self.assertEqual(response['data']['monthly_stats']['total_revenue'], "25.00")
            self.assertEqual(response['data']['monthly_stats']['period'], "2025-05")
            self.assertEqual(response['data']['regional_distribution']["Test District"], 1)
            self.assertEqual(response['data']['restaurant_stats']["average_rating"], 4.5)
            self.assertEqual(response['data']['restaurant_stats']["recent_comments"][0]["user_name"], "Test User")


if __name__ == '__main__':
    unittest.main()