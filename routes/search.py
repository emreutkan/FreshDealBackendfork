from flask import Blueprint, request, jsonify
from models import Restaurant, Listing

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    try:
        # Get search parameters
        search_type = request.args.get("type")  # 'restaurant' or 'listing'
        query = request.args.get("query", "").strip()
        restaurant_id = request.args.get("restaurant_id", type=int)

        if not query:
            return jsonify({"success": False, "message": "Query parameter is required"}), 400

        if search_type == "restaurant":
            # Search restaurants by name
            results = Restaurant.query.filter(Restaurant.restaurantName.ilike(f"%{query}%")).all()
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
            return jsonify({"success": True, "type": "restaurant", "results": data}), 200

        elif search_type == "listing":
            if not restaurant_id:
                return jsonify({"success": False, "message": "Restaurant ID is required for listing search"}), 400

            # Search listings by title within a specific restaurant
            results = Listing.query.filter(
                Listing.restaurant_id == restaurant_id, Listing.title.ilike(f"%{query}%")
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
            return jsonify({"success": True, "type": "listing", "results": data}), 200

        else:
            return jsonify({"success": False, "message": "Invalid search type. Use 'restaurant' or 'listing'"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while performing search", "error": str(e)}), 500
