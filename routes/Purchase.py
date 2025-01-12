from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Listing, Purchase, restaurantComments

purchase_bp = Blueprint("purchase", __name__)

@purchase_bp.route("/purchase", methods=["POST"])
@jwt_required()
def create_purchase():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        listing_id = data.get("listing_id")
        quantity = data.get("quantity", 1)

        if not listing_id or not quantity:
            return jsonify({"success": False, "message": "Listing ID and quantity are required"}), 400

        listing = Listing.query.get(listing_id)
        if not listing:
            return jsonify({"success": False, "message": "Listing not found"}), 404

        if listing.count < quantity:
            return jsonify({"success": False, "message": "Insufficient stock"}), 400

        # Calculate total price
        total_price = listing.price * quantity

        # Update listing count
        listing.count -= quantity

        # Create purchase
        purchase = Purchase(user_id=user_id, listing_id=listing_id, quantity=quantity, total_price=total_price)
        db.session.add(purchase)
        db.session.commit()

        return jsonify({"success": True, "message": "Purchase successful", "purchase_id": purchase.id}), 201

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@purchase_bp.route("/purchase/<int:purchase_id>/comment", methods=["POST"])
@jwt_required()
def add_comment(purchase_id):
    try:
        data = request.get_json()
        comment_text = data.get("comment_text")
        rating = data.get("rating")

        if not comment_text:
            return jsonify({"success": False, "message": "Comment text is required"}), 400

        purchase = Purchase.query.get(purchase_id)
        if not purchase or purchase.user_id != get_jwt_identity():
            return jsonify({"success": False, "message": "Purchase not found or access denied"}), 404

        if purchase.comment:
            return jsonify({"success": False, "message": "Comment already exists for this purchase"}), 400

        # Create and save comment
        comment = restaurantComments(purchase_id=purchase_id, comment_text=comment_text, rating=rating)
        db.session.add(comment)
        db.session.commit()

        return jsonify({"success": True, "message": "Comment added successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
