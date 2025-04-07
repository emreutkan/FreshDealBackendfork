from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.services.restaurant_badge_services import get_restaurant_badges, add_restaurant_badge_point

restaurant_badge_bp = Blueprint("restaurant_badge", __name__)

@restaurant_badge_bp.route("/restaurants/<int:restaurant_id>/badges", methods=["GET"])
def get_badges(restaurant_id):
    """
    Retrieve Restaurant Badges
    This endpoint retrieves all badges for a given restaurant based on its accumulated badge points.

    ---
    summary: Retrieve badges for a restaurant
    description: >
      Returns a JSON object with the restaurant ID and a list of badge names awarded to the specified restaurant.
      Badge determination is based on the restaurant's accumulated points thresholds.
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
            badges:
              type: array
              items:
                type: string
              description: List of badges awarded to the restaurant.
        examples:
          application/json:
            restaurant_id: 1
            badges:
              - fresh
              - fast_delivery
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
        badges = get_restaurant_badges(restaurant_id)
        return jsonify({"restaurant_id": restaurant_id, "badges": badges}), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while retrieving badges",
            "error": str(e)
        }), 500

#
# @restaurant_badge_bp.route("/restaurants/<int:restaurant_id>/badges", methods=["POST"])
# @jwt_required()
# def add_badge(restaurant_id):
#     """
#     Award a Badge Point to a Restaurant
#     This endpoint awards a badge point to the specified restaurant based on the provided badge type.
#
#     ---
#     summary: Award a badge point to a restaurant
#     description: >
#       Awards a badge point to the restaurant specified by the restaurant_id.
#       The request body must include a valid badge_name. Valid values are:
#         - fresh
#         - fast_delivery
#         - customer_friendly
#       On success, the endpoint returns a confirmation message.
#     tags:
#       - Restaurant Badge
#     security:
#       - BearerAuth: []
#     parameters:
#       - name: restaurant_id
#         in: path
#         type: integer
#         required: true
#         description: Unique identifier of the restaurant.
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             required:
#               - badge_name
#             properties:
#               badge_name:
#                 type: string
#                 enum: [fresh, fast_delivery, customer_friendly]
#                 description: The type of badge to award.
#           examples:
#             AwardBadge:
#               summary: Award a "fresh" badge point
#               value:
#                 badge_name: fresh
#     responses:
#       200:
#         description: Badge point awarded successfully.
#         schema:
#           type: object
#           properties:
#             success:
#               type: boolean
#               description: Indicator of successful operation.
#             message:
#               type: string
#               description: Success message.
#         examples:
#           application/json:
#             success: true
#             message: "Badge point added successfully"
#       400:
#         description: Missing or invalid badge_name.
#         schema:
#           type: object
#           properties:
#             success:
#               type: boolean
#             message:
#               type: string
#         examples:
#           application/json:
#             success: false
#             message: "badge_name is required"
#       401:
#         description: Unauthorized access.
#       500:
#         description: An error occurred while awarding the badge point.
#         schema:
#           type: object
#           properties:
#             success:
#               type: boolean
#             message:
#               type: string
#             error:
#               type: string
#     """
#     try:
#         data = request.get_json()
#         badge_name = data.get("badge_name")
#         if not badge_name:
#             return jsonify({"success": False, "message": "badge_name is required"}), 400
#
#         add_restaurant_badge_point(restaurant_id, badge_name)
#         return jsonify({"success": True, "message": "Badge point added successfully"}), 200
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "message": "An error occurred while awarding badge point",
#             "error": str(e)
#         }), 500
