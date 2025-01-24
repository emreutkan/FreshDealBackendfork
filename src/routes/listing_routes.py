import os
from flask import Blueprint, request, jsonify, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.services.listings_service import (
    create_listing_service,
    get_listings_service,
    search_service
)
from src.models import User

listings_bp = Blueprint("listings", __name__)

# Define the absolute path for the upload folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Common schema definitions for reuse
LISTING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "description": "Unique identifier for the listing"},
        "restaurant_id": {"type": "integer", "description": "ID of the restaurant this listing belongs to"},
        "title": {"type": "string", "description": "Title of the listing"},
        "description": {"type": "string", "description": "Detailed description of the listing"},
        "image_url": {"type": "string", "description": "URL to the listing's image"},
        "original_price": {"type": "number", "format": "float", "description": "Original price of the item"},
        "pick_up_price": {"type": "number", "format": "float", "description": "Price for pick-up orders"},
        "delivery_price": {"type": "number", "format": "float", "description": "Price for delivery orders"},
        "count": {"type": "integer", "description": "Number of items available"},
        "consume_within": {"type": "integer", "description": "Number of days within which the item should be consumed"},
        "available_for_pickup": {"type": "boolean", "description": "Whether the item is available for pickup"},
        "available_for_delivery": {"type": "boolean", "description": "Whether the item is available for delivery"}
    }
}

@listings_bp.route("/restaurants/<int:restaurant_id>/listings", methods=["POST"])
@jwt_required()
def create_listing(restaurant_id):
    """
     Create a new listing for a restaurant
     ---
     tags:
       - Listings
     summary: Create a new food listing for a restaurant
     description: |
       Creates a new food listing with details including prices, availability, and an image.
       Only restaurant owners can create listings.
       Current time (UTC): 2025-01-15 15:17:37
     parameters:
       - in: path
         name: restaurant_id
         type: integer
         required: true
         description: ID of the restaurant
     consumes:
       - multipart/form-data
     parameters:
       - in: formData
         name: title
         type: string
         required: true
         description: Title of the listing
         example: "Fresh Pizza Margherita"
       - in: formData
         name: description
         type: string
         required: false
         description: Detailed description of the listing
         example: "Traditional Italian pizza with fresh basil"
       - in: formData
         name: original_price
         type: number
         required: true
         description: Original price of the item
         example: 15.99
       - in: formData
         name: pick_up_price
         type: number
         required: false
         description: Price for pick-up orders
         example: 12.99
       - in: formData
         name: delivery_price
         type: number
         required: false
         description: Price for delivery orders
         example: 17.99
       - in: formData
         name: count
         type: integer
         required: false
         default: 1
         description: Number of items available
         example: 5
       - in: formData
         name: consume_within
         type: integer
         required: true
         description: Days within which the item should be consumed
         example: 2
       - in: formData
         name: image
         type: file
         required: true
         description: Image file for the listing
     responses:
       201:
         description: Listing created successfully
         schema:
           type: object
           properties:
             success:
               type: boolean
               example: true
             message:
               type: string
               example: "Listing created successfully!"
             listing:
               type: object
               properties:
                 id:
                   type: integer
                   example: 1
                 title:
                   type: string
                   example: "Fresh Pizza Margherita"
                 original_price:
                   type: number
                   example: 15.99
       400:
         description: Validation error
         schema:
           type: object
           properties:
             success:
               type: boolean
               example: false
             message:
               type: string
               example: "Title and original price are required"
       403:
         description: Not authorized
         schema:
           type: object
           properties:
             success:
               type: boolean
               example: false
             message:
               type: string
               example: "Only owners can add listings"
     """

    try:
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)
        if not owner:
            return jsonify({"success": False, "message": "Owner not found"}), 404

        if owner.role != "owner":
            return jsonify({"success": False, "message": "Only owners can add listings"}), 403

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
       Serve an uploaded listing image file
       ---
       tags:
         - Listings
       summary: Retrieve a listing's image file
       description: |
         Returns the image file associated with a listing.
         Current time (UTC): 2025-01-15 15:17:37
       parameters:
         - in: path
           name: filename
           type: string
           required: true
           description: Name of the image file to retrieve
       responses:
         200:
           description: Image file
         404:
           description: File not found
           schema:
             type: object
             properties:
               success:
                 type: boolean
                 example: false
               message:
                 type: string
                 example: "File not found"
    """
    try:
        filename = secure_filename(filename)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"success": False, "message": "File not found"}), 404


@listings_bp.route("/listings", methods=["GET"])
def get_listings():
    """
    Get all listings with optional filtering
    ---
    tags:
      - Listings
    summary: Retrieve paginated list of food listings
    description: |
      Returns a paginated list of all food listings.
      Can be filtered by restaurant ID.
      Current time (UTC): 2025-01-15 15:17:37
    parameters:
      - in: query
        name: restaurant_id
        type: integer
        required: false
        description: Filter listings by restaurant ID
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: Page number
      - in: query
        name: per_page
        type: integer
        required: false
        default: 10
        description: Number of items per page (max 100)
    responses:
      200:
        description: List of listings
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "Fresh Pizza Margherita"
                  original_price:
                    type: number
                    example: 15.99
            pagination:
              type: object
              properties:
                total:
                  type: integer
                  example: 50
                pages:
                  type: integer
                  example: 5
                current_page:
                  type: integer
                  example: 1
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "An error occurred while fetching listings"
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
        Search listings and restaurants
        ---
        tags:
          - Listings
        summary: Search for food listings or restaurants
        description: |
          Performs a search across listings or restaurants based on query text.
          Current time (UTC): 2025-01-15 15:17:37
        parameters:
          - in: query
            name: type
            type: string
            enum: [restaurant, listing]
            required: true
            description: Type of search to perform
          - in: query
            name: query
            type: string
            required: true
            description: Search text for partial matching
          - in: query
            name: restaurant_id
            type: integer
            required: false
            description: Required for listing search - restaurant to search within
        responses:
          200:
            description: Search results
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                type:
                  type: string
                  example: "listing"
                results:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      title:
                        type: string
                        example: "Fresh Pizza Margherita"
          400:
            description: Invalid parameters
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Invalid search type"
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

