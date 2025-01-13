# routes/addresses.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.address_service import (
    create_address as create_address_service,
    list_addresses as list_addresses_service,
    get_address as get_address_service,
    update_address as update_address_service,
    delete_address as delete_address_service,
)

addresses_bp = Blueprint("addresses", __name__)


@addresses_bp.route("/addresses", methods=["POST"])
@jwt_required()
def create_address():
    """
    Create a new address
    ---
    tags:
      - Addresses
    security:
      - jwt: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
              - longitude
              - latitude
              - street
              - district
              - province
              - country
              - postalCode
            properties:
              title:
                type: string
              longitude:
                type: number
                format: float
              latitude:
                type: number
                format: float
              street:
                type: string
              neighborhood:
                type: string
              district:
                type: string
              province:
                type: string
              country:
                type: string
              postalCode:
                type: string
              apartmentNo:
                type: string
              doorNo:
                type: string
    responses:
      201:
        description: Address created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                address:
                  type: object
      400:
        description: Validation error
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        response, status = create_address_service(user_id, data)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the address.",
            "error": str(e)
        }), 500


@addresses_bp.route("/addresses", methods=["GET"])
@jwt_required()
def list_addresses():
    """
    Retrieve a list of addresses for the current user
    ---
    tags:
      - Addresses
    security:
      - jwt: []
    responses:
      200:
        description: A list of addresses
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
      404:
        description: No addresses found for the user
    """
    try:
        user_id = get_jwt_identity()
        response, status = list_addresses_service(user_id)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "message": "An error occurred while fetching addresses.",
            "error": str(e)
        }), 500


@addresses_bp.route("/addresses/<int:address_id>", methods=["GET"])
@jwt_required()
def get_address(address_id):
    """
    Retrieve a specific address by its ID
    ---
    tags:
      - Addresses
    security:
      - jwt: []
    parameters:
      - name: address_id
        in: path
        description: ID of the address to retrieve
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Address details
        content:
          application/json:
            schema:
              type: object
      404:
        description: Address not found
    """
    try:
        user_id = get_jwt_identity()
        response, status = get_address_service(user_id, address_id)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "message": "An error occurred while fetching the address.",
            "error": str(e)
        }), 500


@addresses_bp.route("/addresses/<int:address_id>", methods=["PUT"])
@jwt_required()
def update_address(address_id):
    """
    Update an existing address
    ---
    tags:
      - Addresses
    security:
      - jwt: []
    parameters:
      - name: address_id
        in: path
        description: ID of the address to update
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
              # Note: latitude and longitude will be ignored if provided.
              street:
                type: string
              neighborhood:
                type: string
              district:
                type: string
              province:
                type: string
              country:
                type: string
              postalCode:
                type: string
              apartmentNo:
                type: string
              doorNo:
                type: string
              is_primary:
                type: boolean
    responses:
      200:
        description: Address updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                address:
                  type: object
      404:
        description: Address not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        response, status = update_address_service(user_id, address_id, data)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "message": "An error occurred while updating the address.",
            "error": str(e)
        }), 500


@addresses_bp.route("/addresses/<int:address_id>", methods=["DELETE"])
@jwt_required()
def delete_address(address_id):
    """
    Delete an address
    ---
    tags:
      - Addresses
    security:
      - jwt: []
    parameters:
      - name: address_id
        in: path
        description: ID of the address to delete
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Address successfully deleted
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Address not found
    """
    try:
        user_id = get_jwt_identity()
        response, status = delete_address_service(user_id, address_id)
        return jsonify(response), status
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({
            "message": "An error occurred while deleting the address.",
            "error": str(e)
        }), 500
