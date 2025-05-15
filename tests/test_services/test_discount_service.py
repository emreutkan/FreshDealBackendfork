import unittest
from decimal import Decimal
from src.services.discount_service import calculate_discount_amount, apply_discount
from unittest.mock import MagicMock


class TestDiscountService(unittest.TestCase):

    def test_calculate_discount_amount(self):
        # Test no discount case
        self.assertEqual(calculate_discount_amount('100'), Decimal('0'))

        # Test threshold cases
        self.assertEqual(calculate_discount_amount('150'), Decimal('50'))
        self.assertEqual(calculate_discount_amount('200'), Decimal('75'))
        self.assertEqual(calculate_discount_amount('250'), Decimal('100'))
        self.assertEqual(calculate_discount_amount('400'), Decimal('150'))

        # Test above threshold cases
        self.assertEqual(calculate_discount_amount('175'), Decimal('50'))
        self.assertEqual(calculate_discount_amount('225'), Decimal('75'))
        self.assertEqual(calculate_discount_amount('300'), Decimal('100'))
        self.assertEqual(calculate_discount_amount('500'), Decimal('150'))

    def test_apply_discount_empty_purchases(self):
        total, discount, purchases = apply_discount([])
        self.assertEqual(total, Decimal('0'))
        self.assertEqual(discount, Decimal('0'))
        self.assertEqual(purchases, [])

    def test_apply_discount_single_purchase(self):
        purchase = MagicMock()
        purchase.total_price = '200'

        total, discount, purchases = apply_discount([purchase])

        self.assertEqual(total, Decimal('200'))
        self.assertEqual(discount, Decimal('75'))
        self.assertEqual(len(purchases), 1)
        self.assertEqual(Decimal(purchases[0].total_price), Decimal('125'))

    def test_apply_discount_multiple_purchases(self):
        purchase1 = MagicMock()
        purchase1.total_price = '300'

        purchase2 = MagicMock()
        purchase2.total_price = '100'

        total, discount, purchases = apply_discount([purchase1, purchase2])

        self.assertEqual(total, Decimal('400'))
        self.assertEqual(discount, Decimal('150'))
        self.assertEqual(len(purchases), 2)

        # Verify proportional discount application
        self.assertAlmostEqual(Decimal(purchases[0].total_price), Decimal('187.50'), places=2)
        self.assertAlmostEqual(Decimal(purchases[1].total_price), Decimal('62.50'), places=2)

    def test_apply_discount_no_negative_totals(self):
        purchase = MagicMock()
        purchase.total_price = '50'

        total, discount, purchases = apply_discount([purchase])

        self.assertEqual(total, Decimal('50'))
        self.assertEqual(discount, Decimal('0'))
        self.assertEqual(len(purchases), 1)
        self.assertEqual(Decimal(purchases[0].total_price), Decimal('50'))


if __name__ == '__main__':
    unittest.main()