@listings_bp.route("/listings/<int:listing_id>", methods=["PUT"])
@jwt_required()
def edit_listing(listing_id):
    """
    Edit an existing listing
    ---
    tags:
      - Listings
    summary: Edit an existing food listing
    description: |
      Updates an existing food listing's details.
      Only the owner of the restaurant can edit their listings.
      Current time (UTC): 2025-01-23 21:31:45
    parameters:
      - in: path
        name: listing_id
        type: integer
        required: true
        description: ID of the listing to edit
      - in: formData
        name: title
        type: string
        required: false
        description: New title of the listing
        example: "Updated Pizza Margherita"
      - in: formData
        name: description
        type: string
        required: false
        description: New description of the listing
        example: "Updated Italian pizza with fresh basil"
      - in: formData
        name: original_price
        type: number
        required: false
        description: New original price of the item
        example: 16.99
      - in: formData
        name: pick_up_price
        type: number
        required: false
        description: New price for pick-up orders
        example: 13.99
      - in: formData
        name: delivery_price
        type: number
        required: false
        description: New price for delivery orders
        example: 18.99
      - in: formData
        name: count
        type: integer
        required: false
        description: New number of items available
        example: 6
      - in: formData
        name: consume_within
        type: integer
        required: false
        description: New number of days within which the item should be consumed
        example: 3
      - in: formData
        name: image
        type: file
        required: false
        description: New image file for the listing
    responses:
      200:
        description: Listing updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Listing updated successfully"
            listing:
              $ref: '#/definitions/Listing'
      403:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "You do not have permission to edit this listing"
      404:
        description: Listing not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Listing not found"
    """
    try:
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)
        if not owner:
            return jsonify({"success": False, "message": "Owner not found"}), 404

        form_data = request.form.to_dict()
        file_obj = request.files.get("image")

        from src.services.listings_service import edit_listing_service
        response, status = edit_listing_service(
            listing_id=listing_id,
            owner_id=owner_id,
            form_data=form_data,
            file_obj=file_obj,
            url_for_func=url_for
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the listing",
            "error": str(e)
        }), 500

@listings_bp.route("/listings/<int:listing_id>", methods=["DELETE"])
@jwt_required()
def delete_listing(listing_id):
    """
    Delete a listing
    ---
    tags:
      - Listings
    summary: Delete an existing food listing
    description: |
      Removes a food listing from the system.
      Only the owner of the restaurant can delete their listings.
      Current time (UTC): 2025-01-23 21:31:45
    parameters:
      - in: path
        name: listing_id
        type: integer
        required: true
        description: ID of the listing to delete
    responses:
      200:
        description: Listing deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Listing deleted successfully"
      403:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "You do not have permission to delete this listing"
      404:
        description: Listing not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Listing not found"
    """
    try:
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)
        if not owner:
            return jsonify({"success": False, "message": "Owner not found"}), 404

        from src.services.listings_service import delete_listing_service
        response, status = delete_listing_service(
            listing_id=listing_id,
            owner_id=owner_id
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the listing",
            "error": str(e)
        }), 500