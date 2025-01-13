# routes/listings.py

import os
from flask import Blueprint, request, jsonify, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.services.listings_service import (
    create_listing_service,
    get_listings_service,
    search_service  # if needed for extra validation
)
from app.models import User

listings_bp = Blueprint("listings", __name__)

# Define the absolute path for the upload folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@listings_bp.route("/restaurants/<int:restaurant_id>/listings", methods=["POST"])
@jwt_required()
def create_listing(restaurant_id):
    """
    Create a new listing for a restaurant
    ---
    tags:
      - Listings
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: restaurant_id
        type: integer
        required: true
        description: ID of the restaurant
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - title
              - price
              - image
            properties:
              title:
                type: string
              description:
                type: string
              price:
                type: number
                format: float
              count:
                type: integer
                default: 1
              image:
                type: string
                format: binary
    responses:
      201:
        description: Listing added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                listing:
                  type: object
      400:
        description: Validation error or missing image file
      403:
        description: Forbidden (not an owner or not the restaurant's owner)
      404:
        description: Restaurant or owner not found
    """
    try:
        # Validate user/owner permissions
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)
        if not owner:
            return jsonify({"success": False, "message": "Owner not found"}), 404

        if owner.role != "owner":
            return jsonify({"success": False, "message": "Only owners can add listings"}), 403

        # For file uploads and form data, use request.form and request.files
        form_data = request.form.to_dict()
        file_obj = request.files.get("image")

        response, status = create_listing_service(
            restaurant_id, owner_id, form_data, file_obj, url_for
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@listings_bp.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    """
    Serve the uploaded file
    ---
    tags:
      - Listings
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: The name of the file to retrieve
    responses:
      200:
        description: The requested file
      404:
        description: File not found
    """
    try:
        # Secure filename to avoid directory traversal
        filename = secure_filename(filename)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"success": False, "message": "File not found"}), 404


@listings_bp.route("/listings", methods=["GET"])
def get_listings():
    """
    Retrieve a list of listings with optional filtering and pagination
    ---
    tags:
      - Listings
    parameters:
      - in: query
        name: restaurant_id
        type: integer
        required: false
        description: Filter by restaurant ID
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: Page number for pagination
      - in: query
        name: per_page
        type: integer
        required: false
        default: 10
        description: Listings per page
    responses:
      200:
        description: Listings successfully retrieved
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                data:
                  type: array
                  items:
                    type: object
                pagination:
                  type: object
                  properties:
                    total:
                      type: integer
                    pages:
                      type: integer
                    current_page:
                      type: integer
                    per_page:
                      type: integer
                    has_next:
                      type: boolean
                    has_prev:
                      type: boolean
      500:
        description: Error fetching listings
    """
    try:
        restaurant_id = request.args.get('restaurant_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        response, status = get_listings_service(restaurant_id, page, per_page, url_for)
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching listings",
            "error": str(e)
        }), 500


@listings_bp.route("/search", methods=["GET"])
def search():
    """
    Search restaurants or listings
    ---
    tags:
      - Listings
    parameters:
      - in: query
        name: type
        type: string
        required: true
        description: 'Type of search: "restaurant" or "listing"'
      - in: query
        name: query
        type: string
        required: true
        description: Search text (partial match)
      - in: query
        name: restaurant_id
        type: integer
        required: false
        description: Required if type is "listing"
    responses:
      200:
        description: Search results returned successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                type:
                  type: string
                results:
                  type: array
                  items:
                    type: object
      400:
        description: Missing or invalid parameters
      500:
        description: Error performing search
    """
    try:
        search_type = request.args.get("type")
        query_text = request.args.get("query", "").strip()
        restaurant_id = request.args.get("restaurant_id", type=int)
        response, status = search_service(search_type, query_text, restaurant_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while performing search",
            "error": str(e)
        }), 500
