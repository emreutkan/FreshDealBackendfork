from . import db, Listing
from sqlalchemy import Integer, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from enum import Enum


class PurchaseStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'),
                              nullable=False)  # Added for query optimization
    quantity = db.Column(Integer, nullable=False, default=1)
    total_price = db.Column(DECIMAL(10, 2), nullable=False)
    purchase_date = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(PurchaseStatus), default=PurchaseStatus.PENDING, nullable=False)

    is_delivery = db.Column(db.Boolean, default=False, nullable=False)
    delivery_address = db.Column(db.String(500))
    completion_image_url = db.Column(db.String(255))
    delivery_notes = db.Column(db.String(500))

    # Relationships
    user = relationship('User', back_populates='purchases')
    listing = relationship('Listing', back_populates='purchases')
    restaurant = relationship('Restaurant', back_populates='purchases')  # Add this relationship
    restaurant_comment = relationship('RestaurantComment', uselist=False, back_populates='purchase')

    @classmethod
    def get_restaurant_purchases(cls, restaurant_id):
        """
        Get all purchases for a specific restaurant through listings
        """
        return cls.query \
            .join(Listing) \
            .filter(Listing.restaurant_id == restaurant_id) \
            .order_by(cls.purchase_date.desc()) \
            .all()

    def to_dict(self):
        """
        Convert purchase to dictionary for API response
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "listing_title": self.listing.title if self.listing else None,
            "quantity": self.quantity,
            "total_price": str(self.total_price),
            "purchase_date": self.purchase_date.isoformat(),
            "status": self.status.value,
            "is_delivery": self.is_delivery,
            "delivery_address": self.delivery_address,
            "delivery_notes": self.delivery_notes,
            "completion_image_url": self.completion_image_url
        }