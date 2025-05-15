import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from decimal import Decimal
from flask import Flask
from src.models import db, User, DiscountEarned, Purchase
from src.services.gamification_services import add_discount_point, get_user_rankings, get_single_user_rank, \
    get_monthly_user_rankings, get_single_user_monthly_rank


class TestGamificationService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_datetime = datetime(2025, 5, 15, 11, 32, 25, tzinfo=UTC)

        self.user1 = User(id=1, name="Test User 1", email="test1@test.com")
        self.user2 = User(id=2, name="Test User 2", email="test2@test.com")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_discount_point(self):
        mock_purchase = MagicMock()
        mock_purchase.user_id = 1
        mock_purchase.total_price = '100.00'

        with patch('src.services.gamification_services.Purchase.query') as mock_purchase_query:
            mock_purchase_query.get.return_value = mock_purchase

            result = add_discount_point(1)
            self.assertTrue(result)

            discount = DiscountEarned.query.filter_by(user_id=1).first()
            self.assertIsNotNone(discount)
            self.assertEqual(discount.user_id, 1)
            self.assertEqual(float(discount.discount), 10.0)  # 10% of 100

    def test_get_user_rankings(self):
        discounts = [
            DiscountEarned(user_id=1, discount=Decimal('50.00')),
            DiscountEarned(user_id=1, discount=Decimal('30.00')),
            DiscountEarned(user_id=2, discount=Decimal('40.00'))
        ]
        db.session.add_all(discounts)
        db.session.commit()

        response = get_user_rankings()
        data = response.get_json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['user_id'], 1)  # Highest discount
        self.assertEqual(data[0]['total_discount'], 80.0)
        self.assertEqual(data[1]['user_id'], 2)
        self.assertEqual(data[1]['total_discount'], 40.0)

    def test_get_single_user_rank(self):
        discounts = [
            DiscountEarned(user_id=1, discount=Decimal('50.00')),
            DiscountEarned(user_id=2, discount=Decimal('75.00'))
        ]
        db.session.add_all(discounts)
        db.session.commit()

        response = get_single_user_rank(1)
        self.assertEqual(response['rank'], 2)  # Second place
        self.assertEqual(response['total_discount'], 50.0)

    def test_get_monthly_user_rankings(self):
        with patch('src.services.gamification_services.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_datetime

            discounts = [
                DiscountEarned(
                    user_id=1,
                    discount=Decimal('50.00'),
                    earned_at=self.test_datetime
                ),
                DiscountEarned(
                    user_id=2,
                    discount=Decimal('75.00'),
                    earned_at=self.test_datetime
                )
            ]
            db.session.add_all(discounts)
            db.session.commit()

            response = get_monthly_user_rankings()
            data = response.get_json()

            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['user_id'], 2)  # Highest monthly discount
            self.assertEqual(data[0]['total_discount'], 75.0)

    def test_get_single_user_monthly_rank(self):
        with patch('src.services.gamification_services.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_datetime

            discounts = [
                DiscountEarned(
                    user_id=1,
                    discount=Decimal('50.00'),
                    earned_at=self.test_datetime
                ),
                DiscountEarned(
                    user_id=2,
                    discount=Decimal('75.00'),
                    earned_at=self.test_datetime
                )
            ]
            db.session.add_all(discounts)
            db.session.commit()

            response = get_single_user_monthly_rank(1)
            data = response.get_json()

            self.assertEqual(data['rank'], 2)  # Second place
            self.assertEqual(data['total_discount'], 50.0)

    def test_get_user_rankings_no_users(self):
        response = get_user_rankings()
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_get_single_user_rank_user_not_found(self):
        response, status_code = get_single_user_rank(999)
        self.assertEqual(status_code, 404)
        self.assertEqual(response['error'], 'User not found')

    def test_get_single_user_rank_no_discounts(self):
        response = get_single_user_rank(1)
        self.assertEqual(response['rank'], 1)
        self.assertEqual(response['total_discount'], 0.0)


if __name__ == '__main__':
    unittest.main()