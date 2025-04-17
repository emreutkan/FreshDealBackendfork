from src.models import db
from src.models.restaurant_badge_points_model import RestaurantBadgePoints

VALID_BADGES = [
    'fresh', 'fast_delivery', 'customer_friendly',
    'not_fresh', 'slow_delivery', 'not_customer_friendly'
]

BADGE_PAIRS = {
    'fresh': 'not_fresh',
    'fast_delivery': 'slow_delivery',
    'customer_friendly': 'not_customer_friendly',
    'not_fresh': 'fresh',
    'slow_delivery': 'fast_delivery',
    'not_customer_friendly': 'customer_friendly'
}

def add_restaurant_badge_point(restaurant_id, badge_name):
    if badge_name not in VALID_BADGES:
        raise ValueError(f"'{badge_name}' is not a valid badge name.")

    badge_record = RestaurantBadgePoints.query.filter_by(restaurantID=restaurant_id).first()

    if not badge_record:
        badge_record = RestaurantBadgePoints(restaurantID=restaurant_id)
        db.session.add(badge_record)

    if badge_name == 'fresh':
        badge_record.freshPoint += 1
    elif badge_name == 'not_fresh':
        badge_record.notFreshPoint += 1
    elif badge_name == 'fast_delivery':
        badge_record.fastDeliveryPoint += 1
    elif badge_name == 'slow_delivery':
        badge_record.slowDeliveryPoint += 1
    elif badge_name == 'customer_friendly':
        badge_record.customerFriendlyPoint += 1
    elif badge_name == 'not_customer_friendly':
        badge_record.notCustomerFriendlyPoint += 1

    db.session.commit()

def get_restaurant_badges(restaurant_id):
    badge_record = RestaurantBadgePoints.query.filter_by(restaurantID=restaurant_id).first()
    if not badge_record:
        return []

    badges = []

    fresh_score = badge_record.freshPoint - badge_record.notFreshPoint
    delivery_score = badge_record.fastDeliveryPoint - badge_record.slowDeliveryPoint
    friendly_score = badge_record.customerFriendlyPoint - badge_record.notCustomerFriendlyPoint

    if fresh_score > 100:
        badges.append('fresh')
    if delivery_score > 100:
        badges.append('fast_delivery')
    if friendly_score > 100:
        badges.append('customer_friendly')

    return badges