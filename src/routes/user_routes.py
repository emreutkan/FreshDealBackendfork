import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.services.purchase_service import get_user_active_orders_service
from src.services.user_services import (
    fetch_user_data,
    change_password,
    change_username,
    change_email,
    add_favorite,
    remove_favorite,
    get_favorites
)

user_bp = Blueprint("user", __name__)

def is_valid_email(email):
    """
    Validates an email address using a regex pattern.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# ----------------------------
# User Resource
# ----------------------------

@user_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    """
    Get the authenticated user's information and associated addresses.
    ---
    tags:
      - User
    security:
      - BearerAuth: []
    responses:
      200:
        description: User data fetched successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                user_data:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    email:
                      type: string
                    phone_number:
                      type: string
                    role:
                      type: string
                    email_verified:
                      type: boolean
                user_address_list:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      longitude:
                        type: number
                        format: float
                      latitude:
                        type: number
                        format: float
                      street:
                        type: string
                      neighborhood:
                        type: string
                      district:
                        type: string
                      province:
                        type: string
                      country:
                        type: string
                      postalCode:
                        type: string
                      apartmentNo:
                        type: string
                      doorNo:
                        type: string
                      is_primary:
                        type: boolean
      404:
        description: User not found.
      500:
        description: An error occurred.
    """
    try:
        user_id = get_jwt_identity()
        data, error = fetch_user_data(user_id)
        if error:
            status_code = 404 if error == "User not found" else 400
            return jsonify({"message": error}), status_code

        return jsonify(data), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@user_bp.route("/user/password", methods=["PUT"])
@jwt_required()
def update_password():
    """
    Update the user's password.
    Expects a JSON payload with:
      - old_password: the current password
      - new_password: the new password to set
    ---
    tags:
      - User
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - old_password
              - new_password
            properties:
              old_password:
                type: string
              new_password:
                type: string
    responses:
      200:
        description: Password updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: Validation error or incorrect old password.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return jsonify({"message": "Old and new passwords are required"}), 400

        user_id = get_jwt_identity()
        success, message = change_password(user_id, old_password, new_password)
        if not success:
            return jsonify({"message": message}), 400

        return jsonify({"message": message}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@user_bp.route("/user/username", methods=["PUT"])
@jwt_required()
def update_username():
    """
    Update the user's username.
    Expects a JSON payload with:
      - username: the new username
    ---
    tags:
      - User
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
            properties:
              username:
                type: string
    responses:
      200:
        description: Username updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: New username is required.
      404:
        description: User not found.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        new_username = data.get("username")

        if not new_username:
            return jsonify({"message": "New username is required"}), 400

        user_id = get_jwt_identity()
        success, message = change_username(user_id, new_username)
        if not success:
            return jsonify({"message": message}), 404

        return jsonify({"message": message}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@user_bp.route("/user/email", methods=["PUT"])
@jwt_required()
def update_email():
    """
    Update the user's email and send a verification email.
    Expects a JSON payload with:
      - old_email: the current email address
      - new_email: the new email address to update to
    ---
    tags:
      - User
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - old_email
              - new_email
            properties:
              old_email:
                type: string
              new_email:
                type: string
    responses:
      200:
        description: Email updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: Validation error or email mismatch.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        old_email = data.get("old_email")
        new_email = data.get("new_email")

        if not old_email or not new_email:
            return jsonify({"message": "Old and new emails are required"}), 400

        # Validate email formats
        if not is_valid_email(old_email):
            return jsonify({"message": "Invalid old email format"}), 400
        if not is_valid_email(new_email):
            return jsonify({"message": "Invalid new email format"}), 400

        user_id = get_jwt_identity()
        success, message = change_email(user_id, old_email, new_email)
        if not success:
            return jsonify({"message": message}), 400

        return jsonify({"message": message}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500

# ----------------------------
# Favorites Sub-Resource
# ----------------------------

@user_bp.route("/user/favorites", methods=["GET"])
@jwt_required()
def get_favorites_route():
    """
    Get the list of favorite restaurants for the authenticated user.
    ---
    tags:
      - Favorites
    security:
      - BearerAuth: []
    responses:
      200:
        description: Favorites retrieved successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                favorites:
                  type: array
                  items:
                    type: integer
      500:
        description: An error occurred.
    """
    try:
        user_id = get_jwt_identity()
        favorites = get_favorites(user_id)
        return jsonify({"favorites": favorites}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500

@user_bp.route("/user/favorites", methods=["POST"])
@jwt_required()
def add_favorite_route():
    """
    Add a restaurant to the user's favorites.
    Expects a JSON payload with:
      - restaurant_id: the ID of the restaurant to add
    ---
    tags:
      - Favorites
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - restaurant_id
            properties:
              restaurant_id:
                type: integer
    responses:
      201:
        description: Restaurant added to favorites successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: Validation error.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")

        if not restaurant_id:
            return jsonify({"message": "Restaurant ID is required"}), 400

        user_id = get_jwt_identity()
        success, message = add_favorite(user_id, restaurant_id)
        if not success:
            return jsonify({"message": message}), 400

        return jsonify({"message": message}), 201

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500

@user_bp.route("/user/favorites", methods=["DELETE"])
@jwt_required()
def remove_favorite_route():
    """
    Remove a restaurant from the user's favorites.
    Expects a JSON payload with:
      - restaurant_id: the ID of the restaurant to remove
    ---
    tags:
      - Favorites
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - restaurant_id
            properties:
              restaurant_id:
                type: integer
    responses:
      200:
        description: Restaurant removed from favorites successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Favorite not found.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")

        if not restaurant_id:
            return jsonify({"message": "Restaurant ID is required"}), 400

        user_id = get_jwt_identity()
        success, message = remove_favorite(user_id, restaurant_id)
        if not success:
            return jsonify({"message": message}), 404

        return jsonify({"message": message}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500

@user_bp.route('/users/active-orders', methods=['GET'])
@jwt_required()  # Assuming you're using Flask-JWT-Extended
def get_user_active_orders():
    current_user_id = get_jwt_identity()  # Get the current user's ID
    return get_user_active_orders_service(current_user_id)
