from . import db, Listing
from sqlalchemy import Integer, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum


class PurchaseStatus(str, PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

    @classmethod
    def active_statuses(cls):
        return [cls.PENDING, cls.ACCEPTED]

    def is_active(self):
        return self in self.active_statuses()


class Purchase(db.Model):
    __tablename__ = 'purchases'

    # Add indexes and table configurations
    __table_args__ = (
        db.Index('idx_purchase_user_status', 'user_id', 'status'),
        db.Index('idx_purchase_date', 'purchase_date'),
        db.Index('idx_purchase_restaurant', 'restaurant_id'),
        {'mysql_engine': 'InnoDB'}
    )

    # Columns
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(
        Integer,
        ForeignKey('restaurants.id'),  # <-- remove ondelete='CASCADE'
        nullable=False
    )

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
    restaurant = relationship('Restaurant', back_populates='purchases')
    restaurant_comment = relationship('RestaurantComment', uselist=False, back_populates='purchase')

    def __init__(self, **kwargs):
        super(Purchase, self).__init__(**kwargs)
        self.validate_delivery_info()

    # Properties
    @property
    def is_active(self):
        """Check if the purchase is active"""
        return self.status in PurchaseStatus.active_statuses()

    @property
    def formatted_total_price(self):
        """Return formatted price string"""
        return f"${float(self.total_price):.2f}"

    # Validation Methods
    def validate_delivery_info(self):
        """Validate delivery information consistency"""
        if self.is_delivery and not self.delivery_address:
            raise ValueError("Delivery address is required for delivery orders")

    def validate_status_transition(self, new_status):
        """Validate status transitions"""
        valid_transitions = {
            PurchaseStatus.PENDING: [PurchaseStatus.ACCEPTED, PurchaseStatus.REJECTED],
            PurchaseStatus.ACCEPTED: [PurchaseStatus.COMPLETED],
            PurchaseStatus.REJECTED: [],
            PurchaseStatus.COMPLETED: []
        }
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")

    def can_be_modified(self):
        """Check if the purchase can still be modified"""
        return self.status == PurchaseStatus.PENDING

    # Query Methods
    @classmethod
    def get_restaurant_purchases(cls, restaurant_id):
        """Get all purchases for a specific restaurant"""
        return cls.query \
            .filter(cls.restaurant_id == restaurant_id) \
            .order_by(cls.purchase_date.desc()) \
            .all()

    @classmethod
    def get_active_purchases_for_user(cls, user_id):
        """Get all active purchases for a user"""
        return cls.query.filter(
            db.and_(
                cls.user_id == user_id,
                cls.status.in_([PurchaseStatus.PENDING, PurchaseStatus.ACCEPTED])
            )
        ).order_by(cls.purchase_date.desc()).all()

    @classmethod
    def get_restaurant_active_purchases(cls, restaurant_id):
        """Get active purchases for a restaurant"""
        return cls.query.filter(
            db.and_(
                cls.restaurant_id == restaurant_id,
                cls.status.in_([PurchaseStatus.PENDING, PurchaseStatus.ACCEPTED])
            )
        ).order_by(cls.purchase_date.desc()).all()

    # Serialization Methods
    def to_dict(self, include_relations=False):
        """
        Enhanced dictionary representation with optional relationship inclusion
        """
        base_dict = {
            "purchase_id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "listing_title": self.listing.title if self.listing else None,
            "quantity": self.quantity,
            "total_price": str(self.total_price),
            "formatted_total_price": self.formatted_total_price,
            "purchase_date": self.purchase_date.isoformat(),
            "status": self.status.value,
            "is_active": self.is_active,
            "is_delivery": self.is_delivery,
            "delivery_address": self.delivery_address,
            "delivery_notes": self.delivery_notes,
            "completion_image_url": self.completion_image_url,
            "restaurant_id": self.restaurant_id,
        }

        if include_relations:
            base_dict.update({
                "listing": {
                    "id": self.listing.id,
                    "title": self.listing.title
                } if self.listing else None,
                "restaurant": {
                    "id": self.restaurant.id,
                    "name": self.restaurant.restaurantName
                } if self.restaurant else None,
                "user": {
                    "id": self.user.id,
                    "name": self.user.name,
                } if self.user else None
            })

        return base_dict

    def update_status(self, new_status):
        """
        Update the status of the purchase with validation
        """
        self.validate_status_transition(new_status)
        self.status = new_status
        return self