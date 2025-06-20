import unittest
from decimal import Decimal
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, Restaurant, Listing, User, Purchase
from src.models.purchase_model import PurchaseStatus

class TestPurchaseModel(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.owner = User(
            name="Owner",
            email="owner@test.com",
            phone_number="+1234567890",
            password=generate_password_hash("password"),
            role="owner",
            email_verified=True
        )
        db.session.add(self.owner)
        db.session.commit()

        self.restaurant = Restaurant(
            owner_id=self.owner.id,
            restaurantName="Test Restaurant",
            restaurantDescription="Desc",
            longitude=0.0,
            latitude=0.0,
            category="Test",
            workingDays="Monday,Tuesday",
            workingHoursStart="09:00",
            workingHoursEnd="18:00",
            pickup=True,
            delivery=True
        )
        db.session.add(self.restaurant)
        db.session.commit()

        self.listing = Listing.create(
            restaurant_id=self.restaurant.id,
            title="Listing",
            description="Desc",
            image_url="http://example.com/img.jpg",
            count=5,
            original_price=Decimal('10.00'),
            pick_up_price=Decimal('9.00'),
            delivery_price=Decimal('12.00'),
            consume_within=6
        )
        db.session.add(self.listing)
        db.session.commit()

        self.purchase = Purchase(
            user_id=self.owner.id,
            listing_id=self.listing.id,
            restaurant_id=self.restaurant.id,
            quantity=2,
            total_price=Decimal('20.00'),
            status=PurchaseStatus.PENDING,
            is_delivery=False
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_formatted_total_price(self):
        self.assertEqual(self.purchase.formatted_total_price, "$20.00")

    def test_validate_status_transition_invalid(self):
        with self.assertRaises(ValueError):
            self.purchase.validate_status_transition(PurchaseStatus.COMPLETED)

    def test_update_status_success(self):
        result = self.purchase.update_status(PurchaseStatus.ACCEPTED)
        self.assertIs(result, self.purchase)
        self.assertEqual(self.purchase.status, PurchaseStatus.ACCEPTED)

    def test_update_status_invalid(self):
        with self.assertRaises(ValueError):
            self.purchase.update_status(PurchaseStatus.COMPLETED)

if __name__ == '__main__':
    unittest.main()
