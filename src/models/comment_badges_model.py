from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from . import db

class CommentBadge(db.Model):
    __tablename__ = 'comment_badges'

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    comment_id = db.Column(Integer, ForeignKey('restaurant_comments.id'), nullable=False)
    badge_name = db.Column(String(50), nullable=False)
    is_positive = db.Column(Boolean, nullable=False, default=True)

    comment = relationship("RestaurantComment", back_populates="badges")