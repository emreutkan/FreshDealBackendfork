# services/restaurant_service.py
import uuid
import os
from math import radians, cos, sin, asin, sqrt
from werkzeug.utils import secure_filename
from src.models import db, Restaurant, RestaurantComment, Purchase

# You can define the upload folder and allowed extensions globally if needed.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "routes"))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webm'}


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def restaurant_to_dict(restaurant):
    return {
        "id": restaurant.id,
        "owner_id": restaurant.owner_id,
        "restaurantName": restaurant.restaurantName,
        "restaurantDescription": restaurant.restaurantDescription,
        "longitude": float(restaurant.longitude),
        "latitude": float(restaurant.latitude),
        "category": restaurant.category,
        "workingDays": restaurant.workingDays.split(",") if restaurant.workingDays else [],
        "workingHoursStart": restaurant.workingHoursStart,
        "workingHoursEnd": restaurant.workingHoursEnd,
        "listings": restaurant.listings,
        "rating": float(restaurant.rating) if restaurant.rating else None,
        "ratingCount": restaurant.ratingCount,
        "image_url": restaurant.image_url,
        "pickup": restaurant.pickup,
        "delivery": restaurant.delivery,
        "maxDeliveryDistance": restaurant.maxDeliveryDistance,
        "deliveryFee": float(restaurant.deliveryFee) if restaurant.deliveryFee else None,
        "minOrderAmount": float(restaurant.minOrderAmount) if restaurant.minOrderAmount else None
    }

def create_restaurant_service(owner_id, form, files, url_for_func):
    """
    Create a new restaurant using multipart/form-data values.

    :param owner_id: The ID of the authenticated owner.
    :param form: The form data (request.form).
    :param files: The files (request.files).
    :param url_for_func: The url_for function to build URLs.

    :return: Tuple (response dict, HTTP status code)
    """
    # Retrieve owner’s information should be done in routes.
    restaurant_name = form.get('restaurantName')
    restaurant_description = form.get('restaurantDescription')
    longitude = form.get('longitude')
    latitude = form.get('latitude')
    category = form.get('category')
    working_hours_start = form.get('workingHoursStart')
    working_hours_end = form.get('workingHoursEnd')
    listings = form.get('listings', 0)
    working_days = form.getlist('workingDays')
    pickup = form.get('pickup', 'false').lower() == 'true'
    delivery = form.get('delivery', 'false').lower() == 'true'
    delivery_fee = form.get('deliveryFee')
    min_order_amount = form.get('minOrderAmount')
    max_delivery_distance = form.get('maxDeliveryDistance')

    # Validate required fields.
    if not restaurant_name:
        return {"success": False, "message": "Restaurant name is required"}, 400
    if not category:
        return {"success": False, "message": "Category is required"}, 400
    if longitude is None or latitude is None:
        return {"success": False, "message": "Longitude and latitude are required"}, 400

    try:
        longitude = float(longitude)
        latitude = float(latitude)
        listings = int(listings)
        max_delivery_distance = float(max_delivery_distance) if max_delivery_distance else None
        delivery_fee = float(delivery_fee) if delivery_fee else None
        min_order_amount = float(min_order_amount) if min_order_amount else None
    except ValueError:
        return {"success": False, "message": "Invalid format for numeric fields"}, 400

    # Handle optional file upload.
    image_url = None
    file = files.get("image")
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        image_url = url_for_func('api_v1.restaurant.get_uploaded_file', filename=unique_filename, _external=True)
    elif file:  # File provided but not allowed.
        return {"success": False, "message": "Invalid image file type"}, 400

    # Prepare working days as a comma-separated string.
    working_days_str = ",".join(working_days) if working_days else ""

    new_restaurant = Restaurant(
        owner_id=owner_id,
        restaurantName=restaurant_name,
        restaurantDescription=restaurant_description,
        longitude=longitude,
        latitude=latitude,
        category=category,
        workingDays=working_days_str,
        workingHoursStart=working_hours_start,
        workingHoursEnd=working_hours_end,
        listings=listings,
        ratingCount=0,
        image_url=image_url,
        pickup=pickup,
        delivery=delivery,
        maxDeliveryDistance=max_delivery_distance,
        deliveryFee=delivery_fee,
        minOrderAmount=min_order_amount
    )

    db.session.add(new_restaurant)
    db.session.commit()
    return {
        "success": True,
        "message": "Restaurant added successfully!",
        "restaurant": restaurant_to_dict(new_restaurant)
    }, 201


