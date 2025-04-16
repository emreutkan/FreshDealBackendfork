from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.AI_services.comment_analysis_service import CommentAnalysisService
from src.models import User, Restaurant
import logging

# Configure logging
logger = logging.getLogger(__name__)

comment_analysis_bp = Blueprint('comment_analysis', __name__)


@comment_analysis_bp.route('/restaurants/<int:restaurant_id>/comment-analysis', methods=['GET'])
@jwt_required()
def analyze_restaurant_comments(restaurant_id):
    """
    Analyze comments for a specific restaurant from the last 3 months
    ---
    tags:
      - AI Services
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
        description: ID of the restaurant
    security:
      - BearerAuth: []
    responses:
      200:
        description: Comment analysis results
        content:
          application/json:
            schema:
              type: object
              properties:
                restaurant_id:
                  type: integer
                  description: ID of the restaurant
                restaurant_name:
                  type: string
                  description: Name of the restaurant
                comment_count:
                  type: integer
                  description: Number of comments analyzed
                analysis_date:
                  type: string
                  format: date-time
                  description: Date and time of the analysis
                good_aspects:
                  type: array
                  items:
                    type: string
                  description: Positive aspects mentioned in comments
                bad_aspects:
                  type: array
                  items:
                    type: string
                  description: Negative aspects mentioned in comments
      404:
        description: Restaurant not found
      500:
        description: Internal server error
    """
    try:
        logger.info(f"Comment analysis requested for restaurant ID: {restaurant_id}")
        user_id = get_jwt_identity()
        logger.info(f"Request from user ID: {user_id}")

        # Verify the restaurant exists
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            logger.warning(f"Restaurant with ID {restaurant_id} not found")
            return jsonify({"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}), 404

        # Initialize comment analyzer
        analyzer = CommentAnalysisService()

        # Analyze comments
        logger.info(f"Starting comment analysis for restaurant: {restaurant.restaurantName}")
        analysis_results = analyzer.analyze_comments(restaurant_id)

        # Check if there was an error
        if "error" in analysis_results:
            error_msg = analysis_results["error"]
            logger.error(f"Error in comment analysis: {error_msg}")

            # Provide a more user-friendly message
            if "400 Client Error" in error_msg:
                return jsonify({
                    "success": False,
                    "message": "Error connecting to the analysis service. Please try again later.",
                    "details": "There may be an issue with the API key or the service may be temporarily unavailable."
                }), 500
            else:
                return jsonify({
                    "success": False,
                    "message": error_msg
                }), 500

        logger.info(f"Comment analysis completed successfully for restaurant ID: {restaurant_id}")
        return jsonify(analysis_results), 200

    except Exception as e:
        logger.exception(f"Unexpected error in comment analysis endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error analyzing restaurant comments: {str(e)}"
        }), 500