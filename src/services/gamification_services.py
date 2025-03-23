from flask import jsonify
from src.models import db, DiscountEarned, User, Purchase, Listing
from sqlalchemy import func
from datetime import datetime

def add_discount_point(purchase_id):
    purchase = Purchase.query.filter_by(id=purchase_id).first()
    user_id = purchase.user_id

    listing = Listing.query.filter_by(id=purchase.listing_id)
    discount = (purchase.quantity * float(listing.original_price)) - float(purchase.total_price)

    new_discount_point = DiscountEarned(
        user_id=user_id,
        discount=discount,
        earned_at=datetime.now()
    )

    db.session.add(new_discount_point)
    db.session.commit()


def get_user_rankings():
    results = db.session.query(
                DiscountEarned.user_id.label('user_id'),
                User.name.label('user_name'),
                func.sum(DiscountEarned.discount).label('total_discount')
            ) \
            .join(User, User.id == DiscountEarned.user_id) \
            .group_by(DiscountEarned.user_id) \
            .order_by(func.sum(DiscountEarned.discount).desc()) \
            .all()


    user_rankings = []
    rank = 1
    for user_id, user_name, total_discount in results:
        if total_discount is None:
            total_discount = 0.0
        else:
            total_discount = float(total_discount)

        user_rankings.append({
            'rank': rank,
            'user_id': user_id,
            'user_name': user_name,
            'total_discount': float(total_discount)
        })
        rank += 1

    return jsonify(user_rankings)
