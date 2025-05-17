from datetime import datetime, timezone
from . import db

class RestaurantPunishment(db.Model):
    __tablename__ = 'restaurant_punishments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    punishment_type = db.Column(db.String(20), nullable=False)  # PERMANENT or TEMPORARY
    duration_days = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_reverted = db.Column(db.Boolean, default=False, nullable=False)
    reverted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reverted_at = db.Column(db.DateTime, nullable=True)
    reversion_reason = db.Column(db.Text, nullable=True)

    # Relations
    creator = db.relationship('User', foreign_keys=[created_by], backref='issued_punishments')
    reverter = db.relationship('User', foreign_keys=[reverted_by], backref='reverted_punishments')


class RefundRecord(db.Model):
    __tablename__ = 'refund_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))