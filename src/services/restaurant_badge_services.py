from src.models import db
from src.models.restaurant_badge_points_model import RestaurantBadgePoints

VALID_BADGES = ['fresh', 'fast_delivery', 'customer_friendly']


def add_restaurant_badge_point(restaurant_id, badge_name):
    """
    Add a badge point for a restaurant based on the badge type.

    Args:
        restaurant_id (int): ID of the restaurant.
        badge_name (str): Name of the badge ('fresh', 'fast_delivery', or 'customer_friendly').

    Raises:
        ValueError: If the badge_name is not valid.
    """
    if badge_name not in VALID_BADGES:
        raise ValueError(f"'{badge_name}' is not a valid badge name.")

    # Retrieve the existing badge record for the restaurant, if any.
    badge_record = RestaurantBadgePoints.query.filter_by(restaurantID=restaurant_id).first()

    if badge_record:
        if badge_name == 'fresh':
            badge_record.freshPoint += 1
        elif badge_name == 'fast_delivery':
            badge_record.fastDeliveryPoint += 1
        elif badge_name == 'customer_friendly':
            badge_record.customerFriendlyPoint += 1
        db.session.commit()
    else:
        # Create a new badge record with the appropriate badge initialized.
        badge_record = RestaurantBadgePoints(
            restaurantID=restaurant_id,
            freshPoint=1 if badge_name == 'fresh' else 0,
            fastDeliveryPoint=1 if badge_name == 'fast_delivery' else 0,
            customerFriendlyPoint=1 if badge_name == 'customer_friendly' else 0
        )
        db.session.add(badge_record)
        db.session.commit()


def get_restaurant_badges(restaurant_id):
    """
    Retrieve the list of badges awarded to a restaurant based on its badge points.

    Args:
        restaurant_id (int): ID of the restaurant.

    Returns:
        list: A list of badge names.
    """
    badge_record = RestaurantBadgePoints.query.filter_by(restaurantID=restaurant_id).first()
    if not badge_record:
        return []

    badges = []

    # Evaluate 'fresh' badge
    if badge_record.freshPoint > 100:
        badges.append('fresh')

    # Evaluate 'fast_delivery' badge
    if badge_record.fastDeliveryPoint > 100:
        badges.append('fast_delivery')

    # Evaluate 'customer_friendly' badge
    if badge_record.customerFriendlyPoint > 100:
        badges.append('customer_friendly')

    return badges
