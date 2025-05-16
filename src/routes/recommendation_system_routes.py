from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.services.recommendation_system_service import RecommendationSystemService, \
    RestaurantRecommendationSystemService
from src.models import Listing
import json
import traceback
import sys
import pandas as pd
from sklearn.neighbors import NearestNeighbors

recommendation_bp = Blueprint('recommendations', __name__)


@recommendation_bp.route('/api/recommendations/<int:listing_id>', methods=['GET'])
@jwt_required()
@swag_from({
    "tags": ["Recommendations"],
    "summary": "Get recommendations for a specific listing",
    "description": (
            "Retrieves personalized recommendations for a given listing based on purchase patterns "
            "using a KNN-based collaborative filtering approach. The recommendations are sorted "
            "by similarity score."
    ),
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "listing_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the listing to get recommendations for",
            "example": 51
        }
    ],
    "responses": {
        "200": {
            "description": "Recommendations retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": True},
                            "data": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "example": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
                            }
                        }
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized - Missing or invalid authorization token",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "msg": {"type": "string", "example": "Missing Authorization Header"}
                        }
                    }
                }
            }
        },
        "404": {
            "description": "Listing not found or no recommendations available",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "Listing not found"}
                        }
                    }
                }
            }
        },
        "500": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "Error getting recommendations"}
                        }
                    }
                }
            }
        }
    }
})
def get_recommendations_for_listing(listing_id):
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args)
        }
        print(json.dumps({"request": request_log}, indent=2))

        # Get recommendations
        response, status = RecommendationSystemService.get_recommendations_for_listing(listing_id)

        # If it fails with the initialization error, create a fallback response
        if status == 404 and response.get("message") == "Could not initialize recommendation model":
            # Get the listing and return its listing ID
            listing = Listing.query.get(listing_id)
            if listing:
                response = {
                    "success": True,
                    "data": [listing_id]
                }
                return jsonify(response), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Could not find listing"
                }), 404

        print(json.dumps({"response": response, "status": status}, indent=2))
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while fetching recommendations",
            "error": str(e)
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@recommendation_bp.route('/api/recommendations/users', methods=['GET'])
@jwt_required()
@swag_from({
    "tags": ["Recommendations"],
    "summary": "Get restaurant recommendations for the authenticated user",
    "description": (
            "Retrieves personalized restaurant recommendations for the authenticated user based on "
            "their purchase history using a KNN-based approach. The recommendations are sorted "
            "by similarity score. User is identified by the JWT token."
    ),
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Recommendations retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": True},
                            "data": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "example": [42, 1, 234, 54, 76, 12, 89, 23, 45, 67]
                            }
                        }
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized - Missing or invalid authorization token",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "msg": {"type": "string", "example": "Missing Authorization Header"}
                        }
                    }
                }
            }
        },
        "404": {
            "description": "User not found or no purchase history available",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "No purchase history found for this user"}
                        }
                    }
                }
            }
        },
        "500": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "Error getting recommendations"}
                        }
                    }
                }
            }
        }
    }
})
def get_recommendations_for_current_user():
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args)
        }
        print(json.dumps({"request": request_log}, indent=2))

        # Get the user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get recommendations using the user ID from the token
        response, status = RestaurantRecommendationSystemService.get_recommendations_by_user(current_user_id)

        print(json.dumps({"response": response, "status": status}, indent=2))
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while fetching restaurant recommendations",
            "error": str(e)
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


# Keep the old endpoint for backward compatibility but mark it as deprecated
@recommendation_bp.route('/api/recommendations/users/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from({
    "tags": ["Recommendations"],
    "summary": "Get restaurant recommendations for a specific user (DEPRECATED)",
    "description": (
            "DEPRECATED: Use '/api/recommendations/users' endpoint instead.\n\n"
            "Retrieves personalized restaurant recommendations for a given user based on "
            "a user's purchase history using a KNN-based approach. The recommendations are sorted "
            "by similarity score."
    ),
    "deprecated": True,
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the user to get recommendations for",
            "example": 51
        }
    ],
    "responses": {
        "200": {
            "description": "Recommendations retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": True},
                            "data": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "example": [42, 1, 234, 54, 76, 12, 89, 23, 45, 67]
                            }
                        }
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized - Missing or invalid authorization token",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "msg": {"type": "string", "example": "Missing Authorization Header"}
                        }
                    }
                }
            }
        },
        "404": {
            "description": "User not found or no purchase history available",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "No purchase history found for this user"}
                        }
                    }
                }
            }
        },
        "500": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "message": {"type": "string", "example": "Error getting recommendations"}
                        }
                    }
                }
            }
        }
    }
})
def get_recommendations_for_user(user_id):
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args)
        }
        print(json.dumps({"request": request_log}, indent=2))

        # Get recommendations
        response, status = RestaurantRecommendationSystemService.get_recommendations_by_user(user_id)

        print(json.dumps({"response": response, "status": status}, indent=2))
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while fetching restaurant recommendations",
            "error": str(e)
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500