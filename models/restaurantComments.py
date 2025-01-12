from . import db
from sqlalchemy import Integer, String, DECIMAL, Boolean, Float, ForeignKey
from sqlalchemy.orm import validates, relationship



class RestaurantComment(db.Model):
    __tablename__ = 'restaurant_comments'

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    purchase_id = db.Column(Integer, ForeignKey('purchases.id'), nullable=False, unique=True)  # Restrict one comment per purchase
    comment = db.Column(String(1000), nullable=False)
    rating = db.Column(DECIMAL(3, 2), nullable=False)  # Rating is mandatory
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    restaurant = relationship("Restaurant", back_populates="comments")  # Matches 'comments' in Restaurant
    user = relationship("User", back_populates="comments")  # Matches 'comments' in User
    purchase = relationship("Purchase", back_populates="restaurant_comment")  # Matches 'restaurant_comment' in Purchase