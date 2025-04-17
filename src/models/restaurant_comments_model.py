from sqlalchemy import Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class RestaurantComment(db.Model):
    __tablename__ = 'restaurant_comments'

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    purchase_id = db.Column(Integer, ForeignKey('purchases.id'), nullable=False, unique=True)
    comment = db.Column(String(1000), nullable=False)
    rating = db.Column(DECIMAL(3, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    restaurant = relationship("Restaurant", back_populates="comments")
    user = relationship("User", back_populates="comments")
    purchase = relationship("Purchase", back_populates="restaurant_comment")
    badges = relationship("CommentBadge", back_populates="comment", cascade="all, delete-orphan")