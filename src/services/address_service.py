# services/address_service.py

from src.models import db, CustomerAddress

def create_address(user_id, data):
    # Extract fields from the request data
    title = data.get('title')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    street = data.get('street')
    neighborhood = data.get('neighborhood')
    district = data.get('district')
    province = data.get('province')
    country = data.get('country')
    postal_code = data.get('postalCode')
    apartment_no = data.get('apartmentNo')
    door_no = data.get('doorNo')
    is_primary = data.get('is_primary')

    # Validation
    if not title:
        return {"success": False, "message": "Title is required"}, 400

    if longitude is None or latitude is None:
        return {"success": False, "message": "Longitude and latitude are required"}, 400

    if not street:
        return {"success": False, "message": "Street is required"}, 400

    if not district:
        return {"success": False, "message": "District is required"}, 400

    if not province:
        return {"success": False, "message": "Province is required"}, 400

    if not country:
        return {"success": False, "message": "Country is required"}, 400

    if not postal_code:
        return {"success": False, "message": "Postal Code is required"}, 400

    # Check if this is the user's first address
    existing_address = CustomerAddress.query.filter_by(user_id=user_id).first()
    is_first_address = existing_address is None

    # Set all other addresses to non-primary

    # Create a new address
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
        postalCode=postal_code,
        apartmentNo=apartment_no,
        doorNo=door_no,
        is_primary=is_first_address or is_primary
    )

    if is_first_address or is_primary:
        db.session.query(CustomerAddress).filter_by(user_id=user_id).update({"is_primary": False})

    db.session.add(new_address)
    db.session.commit()

    return {
        "success": True,
        "message": "Address created successfully!",
        "address": new_address.to_dict()
    }, 201


def list_addresses(user_id):
    addresses = CustomerAddress.query.filter_by(user_id=user_id).all()

    if not addresses:
        return {"message": "No addresses found for the user"}, 404

    serialized_addresses = [address.to_dict() for address in addresses]
    return serialized_addresses, 200


def get_address(user_id, address_id):
    address = CustomerAddress.query.filter_by(id=address_id, user_id=user_id).first()

    if not address:
        return {"message": "Address not found"}, 404

    return address.to_dict(), 200


def update_address(user_id, address_id, data):
    address = CustomerAddress.query.filter_by(id=address_id, user_id=user_id).first()

    if not address:
        return {"message": "Address not found or does not belong to the user"}, 404

    # Update fields if provided; otherwise, keep the existing values
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

    if "latitude" in data or "longitude" in data:
        # You can either ignore these changes silently or return an error.
        # For this example, let's log the attempt:
        print("Attempt to update read-only fields: latitude and longitude. Ignoring these changes.")

    # Update primary address logic if provided
    is_primary = data.get("is_primary", None)
    if is_primary is not None:
        if is_primary:  # If setting this address as primary, unset all others first
            db.session.query(CustomerAddress).filter_by(user_id=user_id).update({"is_primary": False})
            address.is_primary = True
        else:
            address.is_primary = False

    db.session.commit()

    return {
        "success": True,
        "message": "Address updated successfully!",
        "address": address.to_dict()
    }, 200


def delete_address(user_id, address_id):
    address = CustomerAddress.query.filter_by(id=address_id, user_id=user_id).first()
    next_address = None

    if not address:
        return {"message": "Address not found"}, 404

    # Check if we're deleting a primary address
    if address.is_primary:
        # Find the next available address (excluding the one being deleted)
        next_address = CustomerAddress.query.filter(
            CustomerAddress.user_id == user_id,
            CustomerAddress.id != address_id
        ).first()

        if next_address:
            next_address.is_primary = True
            db.session.add(next_address)  # Explicitly add the modified address

    # Delete the address
    db.session.delete(address)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": f"Failed to delete address: {str(e)}"
        }, 500

    return {
        "success": True,
        "message": "Address deleted successfully!",
        "new_primary_address_id": next_address.id if next_address else None
    }, 200
