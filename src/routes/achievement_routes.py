from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.achievement_service import AchievementService

achievement_bp = Blueprint("achievement", __name__)

@achievement_bp.route("/user/achievements", methods=["GET"])
@jwt_required()
def get_user_achievements():
    """
    Get all achievements earned by the authenticated user
    ---
    tags:
      - Achievements
    security:
      - BearerAuth: []
    responses:
      200:
        description: User achievements retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                achievements:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
                      badge_image_url:
                        type: string
                      earned_at:
                        type: string
                        format: date-time
                      achievement_type:
                        type: string
      500:
        description: An error occurred
    """
    try:
        user_id = get_jwt_identity()
        achievements = AchievementService.get_user_achievements(user_id)
        return jsonify({
            "achievements": achievements
        }), 200
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching achievements",
            "error": str(e)
        }), 500

@achievement_bp.route("/achievements", methods=["GET"])
@jwt_required()
def get_available_achievements():
    """
    Get all available achievements
    ---
    tags:
      - Achievements
    security:
      - BearerAuth: []
    responses:
      200:
        description: Available achievements retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                achievements:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
                      badge_image_url:
                        type: string
                      achievement_type:
                        type: string
                      threshold:
                        type: integer
      500:
        description: An error occurred
    """
    try:
        achievements = AchievementService.get_available_achievements()
        return jsonify({
            "achievements": achievements
        }), 200
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching achievements",
            "error": str(e)
        }), 500