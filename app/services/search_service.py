# services/search_service.py

from app.models import Restaurant, Listing


def search_restaurants(query):
    """
    Search for restaurants whose name matches the query (case-insensitive).
    Returns a list of matching restaurants.
    """
    results = Restaurant.query.filter(
        Restaurant.restaurantName.ilike(f"%{query}%")
    ).all()

    data = [
        {
            "id": restaurant.id,
            "name": restaurant.restaurantName,
            "description": restaurant.restaurantDescription,
            "image_url": restaurant.image_url,
            "rating": float(restaurant.rating) if restaurant.rating else None,
            "category": restaurant.category,
        }
        for restaurant in results
    ]
    return data


def search_listings(query, restaurant_id):
    """
    Search for listings (within a specific restaurant) whose title matches the query.
    Returns a list of matching listings.
    """
    results = Listing.query.filter(
        Listing.restaurant_id == restaurant_id,
        Listing.title.ilike(f"%{query}%")
    ).all()

    data = [
        {
            "id": listing.id,
            "restaurant_id": listing.restaurant_id,
            "title": listing.title,
            "description": listing.description,
            "image_url": listing.image_url,
            "price": float(listing.price),
            "count": listing.count,
        }
        for listing in results
    ]
    return data