def get_restaurants_service(owner_id):
    """
    Retrieve all restaurants for a given owner.
    """
    restaurants = Restaurant.query.filter_by(owner_id=owner_id).all()
    if not restaurants:
        return {"message": "No restaurant found for the owner"}, 404

    serialized = []
    for restaurant in restaurants:
        serialized.append({
            "id": restaurant.id,
            "owner_id": restaurant.owner_id,
            "restaurantName": restaurant.restaurantName,
            "restaurantDescription": restaurant.restaurantDescription,
            "longitude": float(restaurant.longitude),
            "latitude": float(restaurant.latitude),
            "category": restaurant.category,
            "workingDays": restaurant.workingDays.split(",") if restaurant.workingDays else [],
            "workingHoursStart": restaurant.workingHoursStart,
            "workingHoursEnd": restaurant.workingHoursEnd,
            "listings": restaurant.listings,
            "rating": float(restaurant.rating) if restaurant.rating else None,
            "ratingCount": restaurant.ratingCount,
            "image_url": restaurant.image_url,
            "pickup": restaurant.pickup,
            "delivery": restaurant.delivery,
            "maxDeliveryDistance": restaurant.maxDeliveryDistance,
            "deliveryFee": float(restaurant.deliveryFee) if restaurant.deliveryFee else None,
            "minOrderAmount": float(restaurant.minOrderAmount) if restaurant.minOrderAmount else None
        })
    return serialized, 200


