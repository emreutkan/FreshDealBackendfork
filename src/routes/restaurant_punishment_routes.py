from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.restaurant_punishment_service import RestaurantPunishmentService
from src.models import User
from datetime import datetime, UTC
import json
import traceback
import sys

restaurant_punishment_bp = Blueprint('restaurant_punishment', __name__)


@restaurant_punishment_bp.route('/restaurants/<int:restaurant_id>/punish', methods=['POST'])
@jwt_required()
def punish_restaurant(restaurant_id):
    """
    Issue a Punishment to a Restaurant
    This endpoint allows support team members to issue temporary or permanent punishments to restaurants.

    ---
    summary: Issue a punishment to a restaurant
    description: >
      Support team members can issue temporary or permanent punishments to restaurants based on
      violations or customer complaints.
    tags:
      - Restaurant Punishment
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
        description: ID of the restaurant to punish
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            duration_type:
              type: string
              enum: ['THREE_DAYS', 'ONE_WEEK', 'ONE_MONTH', 'THREE_MONTHS', 'PERMANENT']
              description: Duration of the punishment
            reason:
              type: string
              description: Reason for the punishment
          required:
            - duration_type
            - reason
    responses:
      201:
        description: Punishment issued successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            punishment_id:
              type: integer
      400:
        description: Invalid request data
      403:
        description: Not authorized as support team member
      404:
        description: Restaurant not found
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "body": request.get_json(),
            "restaurant_id": restaurant_id
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can issue punishments",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        data = request.get_json()
        if not data:
            error_response = {
                "success": False,
                "message": "No data provided",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 400}, indent=2))
            return jsonify(error_response), 400

        response, status_code = RestaurantPunishmentService.issue_punishment(
            restaurant_id,
            data,
            current_user_id
        )
        response["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        print(json.dumps({"response": response, "status": status_code}, indent=2))
        return jsonify(response), status_code

    except Exception as e:
        print("An error occurred:", str(e))
        # Print traceback to console separately
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while issuing punishment",
            "error": str(e),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@restaurant_punishment_bp.route('/orders/<int:order_id>/refund', methods=['POST'])
@jwt_required()
def issue_refund(order_id):
    """
    Issue a Refund for an Order
    This endpoint allows support team members to issue refunds for orders.

    ---
    summary: Issue a refund for an order
    description: >
      Support team members can issue refunds for orders due to customer complaints
      or quality issues.
    tags:
      - Restaurant Punishment
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID of the order to refund
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              format: float
              description: Amount to refund
            reason:
              type: string
              description: Reason for the refund
          required:
            - amount
            - reason
    responses:
      201:
        description: Refund issued successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            refund_id:
              type: integer
      400:
        description: Invalid request data
      403:
        description: Not authorized as support team member
      404:
        description: Order not found
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "body": request.get_json(),
            "order_id": order_id
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can issue refunds",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        data = request.get_json()
        if not data:
            error_response = {
                "success": False,
                "message": "No data provided",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 400}, indent=2))
            return jsonify(error_response), 400

        if not data.get('amount') or not data.get('reason'):
            error_response = {
                "success": False,
                "message": "Amount and reason are required",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 400}, indent=2))
            return jsonify(error_response), 400

        response, status_code = RestaurantPunishmentService.issue_refund(
            order_id,
            data,
            current_user_id
        )
        response["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        print(json.dumps({"response": response, "status": status_code}, indent=2))
        return jsonify(response), status_code

    except Exception as e:
        print("An error occurred:", str(e))
        # Print traceback to console separately
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while issuing refund",
            "error": str(e),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@restaurant_punishment_bp.route('/restaurants/<int:restaurant_id>/status', methods=['GET'])
def get_restaurant_status(restaurant_id):
    """
    Get Restaurant Punishment Status
    This endpoint retrieves the current punishment status of a restaurant.

    ---
    summary: Get restaurant punishment status
    description: >
      Get the current punishment status of a restaurant, including active punishment details
      if the restaurant is currently under punishment.
    tags:
      - Restaurant Punishment
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
        description: ID of the restaurant to check
    responses:
      200:
        description: Restaurant status retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            is_active:
              type: boolean
              description: Whether the restaurant is active or punished
            punishment:
              type: object
              properties:
                punishment_id:
                  type: integer
                  description: ID of the active punishment
                type:
                  type: string
                  description: Type of punishment (TEMPORARY or PERMANENT)
                start_date:
                  type: string
                  format: date-time
                  description: When the punishment started
                end_date:
                  type: string
                  format: date-time
                  description: When the punishment will end (null for PERMANENT)
                reason:
                  type: string
                  description: Reason for the punishment
            timestamp:
              type: string
              format: date-time
              description: Timestamp of the response
      404:
        description: Restaurant not found
      500:
        description: Server error
    """
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "restaurant_id": restaurant_id
        }
        print(json.dumps({"request": request_log}, indent=2))

        # Fixed tuple assignment error
        status_data, status_code = RestaurantPunishmentService.check_restaurant_status(restaurant_id)
        status_data["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        print(json.dumps({"response": status_data, "status": status_code}, indent=2))
        return jsonify(status_data), status_code

    except Exception as e:
        print("An error occurred:", str(e))
        # Print traceback to console separately
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while retrieving restaurant status",
            "error": str(e),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@restaurant_punishment_bp.route('/restaurants/<int:restaurant_id>/punishment-history', methods=['GET'])
@jwt_required()
def get_restaurant_punishment_history(restaurant_id):
    """
    Get Restaurant Punishment History
    This endpoint retrieves the complete punishment history for a restaurant.

    ---
    summary: Get restaurant punishment history
    description: >
      Returns a complete history of all punishments issued to a restaurant, including both
      active and reverted punishments with detailed information.
    tags:
      - Restaurant Punishment
    parameters:
      - name: restaurant_id
        in: path
        type: integer
        required: true
        description: ID of the restaurant to check
    responses:
      200:
        description: Restaurant punishment history retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            restaurant_name:
              type: string
              description: Name of the restaurant
            punishment_history:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: ID of the punishment
                  type:
                    type: string
                    description: Type of punishment (TEMPORARY or PERMANENT)
                  duration_days:
                    type: integer
                    description: Duration in days (null for PERMANENT)
                  start_date:
                    type: string
                    format: date-time
                    description: When the punishment started
                  end_date:
                    type: string
                    format: date-time
                    description: When the punishment will end
                  reason:
                    type: string
                    description: Reason for the punishment
                  is_active:
                    type: boolean
                    description: Whether the punishment is currently active
                  is_reverted:
                    type: boolean
                    description: Whether the punishment was reverted
                  created_by:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                  created_at:
                    type: string
                    format: date-time
                  reverted_info:
                    type: object
                    properties:
                      reverted_by:
                        type: object
                        properties:
                          id:
                            type: integer
                          name:
                            type: string
                      reverted_at:
                        type: string
                        format: date-time
                      reason:
                        type: string
            timestamp:
              type: string
              format: date-time
              description: Timestamp of the response
        examples:
          application/json:
            success: true
            restaurant_name: "Fresh Delights Restaurant"
            punishment_history: [
              {
                "id": 1,
                "type": "TEMPORARY",
                "duration_days": 7,
                "start_date": "2025-05-10T14:30:00Z",
                "end_date": "2025-05-17T14:30:00Z",
                "reason": "Multiple late deliveries",
                "is_active": false,
                "is_reverted": false,
                "created_by": {
                  "id": 5,
                  "name": "Support Agent 1"
                },
                "created_at": "2025-05-10T14:30:00Z"
              }
            ]
            timestamp: "2025-05-17 22:51:20"
      404:
        description: Restaurant not found
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "restaurant_id": restaurant_id
        }
        print(json.dumps({"request": request_log}, indent=2))

        data, status_code = RestaurantPunishmentService.get_punishment_history(restaurant_id)
        data["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        print(json.dumps({"response": data, "status": status_code}, indent=2))
        return jsonify(data), status_code

    except Exception as e:
        print("An error occurred:", str(e))
        # Print traceback to console separately
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while retrieving punishment history",
            "error": str(e),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@restaurant_punishment_bp.route('/punishments/<int:punishment_id>/revert', methods=['POST'])
@jwt_required()
def revert_punishment(punishment_id):
    """
    Revert a Restaurant Punishment
    This endpoint allows support team members to revert an active punishment.

    ---
    summary: Revert a restaurant punishment
    description: >
      Support team members can revert active punishments for restaurants with a provided reason,
      which will immediately restore the restaurant's active status.
    tags:
      - Restaurant Punishment
    parameters:
      - name: punishment_id
        in: path
        type: integer
        required: true
        description: ID of the punishment to revert
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            reason:
              type: string
              description: Reason for reverting the punishment
          required:
            - reason
    responses:
      200:
        description: Punishment reverted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            timestamp:
              type: string
              format: date-time
        examples:
          application/json:
            success: true
            message: "Punishment successfully reverted"
            timestamp: "2025-05-17 22:51:20"
      400:
        description: Invalid request data or punishment already reverted
      403:
        description: Not authorized as support team member
      404:
        description: Punishment not found
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "body": request.get_json(),
            "punishment_id": punishment_id
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can revert punishments",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        data = request.get_json()
        if not data or not data.get('reason'):
            error_response = {
                "success": False,
                "message": "Reversion reason is required",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps({"error_response": error_response, "status": 400}, indent=2))
            return jsonify(error_response), 400

        response, status_code = RestaurantPunishmentService.revert_punishment(
            punishment_id,
            data,
            current_user_id
        )
        response["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        print(json.dumps({"response": response, "status": status_code}, indent=2))
        return jsonify(response), status_code

    except Exception as e:
        print("An error occurred:", str(e))
        # Print traceback to console separately
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while reverting punishment",
            "error": str(e),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500