from . import db
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

class UserCart(db.Model):
    __tablename__ = 'user_cart'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    count = db.Column(Integer, nullable=False, default=1)  # Quantity of the item in the cart
    added_at = db.Column(DateTime, nullable=False, default=func.now())  # Timestamp for when the item was added

    # Relationships
    user = relationship("User", backref="cart_items")
    listing = relationship("Listing", backref="cart_entries")
