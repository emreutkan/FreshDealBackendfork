# routes/restaurant_routes.py
import os
from flask import Blueprint, request, jsonify, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.services.restaurant_service import (
    create_restaurant_service,
    get_restaurants_service,
    get_restaurant_service,
    delete_restaurant_service,
    get_restaurants_proximity_service,
    add_comment_service
)
from app.models import User

restaurant_bp = Blueprint("restaurant", __name__)

# Define upload folder (should match the one in the service layer)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@restaurant_bp.route("/restaurants", methods=["POST"])
@jwt_required()
def create_restaurant():
    """
    Create a new restaurant.

    Expects multipart/form-data with fields:
      - restaurantName (string, required)
      - restaurantDescription (string)
      - longitude (number, required)
      - latitude (number, required)
      - category (string, required)
      - workingDays (multiple values or comma‑separated string)
      - workingHoursStart (string)
      - workingHoursEnd (string)
      - listings (integer)
      - pickup ("true"/"false")
      - delivery ("true"/"false")
      - maxDeliveryDistance (number)
      - deliveryFee (number)
      - minOrderAmount (number)
      - image (file, optional)

    ---
    tags:
      - Restaurant
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - restaurantName
              - longitude
              - latitude
              - category
            properties:
              restaurantName:
                type: string
              restaurantDescription:
                type: string
              longitude:
                type: number
              latitude:
                type: number
              category:
                type: string
              workingDays:
                type: array
                items:
                  type: string
              workingHoursStart:
                type: string
              workingHoursEnd:
                type: string
              listings:
                type: integer
                default: 0
              pickup:
                type: string
                enum: [true, false]
              delivery:
                type: string
                enum: [true, false]
              maxDeliveryDistance:
                type: number
              deliveryFee:
                type: number
              minOrderAmount:
                type: number
              image:
                type: string
                format: binary
    responses:
      201:
        description: Restaurant added successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                restaurant:
                  type: object
      400:
        description: Invalid input.
      403:
        description: Forbidden.
      404:
        description: Owner not found.
    """
    try:
        owner_id = get_jwt_identity()
        # Optionally, verify owner exists and has role "owner"
        owner = User.query.get(owner_id)
        if not owner:
            return jsonify({"success": False, "message": "Owner not found"}), 404
        if owner.role != "owner":
            return jsonify({"success": False, "message": "Only owners can add a restaurant"}), 403

        response, status = create_restaurant_service(owner_id, request.form, request.files, url_for)
        return jsonify(response), status

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurant_bp.route("/restaurants", methods=["GET"])
@jwt_required()
def get_restaurants():
    """
    Get all restaurants for the authenticated owner.

    ---
    tags:
      - Restaurant
    security:
      - BearerAuth: []
    responses:
      200:
        description: A list of restaurants.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
      404:
        description: No restaurant found for the owner.
      500:
        description: An error occurred.
    """
    try:
        owner_id = get_jwt_identity()
        response, status = get_restaurants_service(owner_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurant_bp.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    """
    Get a single restaurant by ID.

    ---
    tags:
      - Restaurant
    parameters:
      - in: path
        name: restaurant_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Restaurant details.
      404:
        description: Restaurant not found.
      500:
        description: An error occurred.
    """
    try:
        response, status = get_restaurant_service(restaurant_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurant_bp.route("/restaurants/<int:restaurant_id>", methods=["DELETE"])
@jwt_required()
def delete_restaurant(restaurant_id):
    """
    Delete a restaurant.

    ---
    tags:
      - Restaurant
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: restaurant_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Restaurant successfully deleted.
      403:
        description: Not the owner.
      404:
        description: Restaurant not found.
      500:
        description: An error occurred.
    """
    try:
        owner_id = get_jwt_identity()
        response, status = delete_restaurant_service(restaurant_id, owner_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurant_bp.route("/uploads/<filename>", methods=['GET'])
def get_uploaded_file(filename):
    """
    Serve an uploaded file.

    ---
    tags:
      - Restaurant
    parameters:
      - in: path
        name: filename
        required: true
        schema:
          type: string
    responses:
      200:
        description: The requested file.
      404:
        description: File not found.
    """
    try:
        filename = secure_filename(filename)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"success": False, "message": "File not found"}), 404


@restaurant_bp.route("/restaurants/proximity", methods=["POST"])
@jwt_required()  # Optional: remove if not needed
def get_restaurants_proximity():
    """
    Get restaurants by proximity.

    Expects a JSON payload:
    {
       "latitude": number (required),
       "longitude": number (required),
       "radius": number (optional, default 10 km)
    }

    ---
    tags:
      - Restaurant
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - latitude
              - longitude
            properties:
              latitude:
                type: number
              longitude:
                type: number
              radius:
                type: number
                default: 10
    responses:
      200:
        description: Restaurants within the specified radius.
      400:
        description: Missing or invalid parameters.
      404:
        description: No restaurants found.
      500:
        description: An error occurred.
    """
    try:
        data = request.get_json()
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        radius = data.get('radius', 10)
        response, status = get_restaurants_proximity_service(user_lat, user_lon, radius)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurant_bp.route("/restaurants/<int:restaurant_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(restaurant_id):
    """
    Add a comment to a restaurant.

    Expects a JSON payload with:
      - comment (string, required)
      - rating (number between 0 and 5, required)
      - purchase_id (integer, required)

    ---
    tags:
      - Restaurant
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: restaurant_id
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - comment
              - rating
              - purchase_id
            properties:
              comment:
                type: string
              rating:
                type: number
              purchase_id:
                type: integer
    responses:
      201:
        description: Comment added successfully.
      400:
        description: Missing or invalid input.
      403:
        description: Forbidden (invalid purchase or duplicate comment).
      500:
        description: An error occurred.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        response, status = add_comment_service(restaurant_id, user_id, data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
