import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Restaurant, Listing, User
from werkzeug.utils import secure_filename

listings_bp = Blueprint("listings", __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webm'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@listings_bp.route("/add_listing/<int:restaurant_id>", methods=["POST"])
@jwt_required()
def add_listing(restaurant_id):
    try:
        # Get the current user
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)

        if not owner:
            print("Validation error: Owner not found.")
            return jsonify({"success": False, "message": "Owner not found"}), 404

        if owner.role != "owner":
            print("Validation error: Only owners can add listings.")
            return jsonify({"success": False, "message": "Only owners can add listings"}), 403

        # Get the restaurant
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            print(f"Validation error: Restaurant with ID {restaurant_id} not found.")
            return jsonify({"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}), 404

        if restaurant.owner_id != owner_id:
            print("Validation error: User does not own this restaurant.")
            return jsonify({"success": False, "message": "You do not own this restaurant"}), 403

        # Get form data
        title = request.form.get("title")
        description = request.form.get("description", "")
        price = request.form.get("price")

        # Validate required fields
        if not title or not price:
            print("Validation error: Title or price is missing.")
            return jsonify({"success": False, "message": "Title and price are required"}), 400

        # Handle file upload
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_url = filepath  # Save the file path or URL
        else:
            print("Validation error: Invalid or missing image file.")
            return jsonify({"success": False, "message": "Invalid or missing image file"}), 400

        # Add new listing
        new_listing = Listing(
            restaurant_id=restaurant_id,
            title=title,
            description=description,
            image_url=image_url,
            price=float(price)
        )

        db.session.add(new_listing)
        db.session.commit()

        print(f"Listing '{title}' successfully added to restaurant '{restaurant.restaurantName}'.")
        return jsonify({"success": True, "message": "Listing added successfully!", "image_url": image_url}), 201

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500