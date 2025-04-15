from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import User
from src.services.analytics_service import RestaurantAnalyticsService
from functools import wraps

analytics_bp = Blueprint('analytics', __name__)

def owner_required(f):
    """Decorator to check if the user has owner role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'owner':
            return jsonify({
                "success": False,
                "message": "This endpoint is only available for restaurant owners"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@owner_required
def get_owner_analytics():
    """
    Get analytics dashboard data for restaurant owner
    ---
    tags:
      - Analytics
    security:
      - BearerAuth: []
    responses:
      200:
        description: Analytics dashboard data
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                data:
                  type: object
                  properties:
                    monthly_stats:
                      type: object
                      properties:
                        total_products_sold:
                          type: integer
                        total_revenue:
                          type: string
                        period:
                          type: string
                    regional_distribution:
                      type: object
                    restaurant_ratings:
                      type: object
                      additionalProperties:
                        type: object
                        properties:
                          id:
                            type: integer
                          average_rating:
                            type: number
                          total_ratings:
                            type: integer
                          recent_comments:
                            type: array
                            items:
                              type: object
                              properties:
                                user_name:
                                  type: string
                                rating:
                                  type: number
                                comment:
                                  type: string
                                timestamp:
                                  type: string
      403:
        description: User is not a restaurant owner
      404:
        description: No restaurants found for this owner
    """
    owner_id = get_jwt_identity()
    response, status_code = RestaurantAnalyticsService.get_owner_analytics(owner_id)
    return jsonify(response), status_code