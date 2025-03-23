from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from src.services.gamification_services import get_user_rankings

gamification_bp = Blueprint("gamification", __name__)


@gamification_bp.route("/user/rankings", methods=["GET"])
@jwt_required()
def get_user_rankings_route():
    """
    Get the user rankings based on total discounts earned.
    ---
    tags:
      - Rankings
    security:
      - BearerAuth: []
    responses:
      200:
        description: User rankings fetched successfully.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  rank:
                    type: integer
                  user_id:
                    type: integer
                  user_name:
                    type: string
                  total_discount:
                    type: number
                    format: float
      500:
        description: An error occurred.
    """
    try:
        return get_user_rankings()

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching user rankings",
            "error": str(e)
        }), 500
