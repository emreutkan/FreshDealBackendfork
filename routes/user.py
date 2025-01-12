# routes/user_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_services import (
    fetch_user_data,
    change_password,
    change_username,
    change_email,
    add_favorite,
    remove_favorite,
    get_favorites
)

user_bp = Blueprint("user", __name__)

@user_bp.route("/user/data", methods=["GET"])
@jwt_required()
def get_user_data_route():
    """
    Fetch user information and their associated addresses based on the JWT token.
    """
    try:
        user_id = get_jwt_identity()
        data, error = fetch_user_data(user_id)
        if error:
            return jsonify({"message": error}), 404 if error == "User not found" else 400

        return jsonify(data), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/update_password", methods=["POST"])
@jwt_required()
def update_password_route():
    """
    Update the user's password if the old password matches.
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
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/update_username", methods=["POST"])
@jwt_required()
def update_username_route():
    """
    Update the user's username.
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
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
import re

def is_valid_email(email):
    """
    Validates an email address using a regex pattern.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@user_bp.route("/update_email", methods=["POST"])
@jwt_required()
def update_email_route():
    """
    Update the user's email and send a mock verification email.
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
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/favorites", methods=["POST"])
@jwt_required()
def add_to_favorites_route():
    """
    Add a restaurant to the user's favorites.
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
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/favorites", methods=["DELETE"])
@jwt_required()
def remove_from_favorites_route():
    """
    Remove a restaurant from the user's favorites.
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
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_user_favorites_route():
    """
    Get a list of the user's favorite restaurants.
    """
    try:
        user_id = get_jwt_identity()
        favorites = get_favorites(user_id)
        # Correct jsonify usage
        return jsonify({"favorites": favorites}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
