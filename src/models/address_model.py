from . import db
from sqlalchemy import Integer, String, DECIMAL, Boolean

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
    postalCode = db.Column(String(10), nullable=True)  # Changed from Integer to String(10)
    apartmentNo = db.Column(Integer, nullable=True)
    doorNo = db.Column(String(6), nullable=True)
    is_primary = db.Column(Boolean, nullable=False, default=False)


    def to_dict(self):
        return {
            "id": str(self.id),  # Ensure id is a string if frontend expects it
            "user_id": self.user_id,
            "title": self.title,
            "longitude": float(self.longitude),
            "latitude": float(self.latitude),
            "street": self.street,
            "neighborhood": self.neighborhood,
            "district": self.district,
            "province": self.province,
            "country": self.country,
            "postalCode": self.postalCode,
            "apartmentNo": self.apartmentNo,
            "doorNo": self.doorNo,
            "is_primary": self.is_primary
        }