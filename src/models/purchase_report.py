# models/purchase_report.py
from src.models import db
from sqlalchemy import Integer, ForeignKey, String, DateTime, func, Enum
from sqlalchemy.orm import relationship
import enum


class ReportStatus(enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    INACTIVE = "inactive"


class PurchaseReport(db.Model):
    __tablename__ = 'purchase_reports'

    id = db.Column(Integer, primary_key=True, autoincrement=True)

    # The user who is reporting
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)

    # The purchase being reported
    purchase_id = db.Column(Integer, ForeignKey('purchases.id'), nullable=False)

    # Additional references for convenience (so we can quickly see the associated listing/restaurant)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id'), nullable=True)
    listing_id = db.Column(Integer, ForeignKey('listings.id'), nullable=True)

    # A user-uploaded image URL (or file path) describing what went wrong
    image_url = db.Column(String(2083), nullable=True)

    # A brief text explaining the reason for the report
    description = db.Column(String(1000), nullable=False)

    # Status of the report
    status = db.Column(Enum(ReportStatus), default=ReportStatus.ACTIVE, nullable=False)

    # Timestamp for when the report was created
    reported_at = db.Column(DateTime, nullable=False, default=func.now())

    # Timestamp for when the report was resolved
    resolved_at = db.Column(DateTime, nullable=True)

    # Support user who resolved the report
    resolved_by = db.Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationship to punishment (one report can have one punishment)
    punishment_id = db.Column(Integer, ForeignKey('restaurant_punishments.id'), nullable=True)
    punishment = relationship('RestaurantPunishment', backref='report')

    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='purchase_reports')
    resolver = relationship('User', foreign_keys=[resolved_by], backref='resolved_reports')
    purchase = relationship('Purchase', backref='reports')
    restaurant = relationship('Restaurant', backref='purchase_reports')
    listing = relationship('Listing', backref='purchase_reports')