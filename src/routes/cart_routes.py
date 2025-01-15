# routes/cart_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.cart_service import (
    get_cart_items_service,
    add_to_cart_service,
    update_cart_item_service,
    remove_from_cart_service
)

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart_items():
    """
    Get the current user's cart items.
    ---
    tags:
      - Cart
    security:
      - BearerAuth: []
    responses:
      200:
        description: A list of cart items.
        content:
          application/json:
            schema:
              type: object
              properties:
                cart:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      listing_id:
                        type: integer
                      title:
                        type: string
                      price:
                        type: number
                        format: float
                      count:
                        type: integer
                      added_at:
                        type: string
                        format: date-time
      500:
        description: An error occurred.
    """
    try:
        user_id = get_jwt_identity()
        cart, status = get_cart_items_service(user_id)
        return jsonify({"cart": cart}), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    """
    Add an item to the user's cart.
    Expects a JSON payload with:
      - listing_id: integer (required)
      - count: integer (optional, defaults to 1)
    ---
    tags:
      - Cart
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - listing_id
            properties:
              listing_id:
                type: integer
              count:
                type: integer
                default: 1
    responses:
      201:
        description: Item added to cart.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Listing not found.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        listing_id = data.get("listing_id")
        count = data.get("count", 1)
        user_id = get_jwt_identity()

        response, status = add_to_cart_service(user_id, listing_id, count)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart", methods=["PUT"])
@jwt_required()
def update_cart_item():
    """
    Update the quantity of an item in the user's cart.
    Expects a JSON payload with:
      - listing_id: integer (required)
      - count: integer (required)
    ---
    tags:
      - Cart
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - listing_id
              - count
            properties:
              listing_id:
                type: integer
              count:
                type: integer
    responses:
      200:
        description: Cart item updated.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Item not found in cart.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        listing_id = data.get("listing_id")
        count = data.get("count")
        user_id = get_jwt_identity()

        response, status = update_cart_item_service(user_id, listing_id, count)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart/<int:listing_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(listing_id):
    """
    remove an item from the user's cart.
    ---
    tags:
      - Cart
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: listing_id
        required: true
        schema:
          type: integer
        description: The listing ID of the item to remove.
    responses:
      200:
        description: Item removed from cart.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Item not found in cart.
      500:
        description: An error occurred.
    """
    try:
        user_id = get_jwt_identity()
        response, status = remove_from_cart_service(user_id, listing_id)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500
