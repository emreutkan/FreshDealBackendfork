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

    :param restaurant_id: ID of the restaurant
    :param owner_id: The current user’s id (owner)
    :param form_data: A dictionary (form values) with keys: title, description, price, count
    :param file_obj: The FileStorage object from Flask for the image upload
    :param url_for_func: A reference to Flask's url_for to build URLs (passed from routes)
    :return: Tuple with (response dictionary, HTTP status code)
    """
    # Validate owner exists and is authorized is done in the route, so not repeating it here.

    title = form_data.get("title")
    description = form_data.get("description", "")
    price = form_data.get("price")
    count = form_data.get("count", 1)

    # Validate required fields
    if not title or not price:
        return {"success": False, "message": "Title and price are required"}, 400

    try:
        count = int(count)
        if count <= 0:
            return {"success": False, "message": "Count must be a positive integer"}, 400
    except ValueError:
        return {"success": False, "message": "Count must be an integer"}, 400

    # Handle file upload
    if file_obj and allowed_file(file_obj.filename):
        original_filename = secure_filename(file_obj.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file_obj.save(filepath)
        # Build external URL to serve this image using the provided url_for function
        image_url = url_for_func('listings.get_uploaded_file', filename=unique_filename, _external=True)
    else:
        return {"success": False, "message": "Invalid or missing image file"}, 400

    # Validate restaurant exists and that the owner is the restaurant owner
    from src.models import Restaurant  # imported here to avoid circular import if needed
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404
    if int(restaurant.owner_id) != int(owner_id):
        return {"success": False, "message": "You do not own this restaurant"}, 403

    # Create new listing record
    new_listing = Listing(
        restaurant_id=restaurant_id,
        title=title,
        description=description,
        image_url=image_url,
        price=float(price),
        count=count
    )
    db.session.add(new_listing)
    db.session.commit()

    return {
        "success": True,
        "message": "Listing added successfully!",
        "listing": new_listing.to_dict()  # assuming Listing has a to_dict method
    }, 201


def get_listings_service(restaurant_id, page, per_page, url_for_func):
    """
    Retrieve listings with optional filtering by restaurant and pagination.
    """
    from src.models import Listing  # local import to avoid circular dependencies
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
            image_url = url_for_func('listings.get_uploaded_file', filename=filename, _external=True)
        else:
            image_url = None
        listings_data.append({
            "id": listing.id,
            "restaurant_id": listing.restaurant_id,
            "title": listing.title,
            "description": listing.description,
            "image_url": image_url,
            "original_price": float(listing.original_price),
            "pick_up_price": float(listing.pick_up_price),
            "delivery_price": float(listing.delivery_price),
            "count": listing.count,
            "consume_within": listing.consume_within,
            "available_for_delivery": listing.available_for_delivery,
            "available_for_pickup": listing.available_for_pickup,

        })
    print(listings_data)

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
