import unittest
from decimal import Decimal
from datetime import datetime, timedelta, UTC
from flask import Flask
from werkzeug.security import generate_password_hash
from src.models import db, Restaurant, Listing, User

class TestListingModel(unittest.TestCase):
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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def create_listing(self, **kwargs):
        params = dict(
            restaurant_id=self.restaurant.id,
            title="Listing",
            description="Desc",
            image_url="http://example.com/img.jpg",
            count=5,
            original_price=Decimal('10.00'),
            pick_up_price=Decimal('9.00'),
            delivery_price=Decimal('12.00'),
            consume_within_type="HOURS",
            consume_within=6
        )
        params.update(kwargs)
        return Listing.create(**params)

    def test_create_listing_success(self):
        listing = self.create_listing()
        self.assertEqual(listing.restaurant_id, self.restaurant.id)
        self.assertEqual(listing.consume_within_type, 'HOURS')
        self.assertEqual(listing.update_count, 0)
        self.assertTrue(listing.expires_at > datetime.now(UTC))
        self.assertTrue(listing.available_for_pickup)
        self.assertTrue(listing.available_for_delivery)

    def test_create_listing_invalid_consume_within(self):
        with self.assertRaises(ValueError):
            self.create_listing(consume_within=2)

    def test_decrease_stock(self):
        listing = self.create_listing(count=4)
        db.session.add(listing)
        db.session.commit()
        result = listing.decrease_stock(3)
        self.assertTrue(result)
        self.assertEqual(listing.count, 1)
        result = listing.decrease_stock(2)
        self.assertFalse(result)
        self.assertEqual(listing.count, 1)

    def test_is_expired(self):
        listing = self.create_listing()
        listing.expires_at = datetime.now(UTC) - timedelta(hours=1)
        self.assertTrue(listing.is_expired())

    def test_delete_listing(self):
        listing = self.create_listing()
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id
        success, _ = Listing.delete_listing(listing_id)
        self.assertTrue(success)
        self.assertIsNone(Listing.query.get(listing_id))

if __name__ == '__main__':
    unittest.main()
