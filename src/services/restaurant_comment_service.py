from src.models import db, Restaurant, RestaurantComment, Purchase, CommentBadge
from src.services.restaurant_badge_services import add_restaurant_badge_point, VALID_BADGES

def add_comment_service(restaurant_id, user_id, data):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404

    comment_text = data.get("comment")
    rating = data.get("rating")
    purchase_id = data.get("purchase_id")
    badge_names = data.get("badge_names", [])

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

    if badge_names:
        if not isinstance(badge_names, list):
            badge_names = [badge_names]

        for badge_name in badge_names:
            if badge_name in VALID_BADGES:
                try:
                    add_restaurant_badge_point(restaurant_id, badge_name)
                    is_positive = not badge_name.startswith('not_') and not badge_name.startswith('slow_')
                    comment_badge = CommentBadge(
                        comment=new_comment,
                        badge_name=badge_name,
                        is_positive=is_positive
                    )
                    db.session.add(comment_badge)
                except Exception as e:
                    print(f"Error adding restaurant badge point for badge '{badge_name}': {str(e)}")

    db.session.commit()
    return {"success": True, "message": "Comment added successfully"}, 201