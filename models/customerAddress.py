from . import db
from sqlalchemy import Integer, String, DECIMAL, Boolean, CheckConstraint

class CustomerAddress(db.Model):
    __tablename__ = 'customerAddresses'
    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(String(80), nullable=False)
    longitude = db.Column(DECIMAL(9, 6), nullable=False)
    latitude = db.Column(DECIMAL(9, 6), nullable=False)
    street = db.Column(String(80), nullable=True)
    neighborhood = db.Column(String(80), nullable=True)
    district = db.Column(String(80), nullable=True)
    province = db.Column(String(80), nullable=True)
    country = db.Column(String(80), nullable=True)
    postalCode = db.Column(Integer, nullable=True)
    apartmentNo = db.Column(Integer, nullable=True)
    doorNo = db.Column(String(6), nullable=True)
    is_primary = db.Column(Boolean, nullable=False, default=False)
