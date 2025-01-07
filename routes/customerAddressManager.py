from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CustomerAddress

customerAddressManager_bp = Blueprint("customerAddressManager", __name__)

## todo update swgger with is_primary
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
        existing_addresses = CustomerAddress.query.filter_by(user_id=user_id).first()
        is_first_address = existing_addresses is None

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
            is_primary=is_first_address  # True only if it's the first address
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
        "doorNo": address.doorNo,
        "is_primary": address.is_primary

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
@customerAddressManager_bp.route("/update_customer_address/<int:id>", methods=["PUT"])
@jwt_required()
def update_customer_address(id):
    try:
        user_id = get_jwt_identity()
        address = CustomerAddress.query.filter_by(id=id, user_id=user_id).first()

        if not address:
            return jsonify({"message": "Address not found or does not belong to the user"}), 404

        # Get data from request
        data = request.get_json()

        # Update fields if provided
        address.title = data.get('title', address.title)
        address.longitude = data.get('longitude', address.longitude)
        address.latitude = data.get('latitude', address.latitude)
        address.street = data.get('street', address.street)
        address.neighborhood = data.get('neighborhood', address.neighborhood)
        address.district = data.get('district', address.district)
        address.province = data.get('province', address.province)
        address.country = data.get('country', address.country)
        address.postalCode = data.get('postalCode', address.postalCode)
        address.apartmentNo = data.get('apartmentNo', address.apartmentNo)
        address.doorNo = data.get('doorNo', address.doorNo)

        # Handle is_primary logic
        is_primary = data.get("is_primary", None)
        if is_primary is not None:
            if is_primary:  # If this address is being set as primary
                # Unset is_primary for all other addresses for this user
                CustomerAddress.query.filter_by(user_id=user_id).update({"is_primary": False})
                address.is_primary = True
            else:
                # If is_primary is explicitly set to False, just update this address
                address.is_primary = False

        db.session.commit()
        # Serialize updated address
        serialized_address = address.to_dict()

        return jsonify({
            "success": True,
            "message": "Address updated successfully!",
            "address": serialized_address
        }), 200

    except Exception as e:
        # Log unexpected errors
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the address.",
            "error": str(e)
        }), 500
