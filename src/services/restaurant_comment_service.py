from src.models import db, Restaurant, RestaurantComment, Purchase
from src.services.restaurant_badge_services import add_restaurant_badge_point

def add_comment_service(restaurant_id, user_id, data):
    """
    Add a comment (and rating) for a restaurant.

    Expects data containing:
      - comment: the comment text (required)
      - rating: a number between 0 and 5 (required)
      - purchase_id: the purchase identifier (required)
      - badge_names: (optional) an array of badge types to award restaurant badge points
        Valid badge types might include: 'fresh', 'fast_delivery', 'customer_friendly'
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404

    comment_text = data.get("comment")
    rating = data.get("rating")
    purchase_id = data.get("purchase_id")
    badge_names = data.get("badge_names")  # Optional field for sending multiple badge points

    if not comment_text:
        return {"success": False, "message": "Comment text is required"}, 400
    if rating is None:
        return {"success": False, "message": "Rating is required"}, 400
    if not purchase_id:
        return {"success": False, "message": "Purchase ID is required"}, 400

    purchase = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()
    if not purchase:
        return {"success": False, "message": "No valid purchase found for the user"}, 403

    listing = purchase.listing
    if not listing or listing.restaurant_id != restaurant_id:
        return {"success": False, "message": "Purchase does not correspond to this restaurant"}, 403

    if RestaurantComment.query.filter_by(purchase_id=purchase_id).first():
        return {"success": False, "message": "You have already commented on this purchase"}, 403

    try:
        rating = float(rating)
        if not (0 <= rating <= 5):
            return {"success": False, "message": "Rating must be between 0 and 5"}, 400
    except ValueError:
        return {"success": False, "message": "Invalid rating format"}, 400

    new_comment = RestaurantComment(
        restaurant_id=restaurant_id,
        user_id=user_id,
        purchase_id=purchase_id,
        comment=comment_text,
        rating=rating
    )
    db.session.add(new_comment)
    restaurant.update_rating(rating)
    db.session.commit()

    # Award badge points if "badge_names" is provided.
    if badge_names:
        # Ensure we have a list; if not, convert a single badge to a list.
        if not isinstance(badge_names, list):
            badge_names = [badge_names]
        for badge_name in badge_names:
            try:
                add_restaurant_badge_point(restaurant_id, badge_name)
            except Exception as e:
                # Log the error but don't block the comment submission.
                logging.error(f"Error adding restaurant badge point for badge '{badge_name}': {str(e)}")
    return {"success": True, "message": "Comment added successfully"}, 201
