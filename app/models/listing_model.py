from sqlalchemy.orm import relationship

from . import db
from sqlalchemy import Integer, String, ForeignKey, DECIMAL

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(String(255), nullable=False)
    description = db.Column(String(1000), nullable=True)
    image_url = db.Column(String(2083), nullable=True)  # URL for the image
    price = db.Column(DECIMAL(10, 2), nullable=False)
    count = db.Column(Integer, nullable=False, default=1)  # Default count set to 1

    purchases = relationship('Purchase', back_populates='listing')  # Ensure correct back_populates match