def get_restaurant_service(restaurant_id):
    """
    Retrieve a single restaurant by its ID.
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found."}, 404

    restaurant_data = {
        "id": restaurant.id,
        "owner_id": restaurant.owner_id,
        "restaurantName": restaurant.restaurantName,
        "restaurantDescription": restaurant.restaurantDescription,
        "longitude": float(restaurant.longitude),
        "latitude": float(restaurant.latitude),
        "category": restaurant.category,
        "workingDays": restaurant.workingDays.split(",") if restaurant.workingDays else [],
        "workingHoursStart": restaurant.workingHoursStart,
        "workingHoursEnd": restaurant.workingHoursEnd,
        "listings": restaurant.listings,
        "rating": float(restaurant.rating) if restaurant.rating else None,
        "ratingCount": restaurant.ratingCount,
        "image_url": restaurant.image_url,
        "pickup": restaurant.pickup,
        "delivery": restaurant.delivery,
        "maxDeliveryDistance": restaurant.maxDeliveryDistance,
        "deliveryFee": float(restaurant.deliveryFee) if restaurant.deliveryFee else None,
        "minOrderAmount": float(restaurant.minOrderAmount) if restaurant.minOrderAmount else None,
        "comments": [
            {
                "id": comment.id,
                "user_id": comment.user_id,
                "comment": comment.comment,
                "rating": float(comment.rating),
                "timestamp": comment.timestamp.isoformat()
            }
            for comment in restaurant.comments
        ]
    }
    return restaurant_data, 200



def get_restaurants_proximity_service(user_lat, user_lon, radius=10):
    """
    Retrieve restaurants based on proximity.
    """
    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
        radius = float(radius)
    except ValueError:
        return {"success": False, "message": "Invalid latitude, longitude, or radius format"}, 400

    def haversine(lat1, lon1, lat2, lon2):
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        earth_radius = 6371  # km
        return c * earth_radius

    restaurants = Restaurant.query.all()
    nearby = []
    for restaurant in restaurants:
        dist = haversine(user_lat, user_lon, float(restaurant.latitude), float(restaurant.longitude))
        if dist <= radius and (restaurant.maxDeliveryDistance is None or dist <= restaurant.maxDeliveryDistance):
            nearby.append({
                "id": restaurant.id,
                "owner_id": restaurant.owner_id,
                "restaurantName": restaurant.restaurantName,
                "restaurantDescription": restaurant.restaurantDescription,
                "longitude": float(restaurant.longitude),
                "latitude": float(restaurant.latitude),
                "category": restaurant.category,
                "workingDays": restaurant.workingDays.split(",") if restaurant.workingDays else [],
                "workingHoursStart": restaurant.workingHoursStart,
                "workingHoursEnd": restaurant.workingHoursEnd,
                "listings": restaurant.listings,
                "rating": float(restaurant.rating) if restaurant.rating else None,
                "ratingCount": restaurant.ratingCount,
                "image_url": restaurant.image_url,
                "pickup": restaurant.pickup,
                "delivery": restaurant.delivery,
                "maxDeliveryDistance": restaurant.maxDeliveryDistance,
                "deliveryFee": float(restaurant.deliveryFee) if restaurant.deliveryFee else None,
                "minOrderAmount": float(restaurant.minOrderAmount) if restaurant.minOrderAmount else None,
                "distance_km": round(dist, 2)
            })

    if not nearby:
        return {"message": "No restaurants found within the specified radius"}, 404

    nearby.sort(key=lambda x: x['distance_km'])
    return {"restaurants": nearby}, 200


def add_comment_service(restaurant_id, user_id, data):
    """
    Add a comment (and rating) for a restaurant.
    Expects data containing 'comment', 'rating', and 'purchase_id'.
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404

    comment_text = data.get("comment")
    rating = data.get("rating")
    purchase_id = data.get("purchase_id")

    if not comment_text:
        return {"success": False, "message": "Comment text is required"}, 400
    if rating is None:
        return {"success": False, "message": "Rating is required"}, 400
    if not purchase_id:
        return {"success": False, "message": "Purchase ID is required"}, 400

    # Validate purchase ownership and correspondence.
    purchase = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()
    if not purchase:
        return {"success": False, "message": "No valid purchase found for the user"}, 403

    listing = purchase.listing  # Assuming relationship exists.
    if not listing or listing.restaurant_id != restaurant_id:
        return {"success": False, "message": "Purchase does not correspond to this restaurant"}, 403

    # Prevent duplicate comments.
    if RestaurantComment.query.filter_by(purchase_id=purchase_id).first():
        return {"success": False, "message": "You have already commented on this purchase"}, 403

    try:
        rating = float(rating)
        if not (0 <= rating <= 5):
            return {"success": False, "message": "Rating must be between 0 and 5"}, 400
    except ValueError:
        return {"success": False, "message": "Invalid rating format"}, 400

    new_comment = RestaurantComment(
        restaurant_id=restaurant_id,
        user_id=user_id,
        purchase_id=purchase_id,
        comment=comment_text,
        rating=rating
    )
    db.session.add(new_comment)
    # Update restaurant rating (assuming Restaurant.update_rating exists)
    restaurant.update_rating(rating)
    db.session.commit()
    return {"success": True, "message": "Comment added successfully"}, 201

