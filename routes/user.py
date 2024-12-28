from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, CustomerAddress

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
