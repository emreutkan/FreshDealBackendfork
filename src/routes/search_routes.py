# routes/search_routes.py

from flask import Blueprint, request, jsonify
from src.services.search_service import search_restaurants, search_listings

search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["GET"])
def search():
    """
    Search for restaurants or listings.

    This endpoint searches for restaurants by name or listings by title within a specified restaurant.

    ---
    tags:
      - Search
    parameters:
      - in: query
        name: type
        required: true
        schema:
          type: string
          enum: [restaurant, listing]
        description: 'Search type: "restaurant" or "listing".'
      - in: query
        name: query
        required: true
        schema:
          type: string
        description: The search query.
      - in: query
        name: restaurant_id
        required: false
        schema:
          type: integer
        description: Required for search type "listing".
    Responses:
      200:
        description: Search results returned successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                type:
                  type: string
                  description: The type of results returned.
                results:
                  type: array
                  items:
                    type: object
      400:
        description: Invalid or missing parameters.
      500:
        description: An error occurred during the search.
    """
    try:
        # Get query parameters
        search_type = request.args.get("type")
        query = request.args.get("query", "").strip()
        restaurant_id = request.args.get("restaurant_id", type=int)

        if not query:
            return jsonify({"success": False, "message": "Query parameter is required"}), 400

        if search_type == "restaurant":
            data = search_restaurants(query)
            return jsonify({"success": True, "type": "restaurant", "results": data}), 200

        elif search_type == "listing":
            if not restaurant_id:
                return jsonify({"success": False, "message": "Restaurant ID is required for listing search"}), 400
            data = search_listings(query, restaurant_id)
            return jsonify({"success": True, "type": "listing", "results": data}), 200

        else:
            return jsonify({"success": False, "message": "Invalid search type. Use 'restaurant' or 'listing'"}), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while performing search",
            "error": str(e)
        }), 500
