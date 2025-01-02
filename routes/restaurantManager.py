from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Restaurant, User
from math import radians, cos, sin, asin, sqrt

restaurantManager_bp = Blueprint("restaurantManager", __name__)

@restaurantManager_bp.route("/add_restaurant", methods=["POST"])
@jwt_required()
def add_restaurant():
    try:
        data = request.get_json()
        owner_id = get_jwt_identity()
        restaurant_name = data.get('restaurantName')
        restaurant_description = data.get('restaurantDescription')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        category = data.get('category')
        working_days = data.get('workingDays')
        working_hours_start = data.get('workingHoursStart')
        working_hours_end = data.get('workingHoursEnd')
        listings = data.get('listings')

        owner = User.query.get(owner_id)
        if not owner:
            print("Validation error: Owner not found.")
            return jsonify({"success": False, "message": "Owner not found"}), 404
        elif owner.role != "owner":
            print("Validation error: A restaurant was attempted to be added by someone who is not an owner.")
            return jsonify({"success": False, "message": "Only owners can add a restaurant"}), 400

        working_days_str = ""
        if working_days:
            working_days_str = ",".join(working_days)

        if not restaurant_name:
            print("Validation error: Restaurant name is missing.")
            return jsonify({"success": False, "message": "Restaurant name is required"}), 400

        if not category:
            print("Validation error: Category name is missing.")
            return jsonify({"success": False, "message": "Category is required"}), 400

        if not listings:
            print("Validation error: Listings name is missing.")
            return jsonify({"success": False, "message": "Listings is required"}), 400

        if longitude is None or latitude is None:
            print("Validation error: Longitude or Latitude is missing.")
            return jsonify({"success": False, "message": "Longitude and latitude are required"}), 400

        new_address = Restaurant(
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
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({"message": "New restaurant is successfully added!"}), 201
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurantManager_bp.route("/get_restaurant/<int:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            print(f"Validation error: Restaurant with ID {restaurant_id} not found.")
            return jsonify({"success": False, "message": f"Restaurant with ID {restaurant_id} not found."}), 404

        restaurant_data = {
            "id": restaurant.id,
            "owner_id": restaurant.owner_id,
            "restaurantName": restaurant.restaurantName,
            "restaurantDescription": restaurant.restaurantDescription,
            "longitude": restaurant.longitude,
            "latitude": restaurant.latitude,
            "category": restaurant.category,
            "workingDays": restaurant.workingDays.split(","),
            "workingHoursStart": restaurant.workingHoursStart,
            "workingHoursEnd": restaurant.workingHoursEnd,
            "listings": restaurant.listings,
            "rating": restaurant.rating,
            "ratingCount": restaurant.ratingCount
        }

        return jsonify(restaurant_data), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurantManager_bp.route("/get_restaurants", methods=["GET"])
@jwt_required()
def get_restaurants():
    try:
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)
        if not owner:
            print("Validation error: Owner not found.")
            return jsonify({"success": False, "message": "Owner not found"}), 404
        elif owner.role != "owner":
            print("Validation error: Only users with owner role can own a restaurant.")
            return jsonify({"success": False, "message": "Only users with owner role can own a restaurant"}), 400

        restaurants = Restaurant.query.filter_by(owner_id=owner_id).all()

        if not restaurants:
            return jsonify({"message": "No restaurant found for the owner"}), 404

        serialized_restaurant = []
        for restaurant in restaurants:
            serialized_restaurant.append({
                "id": restaurant.id,
                "owner_id": restaurant.owner_id,
                "restaurantName": restaurant.restaurantName,
                "restaurantDescription": restaurant.restaurantDescription,
                "longitude": restaurant.longitude,
                "latitude": restaurant.latitude,
                "category": restaurant.category,
                "workingDays": restaurant.workingDays.split(","),
                "workingHoursStart": restaurant.workingHoursStart,
                "workingHoursEnd": restaurant.workingHoursEnd,
                "listings": restaurant.listings,
                "rating": restaurant.rating,
                "ratingCount": restaurant.ratingCount
            })
        return jsonify(serialized_restaurant), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500


@restaurantManager_bp.route("/delete_restaurant/<int:restaurant_id>", methods=["DELETE"])
@jwt_required()
def delete_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            print(f"Validation error: Restaurant with ID {restaurant_id} not found.")
            return jsonify({"success": False, "message": f"Restaurant with ID {restaurant_id} not found."}), 404

        owner_id = get_jwt_identity()
        if str(owner_id) != str(restaurant.owner_id):
            print(str(owner_id)+" "+str(restaurant.owner_id))
            print("A restaurant was attempted to be deleted by someone who is not the owner")
            return jsonify({"success": False, "message": "You are not the owner of this restaurant."}), 404

        db.session.delete(restaurant)
        db.session.commit()

        return jsonify({"success": True, "message": f"Restaurant with ID {restaurant_id} successfully deleted."}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500

@restaurantManager_bp.route("/get_restaurants_proximity", methods=["POST"])
@jwt_required()  # Optional: Remove if not requiring authentication
def get_restaurants_proximity():
    try:
        data = request.get_json()
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        radius = data.get('radius', 10)  # Default radius is 10 km

        # Validate input
        if user_lat is None or user_lon is None:
            print("Validation error: Latitude or Longitude is missing.")
            return jsonify({"success": False, "message": "Latitude and longitude are required"}), 400

        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            radius = float(radius)
        except ValueError:
            print("Validation error: Invalid latitude, longitude, or radius format.")
            return jsonify({"success": False, "message": "Invalid latitude, longitude, or radius format"}), 400

        # Haversine formula to calculate distance between two points on the Earth
        def haversine(lat1, lon1, lat2, lon2):
            # convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

            # haversine formula
            d_lon = lon2 - lon1
            d_lat = lat2 - lat1
            a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r

        # Fetch all restaurants (you can optimize this by fetching only those within a bounding box)
        restaurants = Restaurant.query.all()

        nearby_restaurants = []
        for restaurant in restaurants:
            distance = haversine(user_lat, user_lon, restaurant.latitude, restaurant.longitude)
            if distance <= radius:
                nearby_restaurants.append({
                    "id": restaurant.id,
                    "owner_id": restaurant.owner_id,
                    "restaurantName": restaurant.restaurantName,
                    "restaurantDescription": restaurant.restaurantDescription,
                    "longitude": restaurant.longitude,
                    "latitude": restaurant.latitude,
                    "category": restaurant.category,
                    "workingDays": restaurant.workingDays.split(","),
                    "workingHoursStart": restaurant.workingHoursStart,
                    "workingHoursEnd": restaurant.workingHoursEnd,
                    "listings": restaurant.listings,
                    "rating": restaurant.rating,
                    "ratingCount": restaurant.ratingCount,
                    "distance_km": round(distance, 2)
                })

        if not nearby_restaurants:
            return jsonify({"message": "No restaurants found within the specified radius"}), 404

        # Optionally, sort the restaurants by distance
        nearby_restaurants.sort(key=lambda x: x['distance_km'])

        return jsonify({"restaurants": nearby_restaurants}), 200

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
