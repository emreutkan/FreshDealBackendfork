from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Restaurant, User

restaurantManager_bp = Blueprint("restaurantManager", __name__)

@restaurantManager_bp.route("/add_restaurant", methods=["POST"])
@jwt_required()
def add_restaurant():
    try:
        data = request.get_json()
        owner_id = get_jwt_identity()
        restaurantName = data.get('restaurantName')
        restaurantDescription = data.get('restaurantDescription')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        category = data.get('category')
        workingDays = data.get('workingDays')
        workingHoursStart = data.get('workingHoursStart')
        workingHoursEnd = data.get('workingHoursEnd')
        listings = data.get('listings')

        owner = User.query.get(owner_id)
        if not owner:
            print("Validation error: Owner not found.")
            return jsonify({"success": False, "message": "Owner not found"}), 404
        elif owner.role != "owner":
            print("Validation error: A restaurant was attempted to be added by someone who is not an owner.")
            return jsonify({"success": False, "message": "Only owners can add a restaurant"}), 400

        workingDaysStr = ""
        if workingDays:
            workingDaysStr = ",".join(workingDays)

        if not restaurantName:
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
            restaurantName=restaurantName,
            restaurantDescription=restaurantDescription,
            longitude=longitude,
            latitude=latitude,
            category=category,
            workingDays=workingDaysStr,
            workingHoursStart=workingHoursStart,
            workingHoursEnd=workingHoursEnd,
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