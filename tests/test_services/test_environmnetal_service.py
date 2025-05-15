import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from flask import Flask
from src.models import db, Purchase, PurchaseStatus, EnvironmentalContribution
from src.services.environmental_service import EnvironmentalService


class TestEnvironmentalService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_datetime = datetime(2025, 5, 15, 11, 25, 48, tzinfo=UTC)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_calculate_co2_avoided_for_purchase(self):
        purchase = MagicMock()
        purchase.status = PurchaseStatus.COMPLETED
        purchase.quantity = 2

        result = EnvironmentalService.calculate_co2_avoided_for_purchase(purchase)
        self.assertEqual(result, Decimal('2.50'))

        # Test incomplete purchase
        purchase.status = PurchaseStatus.PENDING
        result = EnvironmentalService.calculate_co2_avoided_for_purchase(purchase)
        self.assertEqual(result, Decimal('0.00'))

    def test_record_contribution_for_purchase(self):
        purchase = Purchase(
            id=1,
            user_id=1,
            status=PurchaseStatus.COMPLETED,
            quantity=2,
            total_price='25.00',
            purchase_date=datetime.now(UTC),
            is_delivery=False,
            is_flash_deal=False
        )
        db.session.add(purchase)
        db.session.commit()

        # Test successful recording
        result = EnvironmentalService.record_contribution_for_purchase(1)
        self.assertTrue(result)

        contribution = EnvironmentalContribution.query.filter_by(purchase_id=1).first()
        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.co2_avoided, Decimal('2.50'))

        # Test duplicate recording
        result = EnvironmentalService.record_contribution_for_purchase(1)
        self.assertFalse(result)

        # Test non-existent purchase
        result = EnvironmentalService.record_contribution_for_purchase(999)
        self.assertFalse(result)

    def test_get_user_contributions(self):
        with patch('src.services.environmental_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_datetime

            contributions = [
                EnvironmentalContribution(
                    user_id=1,
                    purchase_id=1,
                    co2_avoided=Decimal('2.50'),
                    created_at=self.test_datetime
                ),
                EnvironmentalContribution(
                    user_id=1,
                    purchase_id=2,
                    co2_avoided=Decimal('1.25'),
                    created_at=self.test_datetime - timedelta(days=40)
                )
            ]

            db.session.add_all(contributions)
            db.session.commit()

            result = EnvironmentalService.get_user_contributions(1)

            self.assertTrue(result['success'])
            self.assertEqual(result['data']['total_co2_avoided'], 3.75)
            self.assertEqual(result['data']['monthly_co2_avoided'], 2.50)
            self.assertEqual(result['data']['unit'], 'kg CO2 equivalent')

    def test_get_all_users_contributions(self):
        with patch('src.services.environmental_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.test_datetime

            contributions = [
                EnvironmentalContribution(
                    user_id=1,
                    purchase_id=1,
                    co2_avoided=Decimal('2.50'),
                    created_at=self.test_datetime
                ),
                EnvironmentalContribution(
                    user_id=2,
                    purchase_id=2,
                    co2_avoided=Decimal('1.25'),
                    created_at=self.test_datetime
                ),
                EnvironmentalContribution(
                    user_id=1,
                    purchase_id=3,
                    co2_avoided=Decimal('1.25'),
                    created_at=self.test_datetime - timedelta(days=40)
                )
            ]

            db.session.add_all(contributions)
            db.session.commit()

            result = EnvironmentalService.get_all_users_contributions()

            self.assertTrue(result['success'])
            self.assertEqual(len(result['data']), 2)
            self.assertEqual(result['data'][0]['user_id'], 1)  # Highest total
            self.assertEqual(result['data'][0]['total_co2_avoided'], 3.75)
            self.assertEqual(result['data'][0]['monthly_co2_avoided'], 2.50)
            self.assertEqual(result['unit'], 'kg CO2 equivalent')


if __name__ == '__main__':
    unittest.main()