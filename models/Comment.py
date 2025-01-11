from . import db
from sqlalchemy import Integer, ForeignKey, String, DECIMAL, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = db.Column(Integer, ForeignKey('purchases.id', ondelete='CASCADE'), nullable=False, unique=True)
    comment_text = db.Column(Text, nullable=False)
    rating = db.Column(DECIMAL(3, 2), nullable=True)  # Optional, allows users to rate their purchase

    # Relationship
    purchase = relationship('Purchase', back_populates='comment')  # Use correct class name
