from . import db
from sqlalchemy import Integer, UniqueConstraint

class UserFavorites(db.Model):
    __tablename__ = 'user_favorites'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(Integer, db.ForeignKey('restaurants.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'restaurant_id', name='unique_user_restaurant'),
    )
