# models/purchase_report.py
from src.models import db
from sqlalchemy import Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship


class PurchaseReport(db.Model):
    __tablename__ = 'purchase_reports'

    id = db.Column(Integer, primary_key=True, autoincrement=True)

    # The user who is reporting
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # The purchase being reported
    purchase_id = db.Column(Integer, ForeignKey('purchases.id', ondelete='CASCADE'), nullable=False)

    # Additional references for convenience (so we can quickly see the associated listing/restaurant)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=True)
    listing_id = db.Column(Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=True)

    # A user-uploaded image URL (or file path) describing what went wrong
    image_url = db.Column(String(2083), nullable=True)

    # A brief text explaining the reason for the report
    description = db.Column(String(1000), nullable=False)

    # Timestamp for when the report was created
    reported_at = db.Column(DateTime, nullable=False, default=func.now())

    # Relationships
    user = relationship('User', backref='purchase_reports')
    purchase = relationship('Purchase', backref='reports')
    restaurant = relationship('Restaurant', backref='purchase_reports')
    listing = relationship('Listing', backref='purchase_reports')