def update_restaurant_service(restaurant_id, owner_id, form, files, url_for_func):
    """
    Update an existing restaurant's details, including an optional image upload.
    :param restaurant_id: The ID of the restaurant to update
    :param owner_id: The ID of the authenticated owner
    :param form: The form data (request.form)
    :param files: The files (request.files)
    :param url_for_func: The url_for function to build URLs
    :return: Tuple (response dict, HTTP status code)
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found"}, 404

    # Check ownership
    if str(owner_id) != str(restaurant.owner_id):
        return {"success": False, "message": "You are not the owner of this restaurant."}, 403

    # Retrieve and validate form fields
    restaurant_name = form.get('restaurantName', restaurant.restaurantName)
    restaurant_description = form.get('restaurantDescription', restaurant.restaurantDescription)
    longitude = form.get('longitude', restaurant.longitude)
    latitude = form.get('latitude', restaurant.latitude)
    category = form.get('category', restaurant.category)
    working_hours_start = form.get('workingHoursStart', restaurant.workingHoursStart)
    working_hours_end = form.get('workingHoursEnd', restaurant.workingHoursEnd)
    listings = form.get('listings', restaurant.listings)
    working_days = form.getlist('workingDays')  # or keep existing if not submitted
    pickup = form.get('pickup')
    delivery = form.get('delivery')
    delivery_fee = form.get('deliveryFee', restaurant.deliveryFee)
    min_order_amount = form.get('minOrderAmount', restaurant.minOrderAmount)
    max_delivery_distance = form.get('maxDeliveryDistance', restaurant.maxDeliveryDistance)

    # Convert booleans
    if pickup is not None:
        pickup = pickup.lower() == 'true'
    if delivery is not None:
        delivery = delivery.lower() == 'true'

    # Validate required fields if needed
    if not restaurant_name:
        return {"success": False, "message": "Restaurant name is required"}, 400
    if not category:
        return {"success": False, "message": "Category is required"}, 400
    if longitude is None or latitude is None:
        return {"success": False, "message": "Longitude and latitude are required"}, 400

    # Convert numeric fields
    try:
        longitude = float(longitude)
        latitude = float(latitude)
        listings = int(listings)
        if max_delivery_distance is not None:
            max_delivery_distance = float(max_delivery_distance)
        if delivery_fee is not None:
            delivery_fee = float(delivery_fee)
        if min_order_amount is not None:
            min_order_amount = float(min_order_amount)
    except ValueError:
        return {"success": False, "message": "Invalid format for numeric fields"}, 400

    # Handle optional file upload
    file = files.get("image")
    if file and allowed_file(file.filename):
        # Remove old file if any
        if restaurant.image_url:
            try:
                old_filename = restaurant.image_url.split('/')[-1]
                old_filepath = os.path.join(UPLOAD_FOLDER, old_filename)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            except Exception as e:
                print(f"Failed to delete old image file: {e}")

        # Save the new file
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        image_url = url_for_func('api_v1.restaurant.get_uploaded_file', filename=unique_filename, _external=True)
        restaurant.image_url = image_url
    elif file:  # File provided but not allowed
        return {"success": False, "message": "Invalid image file type"}, 400

    # Update workingDays if provided
    if working_days:
        working_days_str = ",".join(working_days)
        restaurant.workingDays = working_days_str

    # Assign updated fields
    restaurant.restaurantName = restaurant_name
    restaurant.restaurantDescription = restaurant_description
    restaurant.longitude = longitude
    restaurant.latitude = latitude
    restaurant.category = category
    restaurant.workingHoursStart = working_hours_start
    restaurant.workingHoursEnd = working_hours_end
    restaurant.listings = listings
    if pickup is not None:
        restaurant.pickup = pickup
    if delivery is not None:
        restaurant.delivery = delivery
    restaurant.maxDeliveryDistance = max_delivery_distance
    restaurant.deliveryFee = delivery_fee
    restaurant.minOrderAmount = min_order_amount

    # Commit changes
    db.session.commit()
    return {
        "success": True,
        "message": "Restaurant updated successfully!",
        "restaurant": restaurant_to_dict(restaurant)
    }, 200

def delete_restaurant_service(restaurant_id, owner_id):
    """
    Delete a restaurant by its ID if it is owned by the specified owner.
    Delegates to the Restaurant model's class method.
    """
    return Restaurant.delete_restaurant_service(restaurant_id, owner_id)