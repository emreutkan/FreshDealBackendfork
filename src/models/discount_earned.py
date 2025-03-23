from . import db
from sqlalchemy import Integer, DECIMAL, DateTime, func

class DiscountEarned(db.Model):
    __tablename__ = 'discountEarned'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    discount = db.Column(DECIMAL(10, 2), nullable=False)
    earned_at = db.Column(DateTime, nullable=False, default=func.now())