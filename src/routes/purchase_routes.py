from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.services.purchase_service import (
    create_purchase_order_service,
    handle_restaurant_response_service,
    add_completion_image_service,
    get_restaurant_purchases_service, get_order_details_service, get_user_previous_orders_service,
    get_user_active_orders_service
)

purchase_bp = Blueprint("purchase", __name__)
@purchase_bp.route("/purchase", methods=["POST"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Create a new purchase order from cart items",
    "description": "Creates purchase orders for all items in the user's cart. Supports both pickup and delivery orders.",
    "security": [{"BearerAuth": []}],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["is_delivery"],
                    "properties": {
                        "is_delivery": {
                            "type": "boolean",
                            "description": "Flag to indicate if this is a delivery order",
                            "default": False,
                            "example": False
                        },
                        "pickup_notes": {
                            "type": "string",
                            "description": "Optional notes for pickup orders",
                            "example": "Will pick up at 6pm"
                        },
                        "delivery_address": {
                            "type": "string",
                            "description": "Required only when is_delivery is true",
                            "example": "123 Main St, City"
                        },
                        "delivery_notes": {
                            "type": "string",
                            "description": "Optional notes for delivery orders",
                            "example": "Please leave at door"
                        }
                    }
                },
                "examples": {
                    "pickup_order": {
                        "summary": "Pickup Order Example",
                        "value": {
                            "is_delivery": False,
                            "pickup_notes": "Will pick up at 6pm"
                        }
                    },
                    "delivery_order": {
                        "summary": "Delivery Order Example",
                        "value": {
                            "is_delivery": True,
                            "delivery_address": "123 Main St, City",
                            "delivery_notes": "Please leave at door"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "201": {
            "description": "Purchase orders created successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "Purchase order created successfully, waiting for restaurant approval"
                            },
                            "purchases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "integer",
                                            "example": 1
                                        },
                                        "listing_id": {
                                            "type": "integer",
                                            "example": 1
                                        },
                                        "quantity": {
                                            "type": "integer",
                                            "example": 2
                                        },
                                        "total_price": {
                                            "type": "string",
                                            "example": "25.99"
                                        },
                                        "status": {
                                            "type": "string",
                                            "enum": ["PENDING", "ACCEPTED", "REJECTED", "COMPLETED"],
                                            "example": "PENDING"
                                        },
                                        "is_delivery": {
                                            "type": "boolean",
                                            "example": False
                                        },
                                        "order_notes": {
                                            "type": "string",
                                            "example": "Will pick up at 6pm"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "Cart is empty or delivery address required for delivery orders"
                            }
                        }
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "msg": {
                                "type": "string",
                                "example": "Missing authorization header"
                            }
                        }
                    }
                }
            }
        },
        "500": {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "An error occurred"
                            },
                            "error": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }
    }
})
def create_purchase_order():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
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

@purchase_bp.route("/user/orders/active", methods=["GET"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Get user's active orders",
    "description": "Retrieve all active (pending and accepted) orders for the current user",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Active orders retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "active_orders": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "purchase_id": {"type": "integer"},
                                        "restaurant_name": {"type": "string"},
                                        "listing_title": {"type": "string"},
                                        "quantity": {"type": "integer"},
                                        "total_price": {"type": "string"},
                                        "formatted_total_price": {"type": "string"},
                                        "status": {
                                            "type": "string",
                                            "enum": ["PENDING", "ACCEPTED"]
                                        },
                                        "purchase_date": {"type": "string", "format": "date-time"},
                                        "is_active": {"type": "boolean"},
                                        "is_delivery": {"type": "boolean"},
                                        "delivery_address": {"type": "string"},
                                        "delivery_notes": {"type": "string"},
                                        "restaurant_details": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "image_url": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "500": {"description": "Internal server error"}
    }
})
def get_user_active_orders():
    """Get current user's active orders"""
    user_id = get_jwt_identity()
    response, status = get_user_active_orders_service(user_id)
    return jsonify(response), status

@purchase_bp.route("/user/orders/previous", methods=["GET"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Get user's previous orders",
    "description": "Retrieve completed or rejected orders for the current user with pagination",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "schema": {"type": "integer", "default": 1},
            "required": False,
            "description": "Page number for pagination"
        },
        {
            "name": "per_page",
            "in": "query",
            "schema": {"type": "integer", "default": 10},
            "required": False,
            "description": "Number of items per page"
        }
    ],
    "responses": {
        "200": {
            "description": "Previous orders retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "orders": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "listing_title": {"type": "string"},
                                        "quantity": {"type": "integer"},
                                        "total_price": {"type": "string"},
                                        "formatted_total_price": {"type": "string"},
                                        "status": {
                                            "type": "string",
                                            "enum": ["COMPLETED", "REJECTED"]
                                        },
                                        "purchase_date": {"type": "string", "format": "date-time"},
                                        "is_delivery": {"type": "boolean"},
                                        "delivery_address": {"type": "string"},
                                        "delivery_notes": {"type": "string"},
                                        "completion_image_url": {"type": "string"}
                                    }
                                }
                            },
                            "pagination": {
                                "type": "object",
                                "properties": {
                                    "current_page": {"type": "integer"},
                                    "total_pages": {"type": "integer"},
                                    "per_page": {"type": "integer"},
                                    "total_orders": {"type": "integer"},
                                    "has_next": {"type": "boolean"},
                                    "has_prev": {"type": "boolean"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "500": {"description": "Internal server error"}
    }
})
def get_user_previous_orders():
    """Get current user's previous orders"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    response, status = get_user_previous_orders_service(user_id, page, per_page)
    return jsonify(response), status

@purchase_bp.route("/user/orders/<int:purchase_id>", methods=["GET"])
@jwt_required()
@swag_from({
    "tags": ["Purchases"],
    "summary": "Get order details",
    "description": "Get detailed information about a specific order",
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
            "description": "Order details retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "order": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "listing_title": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "total_price": {"type": "string"},
                                    "formatted_total_price": {"type": "string"},
                                    "status": {
                                        "type": "string",
                                        "enum": ["PENDING", "ACCEPTED", "REJECTED", "COMPLETED"]
                                    },
                                    "purchase_date": {"type": "string", "format": "date-time"},
                                    "is_active": {"type": "boolean"},
                                    "is_delivery": {"type": "boolean"},
                                    "delivery_address": {"type": "string"},
                                    "delivery_notes": {"type": "string"},
                                    "completion_image_url": {"type": "string"},
                                    "listing": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "title": {"type": "string"}
                                        }
                                    },
                                    "restaurant": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "401": {"description": "Unauthorized - Invalid or missing token"},
        "404": {"description": "Order not found"},
        "500": {"description": "Internal server error"}
    }
})
def get_order_details(purchase_id):
    """Get details of a specific order"""
    user_id = get_jwt_identity()
    response, status = get_order_details_service(user_id, purchase_id)
    return jsonify(response), status