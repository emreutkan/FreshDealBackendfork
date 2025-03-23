from src.services.notification_service import NotificationService
from src.models import User, CustomerAddress, Restaurant
from sqlalchemy import and_
import math
from src.models import db
import logging

logger = logging.getLogger(__name__)


def notify_users_about_new_restaurant(restaurant_id: int, max_distance_km: float = 5.0):
    """
    Notify users about a new restaurant based on their primary address proximity.

    Args:
        restaurant_id (int): The ID of the newly added restaurant
        max_distance_km (float): Maximum distance in kilometers to consider a user as "nearby"

    Returns:
        int: Number of users notified
    """
    try:
        # Get the restaurant info
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            logger.error(f"Restaurant with ID {restaurant_id} not found")
            return 0

        restaurant_lat = restaurant.latitude
        restaurant_lng = restaurant.longitude
        restaurant_name = restaurant.restaurantName

        logger.info(f"Finding users near new restaurant: {restaurant_name} (ID: {restaurant_id})")

        # Find users with primary addresses
        primary_addresses = db.session.query(CustomerAddress, User).join(
            User,
            CustomerAddress.user_id == User.id
        ).filter(
            CustomerAddress.is_primary == True
        ).all()

        logger.info(f"Found {len(primary_addresses)} users with primary addresses")

        notified_count = 0

        # Check each user's distance from the restaurant
        for address, user in primary_addresses:
            # Calculate distance between restaurant and user address
            distance = calculate_distance(
                restaurant_lat, restaurant_lng,
                address.latitude, address.longitude
            )

            # If user is nearby, send notification
            if distance <= max_distance_km:
                # Send notification to user
                success = NotificationService.send_notification_to_user(
                    user_id=user.id,
                    title="New Restaurant Opened Nearby!",
                    body=f"{restaurant_name} has just opened near your location. Check it out!",
                    data={
                        "type": "new_restaurant",
                        "restaurant_id": restaurant.id,
                        "screen": "RestaurantDetailScreen"
                    }
                )

                if success:
                    notified_count += 1
                    logger.info(f"Notified user {user.id} about new restaurant {restaurant_id}")
                else:
                    logger.warning(f"Failed to notify user {user.id} about new restaurant {restaurant_id}")

        logger.info(f"Notified {notified_count} users about new restaurant {restaurant_name}")
        return notified_count

    except Exception as e:
        logger.error(f"Error notifying users about new restaurant: {str(e)}")
        return 0


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point

    Returns:
        float: Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Earth radius in kilometers
    radius = 6371

    # Calculate distance
    distance = radius * c
    return distance