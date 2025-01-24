# services/listings_service.py

import os
import uuid
from werkzeug.utils import secure_filename
from src.models import db, Listing

# Define the absolute path for the upload folder (relative to this file's directory)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'routes', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webm'}

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Return True if the filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_listing_service(restaurant_id, owner_id, form_data, file_obj, url_for_func):
    """
    Creates a new listing for a restaurant.
    """
    # Existing validation code remains the same
    title = form_data.get("title")
    description = form_data.get("description", "")
    original_price = form_data.get("original_price")
    pick_up_price = form_data.get("pick_up_price")
    delivery_price = form_data.get("delivery_price")
    count = form_data.get("count", 1)
    consume_within = form_data.get("consume_within")

    # Validate required fields
    if not title or not original_price or not consume_within:
        return {"success": False, "message": "Title, original price, and consume within days are required"}, 400

    try:
        count = int(count)
        consume_within = int(consume_within)
        if count <= 0 or consume_within <= 0:
            return {"success": False, "message": "Count and consume within must be positive integers"}, 400
    except ValueError:
        return {"success": False, "message": "Count and consume within must be integers"}, 400

    # Handle file upload (existing code remains the same)
    if file_obj and allowed_file(file_obj.filename):
        original_filename = secure_filename(file_obj.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file_obj.save(filepath)
        image_url = url_for_func('api_v1.listings.get_uploaded_file', filename=unique_filename, _external=True)
    else:
        return {"success": False, "message": "Invalid or missing image file"}, 400

    # Validate restaurant exists and ownership
    from src.models import Restaurant
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404
    if int(restaurant.owner_id) != int(owner_id):
        return {"success": False, "message": "You do not own this restaurant"}, 403

    # Create new listing record with all fields
    new_listing = Listing.create(
        restaurant_id=restaurant_id,
        title=title,
        description=description,
        image_url=image_url,
        original_price=float(original_price),
        pick_up_price=float(pick_up_price) if pick_up_price else None,
        delivery_price=float(delivery_price) if delivery_price else None,
        count=count,
        consume_within=consume_within
        # available_for_pickup and available_for_delivery are set automatically by create()
    )

    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404
    if int(restaurant.owner_id) != int(owner_id):
        return {"success": False, "message": "You do not own this restaurant"}, 403

    # Create new listing record with all fields


    # Increment the restaurant's listings count
    restaurant.listings += 1

    db.session.add(new_listing)
    db.session.commit()


    return {
        "success": True,
        "message": "Listing added successfully!",
        "listing": new_listing.to_dict()
    }, 201


def get_listings_service(restaurant_id, page, per_page, url_for_func):
    """
    Retrieve listings with optional filtering by restaurant and pagination.
    """
    from src.models import Listing
    query = Listing.query
    if restaurant_id:
        query = query.filter_by(restaurant_id=restaurant_id)
    query = query.order_by(Listing.id.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    listings = pagination.items

    listings_data = []
    for listing in listings:
        if listing.image_url:
            filename = os.path.basename(listing.image_url)
            image_url = url_for_func('api_v1.listings.get_uploaded_file', filename=filename, _external=True)
        else:
            image_url = None

        listings_data.append({
            "id": listing.id,
            "restaurant_id": listing.restaurant_id,
            "title": listing.title,
            "description": listing.description,
            "image_url": image_url,
            "original_price": float(listing.original_price),
            "pick_up_price": float(listing.pick_up_price) if listing.pick_up_price else None,
            "delivery_price": float(listing.delivery_price) if listing.delivery_price else None,
            "count": listing.count,
            "consume_within": listing.consume_within,
            "available_for_delivery": listing.available_for_delivery,
            "available_for_pickup": listing.available_for_pickup
        })

    response = {
        "success": True,
        "data": listings_data,
        "pagination": {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }
    return response, 200


def search_service(search_type, query_text, restaurant_id):
    """
    Search restaurants or listings based on provided criteria.
    """
    from src.models import Restaurant, Listing  # local imports to avoid circular dependencies

    if not query_text:
        return {"success": False, "message": "Query parameter is required"}, 400

    if search_type == "restaurant":
        results = Restaurant.query.filter(Restaurant.restaurantName.ilike(f"%{query_text}%")).all()
        data = [{
            "id": restaurant.id,
            "name": restaurant.restaurantName,
            "description": restaurant.restaurantDescription,
            "image_url": restaurant.image_url,
            "rating": float(restaurant.rating) if restaurant.rating else None,
            "category": restaurant.category,
        } for restaurant in results]
        return {"success": True, "type": "restaurant", "results": data}, 200

    elif search_type == "listing":
        if not restaurant_id:
            return {"success": False, "message": "Restaurant ID is required for listing search"}, 400

        results = Listing.query.filter(
            Listing.restaurant_id == restaurant_id,
            Listing.title.ilike(f"%{query_text}%")
        ).all()
        data = [{
            "id": listing.id,
            "restaurant_id": listing.restaurant_id,
            "title": listing.title,
            "description": listing.description,
            "image_url": listing.image_url,
            "price": float(listing.price),
            "count": listing.count,
        } for listing in results]
        return {"success": True, "type": "listing", "results": data}, 200

    else:
        return {"success": False, "message": "Invalid search type. Use 'restaurant' or 'listing'"}, 400


def edit_listing_service(listing_id, owner_id, form_data, file_obj=None, url_for_func=None):
    """
    Edits an existing listing.

    Args:
        listing_id: ID of the listing to edit
        owner_id: ID of the user making the request
        form_data: Dictionary containing the updated listing data
        file_obj: Optional new image file
        url_for_func: Function to generate URLs for file paths
    """
    # Fetch the existing listing
    listing = Listing.query.get(listing_id)
    if not listing:
        return {"success": False, "message": f"Listing with ID {listing_id} not found"}, 404

    # log the formdata recieved
    print(form_data)
    # Verify ownership through restaurant
    from src.models import Restaurant
    restaurant = Restaurant.query.get(listing.restaurant_id)
    if not restaurant or int(restaurant.owner_id) != int(owner_id):
        return {"success": False, "message": "You do not have permission to edit this listing"}, 403

    # Update the fields that are provided
    if "title" in form_data:
        listing.title = form_data["title"]
    if "description" in form_data:
        listing.description = form_data.get("description", "")
    if "original_price" in form_data:
        listing.original_price = float(form_data["original_price"])
    if "pick_up_price" in form_data:
        listing.pick_up_price = float(form_data["pick_up_price"]) if form_data["pick_up_price"] else None
    if "delivery_price" in form_data:
        listing.delivery_price = float(form_data["delivery_price"]) if form_data["delivery_price"] else None
    if "count" in form_data:
        try:
            count = int(form_data["count"])
            if count <= 0:
                return {"success": False, "message": "Count must be a positive integer"}, 400
            listing.count = count
        except ValueError:
            return {"success": False, "message": "Count must be an integer"}, 400
    if "consume_within" in form_data:
        try:
            consume_within = int(form_data["consume_within"])
            if consume_within <= 0:
                return {"success": False, "message": "Consume within must be a positive integer"}, 400
            listing.consume_within = consume_within
        except ValueError:
            return {"success": False, "message": "Consume within must be an integer"}, 400

    # Handle new image upload if provided
    if file_obj and allowed_file(file_obj.filename):
        # Delete old image file if it exists
        if listing.image_url:
            old_filename = os.path.basename(listing.image_url)
            old_filepath = os.path.join(UPLOAD_FOLDER, old_filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Save new image
        original_filename = secure_filename(file_obj.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file_obj.save(filepath)
        listing.image_url = url_for_func('api_v1.listings.get_uploaded_file',
                                         filename=unique_filename, _external=True)

    try:
        db.session.commit()
        return {
            "success": True,
            "message": "Listing updated successfully",
            "listing": listing.to_dict()
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Error updating listing: {str(e)}"}, 500


# In your service layer:
def delete_listing_service(listing_id):
    """
    Service to safely delete a listing
    """
    success, message = Listing.delete_listing(listing_id)
    print(success, message)
    if success:
        return {"message": message}, 200
    return {"message": message}, 400