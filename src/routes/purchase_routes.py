from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.services.purchase_service import (
    create_purchase_order_service,
    handle_restaurant_response_service,
    add_completion_image_service,
    get_restaurant_purchases_service
)

purchase_bp = Blueprint("purchase", __name__)

@purchase_bp.route("/purchase", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Create a new purchase order",
    "description": (
        "Creates a pending purchase order from items in the user's cart. "
        "Any delivery information (if provided) will be merged with the user's global (default) address."
    ),
    "security": [{"BearerAuth": []}],
    "requestBody": {
        "required": False,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        # You can add additional purchase fields here if needed.
                        "delivery_info": {
                            "type": "object",
                            "description": (
                                "Optional extra delivery info. "
                                "The global default address will automatically be used. "
                                "You may send additional notes here."
                            ),
                            "properties": {
                                "notes": {
                                    "type": "string",
                                    "description": "Additional delivery notes"
                                }
                                # Intentionally omitting an address field as that is fetched globally.
                            }
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "Optional extra purchase-related data."
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "201": {
            "description": "Purchase order created successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "purchases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "purchase_id": {"type": "integer"},
                                        "listing_id": {"type": "integer"},
                                        "quantity": {"type": "integer"},
                                        "total_price": {"type": "string"},
                                        "status": {
                                            "type": "string",
                                            "enum": ["pending", "accepted", "rejected", "completed"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "400": {"description": "Bad request - Cart is empty or global address not found"},
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "500": {"description": "Internal server error"}
    }
})
def create_purchase_order():
    user_id = get_jwt_identity()

    # You still allow a request body so that additional information can be submitted.
    # However, the delivery address will be automatically retrieved from the global address.
    data = request.get_json() or {}
    # Depending on your implementation, you can either:
    # 1. Merge any optional request delivery_info with the default global address; or
    # 2. Simply ignore the request delivery_info and fetch the global one.
    #
    # This example sends along the data to the service, which is expected to retrieve and merge
    # the default delivery address as needed.
    response, status = create_purchase_order_service(user_id, data)
    return jsonify(response), status

@purchase_bp.route("/purchase/<int:purchase_id>/response", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Restaurant response to purchase order",
    "description": "Allow restaurant to accept or reject a pending purchase order",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "purchase_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the purchase order"
        }
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["accept", "reject"],
                            "description": "Action to take on the purchase order"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "200": {
            "description": "Successfully processed restaurant response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "purchase_id": {"type": "integer"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "accepted", "rejected", "completed"]
                            }
                        }
                    }
                }
            }
        },
        "403": {"description": "Unauthorized - Restaurant doesn't own this listing"},
        "404": {"description": "Purchase order not found"},
        "500": {"description": "Internal server error"}
    }
})
def restaurant_response(purchase_id):
    restaurant_id = get_jwt_identity()
    action = request.json.get('action')
    response, status = handle_restaurant_response_service(
        purchase_id,
        restaurant_id,
        action
    )
    return jsonify(response), status

@purchase_bp.route("/purchase/<int:purchase_id>/completion-image", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Add completion image to purchase",
    "description": "Allow restaurant to add a completion image to an accepted purchase",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "purchase_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the purchase order"
        }
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["image_url"],
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the uploaded completion image"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "200": {
            "description": "Successfully added completion image",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "purchase_id": {"type": "integer"},
                            "image_url": {"type": "string"}
                        }
                    }
                }
            }
        },
        "400": {"description": "Purchase must be in accepted state"},
        "403": {"description": "Unauthorized - Restaurant doesn't own this listing"},
        "404": {"description": "Purchase order not found"},
        "500": {"description": "Internal server error"}
    }
})
def add_completion_image(purchase_id):
    restaurant_id = get_jwt_identity()
    image_url = request.json.get('image_url')
    response, status = add_completion_image_service(
        purchase_id,
        restaurant_id,
        image_url
    )
    return jsonify(response), status

@purchase_bp.route("/restaurant/<int:restaurant_id>/purchases", methods=["GET"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Get restaurant purchases",
    "description": "Retrieve all purchases for a specific restaurant",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "restaurant_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the restaurant"
        }
    ],
    "responses": {
        "200": {
            "description": "List of purchases retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "purchases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "user_id": {"type": "integer"},
                                        "listing_id": {"type": "integer"},
                                        "listing_title": {"type": "string"},
                                        "quantity": {"type": "integer"},
                                        "total_price": {"type": "string"},
                                        "purchase_date": {"type": "string", "format": "date-time"},
                                        "status": {
                                            "type": "string",
                                            "enum": ["pending", "accepted", "rejected", "completed"]
                                        },
                                        "is_delivery": {"type": "boolean"},
                                        "delivery_address": {"type": "string"},
                                        "delivery_notes": {"type": "string"},
                                        "completion_image_url": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "403": {"description": "Forbidden - User is not authorized to view these purchases"},
        "500": {"description": "Internal server error"}
    }
})
def get_restaurant_purchases(restaurant_id):
    """Get all purchases for a restaurant"""
    response, status = get_restaurant_purchases_service(restaurant_id)
    return jsonify(response), status

@purchase_bp.route("/purchases/<int:purchase_id>/accept", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Accept purchase order",
    "description": "Restaurant owner accepts a pending purchase order",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "purchase_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the purchase order"
        }
    ],
    "responses": {
        "200": {
            "description": "Purchase successfully accepted",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "purchase_id": {"type": "integer"},
                            "status": {
                                "type": "string",
                                "enum": ["accepted"]
                            }
                        }
                    }
                }
            }
        },
        "400": {"description": "Purchase cannot be accepted (wrong state)"},
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "403": {"description": "Forbidden - User is not the restaurant owner"},
        "404": {"description": "Purchase not found"},
        "500": {"description": "Internal server error"}
    }
})
def accept_purchase(purchase_id):
    """Accept a purchase order"""
    restaurant_id = get_jwt_identity()
    response, status = handle_restaurant_response_service(purchase_id, restaurant_id, 'accept')
    return jsonify(response), status

@purchase_bp.route("/purchases/<int:purchase_id>/reject", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Reject purchase order",
    "description": "Restaurant owner rejects a pending purchase order",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "purchase_id",
            "in": "path",
            "schema": {"type": "integer"},
            "required": True,
            "description": "ID of the purchase order"
        }
    ],
    "responses": {
        "200": {
            "description": "Purchase successfully rejected",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "purchase_id": {"type": "integer"},
                            "status": {
                                "type": "string",
                                "enum": ["rejected"]
                            }
                        }
                    }
                }
            }
        },
        "400": {"description": "Purchase cannot be rejected (wrong state)"},
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "403": {"description": "Forbidden - User is not the restaurant owner"},
        "404": {"description": "Purchase not found"},
        "500": {"description": "Internal server error"}
    }
})
def reject_purchase(purchase_id):
    """Reject a purchase order"""
    restaurant_id = get_jwt_identity()
    response, status = handle_restaurant_response_service(purchase_id, restaurant_id, 'reject')
    return jsonify(response), status
