from . import db
from sqlalchemy import Integer, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id = db.Column(Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(Integer, nullable=False, default=1)
    total_price = db.Column(DECIMAL(10, 2), nullable=False)  # Derived from listing price * quantity
    purchase_date = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='purchases')
    listing = relationship('Listing', back_populates='purchases')
    restaurant_comment = relationship('RestaurantComment', uselist=False, back_populates='purchase')
