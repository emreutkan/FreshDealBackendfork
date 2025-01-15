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
    Get Current User's Cart Items
    ---
    tags:
      - Cart
    summary: Retrieve all items in the current user's shopping cart
    description: Returns a list of all items currently in the authenticated user's shopping cart, including details such as quantity and price
    security:
      - BearerAuth: []
    responses:
      200:
        description: Successfully retrieved cart items
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                cart:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: Cart item ID
                        example: 1
                      listing_id:
                        type: integer
                        description: ID of the listed item
                        example: 123
                      title:
                        type: string
                        description: Name of the item
                        example: "Delicious Pizza"
                      original_price:
                        type: number
                        format: float
                        description: Original price of the item
                        example: 15.99
                      pick_up_price:
                        type: number
                        format: float
                        description: Pick-up price of the item
                        example: 12.99
                      delivery_price:
                        type: number
                        format: float
                        description: Delivery price of the item
                        example: 17.99
                      count:
                        type: integer
                        description: Quantity of items in cart
                        example: 2
                      added_at:
                        type: string
                        format: date-time
                        description: Timestamp when item was added to cart
                        example: "2025-01-15T15:10:16Z"
      401:
        description: Authentication required
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "An error occurred"
                error:
                  type: string
                  example: "Internal server error details"
    """
    try:
        user_id = get_jwt_identity()
        cart, status = get_cart_items_service(user_id)
        return jsonify({"success": True, "cart": cart}), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    """
    Add Item to Cart
    ---
    tags:
      - Cart
    summary: Add a new item to the shopping cart
    description: |
      Adds a specified quantity of an item to the user's cart.
      If the item already exists in the cart, the quantity will be updated.
      Validates stock availability before adding.
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
                description: ID of the listing to add to cart
                example: 123
              count:
                type: integer
                description: Quantity to add (defaults to 1)
                default: 1
                minimum: 1
                example: 2
    responses:
      201:
        description: Item successfully added to cart
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Item added to cart"
      400:
        description: Invalid request or insufficient stock
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Insufficient stock for 'Item Name'. Requested: 5, Available: 3"
      401:
        description: Authentication required
      404:
        description: Listing not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON data provided"
            }), 400

        listing_id = data.get("listing_id")
        if not listing_id:
            return jsonify({
                "success": False,
                "message": "listing_id is required"
            }), 400

        count = data.get("count", 1)
        user_id = get_jwt_identity()

        response, status = add_to_cart_service(user_id, listing_id, count)
        return jsonify({**response, "success": status == 201}), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart", methods=["PUT"])
@jwt_required()
def update_cart_item():
    """
    Update Cart Item Quantity
    ---
    tags:
      - Cart
    summary: Update the quantity of an item in the cart
    description: |
      Updates the quantity of a specific item in the user's cart.
      Validates stock availability before updating.
      Use count=0 to effectively remove the item from cart.
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
                description: ID of the listing to update
                example: 123
              count:
                type: integer
                description: New quantity for the item
                minimum: 0
                example: 3
    responses:
      200:
        description: Cart item successfully updated
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Cart item updated"
      400:
        description: Invalid request or insufficient stock
      401:
        description: Authentication required
      404:
        description: Item not found in cart
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON data provided"
            }), 400

        listing_id = data.get("listing_id")
        count = data.get("count")

        if not listing_id or count is None:
            return jsonify({
                "success": False,
                "message": "listing_id and count are required"
            }), 400

        user_id = get_jwt_identity()
        response, status = update_cart_item_service(user_id, listing_id, count)
        return jsonify({**response, "success": status == 200}), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500


@cart_bp.route("/cart/<int:listing_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(listing_id):
    """
    Remove Item from Cart
    ---
    tags:
      - Cart
    summary: Remove an item from the shopping cart
    description: Completely removes a specific item from the user's cart regardless of quantity
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: listing_id
        required: true
        schema:
          type: integer
        description: The ID of the listing to remove from cart
        example: 123
    responses:
      200:
        description: Item successfully removed from cart
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Item removed from cart"
      401:
        description: Authentication required
      404:
        description: Item not found in cart
      500:
        description: Internal server error
    """
    try:
        user_id = get_jwt_identity()
        response, status = remove_from_cart_service(user_id, listing_id)
        return jsonify({**response, "success": status == 200}), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred",
            "error": str(e)
        }), 500