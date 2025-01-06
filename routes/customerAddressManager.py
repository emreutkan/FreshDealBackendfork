from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CustomerAddress

customerAddressManager_bp = Blueprint("customerAddressManager", __name__)

## todo update swgger with is_primary@customerAddressManager_bp.route("/add_customer_address", methods=["POST"])
@jwt_required()
def add_customer_address():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Extract fields from the request
        title = data.get('title')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        street = data.get('street')
        neighborhood = data.get('neighborhood')
        district = data.get('district')
        province = data.get('province')
        country = data.get('country')
        postalCode = data.get('postalCode')
        apartmentNo = data.get('apartmentNo')
        doorNo = data.get('doorNo')

        # Validation
        if not title:
            return jsonify({"success": False, "message": "Title is required"}), 400

        if longitude is None or latitude is None:
            return jsonify({"success": False, "message": "Longitude and latitude are required"}), 400

        if not street:
            return jsonify({"success": False, "message": "Street is required"}), 400

        if not district:
            return jsonify({"success": False, "message": "District is required"}), 400

        if not province:
            return jsonify({"success": False, "message": "Province is required"}), 400

        if not country:
            return jsonify({"success": False, "message": "Country is required"}), 400

        if not postalCode:
            return jsonify({"success": False, "message": "Postal Code is required"}), 400

        # Set all other addresses to is_primary = False
        CustomerAddress.query.filter_by(user_id=user_id).update({"is_primary": False})

        # Create new address with is_primary = True
        new_address = CustomerAddress(
            user_id=user_id,
            title=title,
            longitude=longitude,
            latitude=latitude,
            street=street,
            neighborhood=neighborhood,
            district=district,
            province=province,
            country=country,
            postalCode=postalCode,
            apartmentNo=apartmentNo,
            doorNo=doorNo,
            is_primary=True  # Default to True for new address
        )
        db.session.add(new_address)
        db.session.commit()

        # Serialize the new_address object
        serialized_address = new_address.to_dict()

        return jsonify({
            "success": True,
            "message": "New customer address is successfully added!",
            "address": serialized_address
        }), 201

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while adding the address.",
            "error": str(e)
        }), 500

@customerAddressManager_bp.route("/get_customer_address", methods=["GET"])
@jwt_required()
def get_customer_address():
    user_id = get_jwt_identity()
    addresses = CustomerAddress.query.filter_by(user_id=user_id).all()

    if not addresses:
        return jsonify({"message": "No address found for the user"}), 404

    serialized_address = []
    for address in addresses:
        serialized_address.append({
        "id": address.id,
        "title": address.title,
        "longitude": address.longitude,
        "latitude": address.latitude,
        "street": address.street,
        "neighborhood": address.neighborhood,
        "district": address.district,
        "province": address.province,
        "country": address.country,
        "postalCode": address.postalCode,
        "apartmentNo": address.apartmentNo,
        "doorNo": address.doorNo
        })
        return jsonify(serialized_address), 200

@customerAddressManager_bp.route("/delete_customer_address/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_customer_address(id):
    user_id = get_jwt_identity()
    
    address = CustomerAddress.query.filter_by(id=id, user_id=user_id).first()

    if not address:
        return jsonify({"message": "Address not found"}), 404

    db.session.delete(address)
    db.session.commit()

    return jsonify({"message": "Address successfully deleted!"}), 200


## todo add to swagger
@customerAddressManager_bp.route("/add_customer_address", methods=["POST"])
@jwt_required()
def add_customer_address():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Extract fields from the request
        title = data.get('title')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        street = data.get('street')
        neighborhood = data.get('neighborhood')
        district = data.get('district')
        province = data.get('province')
        country = data.get('country')
        postalCode = data.get('postalCode')
        apartmentNo = data.get('apartmentNo')
        doorNo = data.get('doorNo')
        is_primary = data.get('is_primary', False)  # Default to False if not provided

        # Validation
        if not title:
            print("Validation error: Title is missing.")
            return jsonify({"success": False, "message": "Title is required"}), 400

        if longitude is None or latitude is None:
            print("Validation error: Longitude or Latitude is missing.")
            return jsonify({"success": False, "message": "Longitude and latitude are required"}), 400

        if not street:
            print("Validation error: Street is missing.")
            return jsonify({"success": False, "message": "Street is required"}), 400

        if not district:
            print("Validation error: District is missing.")
            return jsonify({"success": False, "message": "District is required"}), 400

        if not province:
            print("Validation error: Province is missing.")
            return jsonify({"success": False, "message": "Province is required"}), 400

        if not country:
            print("Validation error: Country is missing.")
            return jsonify({"success": False, "message": "Country is required"}), 400

        if not postalCode:
            print("Validation error: Postal Code is missing.")
            return jsonify({"success": False, "message": "Postal Code is required"}), 400

        # If is_primary is True, unset is_primary for all other addresses for this user
        if is_primary:
            CustomerAddress.query.filter_by(user_id=user_id).update({"is_primary": False})

        # If no existing primary address, set this address as primary
        if not is_primary:
            existing_primary = CustomerAddress.query.filter_by(user_id=user_id, is_primary=True).first()
            if not existing_primary:
                is_primary = True

        # Create new address
        new_address = CustomerAddress(
            user_id=user_id,
            title=title,
            longitude=longitude,
            latitude=latitude,
            street=street,
            neighborhood=neighborhood,
            district=district,
            province=province,
            country=country,
            postalCode=postalCode,
            apartmentNo=apartmentNo,
            doorNo=doorNo,
            is_primary=is_primary
        )
        db.session.add(new_address)
        db.session.commit()

        # Serialize the new_address object
        serialized_address = new_address.to_dict()

        return jsonify({
            "success": True,
            "message": "New customer address is successfully added!",
            "address": serialized_address
        }), 201

    except Exception as e:
        # Log any unexpected exceptions
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while adding the address.",
            "error": str(e)
        }), 500
