from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UserCart, Listing

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart_items():
    """Fetch the current user's cart items."""
    try:
        user_id = get_jwt_identity()
        cart_items = UserCart.query.filter_by(user_id=user_id).all()

        if not cart_items:
            return jsonify({"cart": []}), 200

        cart = [
            {
                "id": item.id,
                "listing_id": item.listing_id,
                "title": item.listing.title,
                "price": float(item.listing.price),
                "count": item.count,
                "added_at": item.added_at
            }
            for item in cart_items
        ]

        return jsonify({"cart": cart}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@cart_bp.route("/cart/add", methods=["POST"])
@jwt_required()
def add_to_cart():
    """Add an item to the user's cart."""
    try:
        data = request.get_json()
        listing_id = data.get("listing_id")
        count = data.get("count", 1)

        user_id = get_jwt_identity()

        # Check if the listing exists
        listing = Listing.query.get(listing_id)
        if not listing:
            return jsonify({"message": "Listing not found"}), 404

        # Check if the item is already in the cart
        cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        if cart_item:
            cart_item.count += count
        else:
            # Add new item to the cart
            cart_item = UserCart(user_id=user_id, listing_id=listing_id, count=count)
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({"message": "Item added to cart"}), 201

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@cart_bp.route("/cart/remove", methods=["DELETE"])
@jwt_required()
def remove_from_cart():
    """Remove an item from the user's cart."""
    try:
        data = request.get_json()
        listing_id = data.get("listing_id")

        user_id = get_jwt_identity()

        # Find and remove item from cart
        cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        if not cart_item:
            return jsonify({"message": "Item not found in cart"}), 404

        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({"message": "Item removed from cart"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@cart_bp.route("/cart/update", methods=["PUT"])
@jwt_required()
def update_cart_item():
    """Update the count of an item in the user's cart."""
    try:
        data = request.get_json()
        listing_id = data.get("listing_id")
        count = data.get("count")

        user_id = get_jwt_identity()

        # Find the cart item
        cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        if not cart_item:
            return jsonify({"message": "Item not found in cart"}), 404

        cart_item.count = count
        db.session.commit()

        return jsonify({"message": "Cart item updated"}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
