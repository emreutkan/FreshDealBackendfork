from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.services.restaurant_badge_services import get_restaurant_badges, add_restaurant_badge_point, VALID_BADGES

restaurant_badge_bp = Blueprint("restaurant_badge", __name__)

@restaurant_badge_bp.route("/restaurants/<int:restaurant_id>/badges", methods=["GET"])
def get_badges(restaurant_id):
    """
    Retrieve Restaurant Badges and Points
    This endpoint retrieves all badges and their points for a given restaurant.

    ---
    summary: Retrieve badges and points for a restaurant
    description: >
      Returns a JSON object with the restaurant ID and detailed badge points information,
      including both positive and negative badge counts.
    tags:
      - Restaurant Badge
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
        description: Unique identifier of the restaurant.
    responses:
      200:
        description: Badges retrieved successfully.
        schema:
          type: object
          properties:
            restaurant_id:
              type: integer
              description: The unique ID of the restaurant.
            badge_points:
              type: object
              properties:
                fresh:
                  type: integer
                  description: Points for fresh badge
                not_fresh:
                  type: integer
                  description: Points for not fresh badge
                fast_delivery:
                  type: integer
                  description: Points for fast delivery badge
                slow_delivery:
                  type: integer
                  description: Points for slow delivery badge
                customer_friendly:
                  type: integer
                  description: Points for customer friendly badge
                not_customer_friendly:
                  type: integer
                  description: Points for not customer friendly badge
        examples:
          application/json:
            restaurant_id: 1
            badge_points:
              fresh: 150
              not_fresh: 20
              fast_delivery: 200
              slow_delivery: 30
              customer_friendly: 180
              not_customer_friendly: 25
      500:
        description: An error occurred while retrieving badges.
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            error:
              type: string
    """
    try:
        badge_points = get_restaurant_badges(restaurant_id)
        return jsonify({
            "restaurant_id": restaurant_id,
            "badge_points": badge_points
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while retrieving badges",
            "error": str(e)
        }), 500