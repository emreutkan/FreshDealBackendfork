from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, CustomerAddress, UserFavorites

user_bp = Blueprint("user", __name__)

@user_bp.route("/user/data", methods=["GET"])
@jwt_required()
def get_user_data():
    """
    Fetch user information and their associated addresses based on the JWT token.
    """
    try:
        # Get user_id from the JWT token
        user_id = get_jwt_identity()

        # Fetch user details
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role
        }

        # Fetch user addresses
        user_addresses = CustomerAddress.query.filter_by(user_id=user_id).all()
        user_address_list = [
            {
                "id": addr.id,
                "title": addr.title,
                "longitude": float(addr.longitude),
                "latitude": float(addr.latitude),
                "street": addr.street,
                "neighborhood": addr.neighborhood,
                "district": addr.district,
                "province": addr.province,
                "country": addr.country,
                "postalCode": addr.postalCode,
                "apartmentNo": addr.apartmentNo,
                "doorNo": addr.doorNo,
                "is_primary": addr.is_primary,
            }
            for addr in user_addresses
        ]

        # Return combined data
        return jsonify({
            "user_data": user_data,
            "user_address_list": user_address_list
        }), 200

    except Exception as e:
        # Log and return an error response for unexpected exceptions
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@user_bp.route("/update_password", methods=["POST"])
@jwt_required()
def update_password():
    """
    Update the user's password if the old password matches.
    """
    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user or not check_password_hash(user.password, old_password):
            return jsonify({"message": "Old password is incorrect"}), 400

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@user_bp.route("/update_username", methods=["POST"])
@jwt_required()
def update_username():
    """
    Update the user's username.
    """
    try:
        data = request.get_json()
        new_username = data.get("username")

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user.name = new_username
        db.session.commit()

        return jsonify({"message": "Username updated successfully"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@user_bp.route("/update_email", methods=["POST"])
@jwt_required()
def update_email():
    """
    Update the user's email and send a mock verification email.
    """
    try:
        data = request.get_json()
        old_email = data.get("old_email")
        new_email = data.get("new_email")

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user or user.email != old_email:
            return jsonify({"message": "Old email is incorrect"}), 400

        user.email = new_email
        db.session.commit()

        send_verification_email(new_email)

        return jsonify({"message": "Email updated successfully"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

def send_verification_email(email):
    """
    Mock function to simulate sending a verification email.
    """
    print(f"Verification email sent to {email}")

@user_bp.route("/favorites", methods=["POST"])
@jwt_required()
def add_to_favorites():
    """
    Add a restaurant to the user's favorites.
    """
    try:
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")

        user_id = get_jwt_identity()

        # Check if the favorite already exists
        existing_favorite = UserFavorites.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if existing_favorite:
            return jsonify({"message": "Restaurant is already in your favorites"}), 400

        # Add favorite
        favorite = UserFavorites(user_id=user_id, restaurant_id=restaurant_id)
        db.session.add(favorite)
        db.session.commit()

        return jsonify({"message": "Restaurant added to favorites"}), 201

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@user_bp.route("/favorites", methods=["DELETE"])
@jwt_required()
def remove_from_favorites():
    """
    Remove a restaurant from the user's favorites.
    """
    try:
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")

        user_id = get_jwt_identity()

        # Find and remove favorite
        favorite = UserFavorites.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if not favorite:
            return jsonify({"message": "Favorite not found"}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Restaurant removed from favorites"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@user_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_user_favorites():
    """
    Get a list of the user's favorite restaurants.
    """
    try:
        user_id = get_jwt_identity()

        # Fetch user's favorites
        favorites = UserFavorites.query.filter_by(user_id=user_id).all()
        if not favorites:
            return jsonify({"favorites": []}), 200

        favorite_restaurants = [
            {
                "restaurant_id": favorite.restaurant_id,
                "restaurant_name": favorite.restaurant.restaurantName,
            }
            for favorite in favorites
        ]

        return jsonify({"favorites": favorite_restaurants}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
