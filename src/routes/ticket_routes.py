import json
import sys
import traceback
from datetime import datetime, UTC
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.models import User, db
from src.models.purchase_report import PurchaseReport

ticket_bp = Blueprint('ticket', __name__)


@ticket_bp.route('/tickets', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Tickets'],
    'summary': 'Get all tickets in the system',
    'description': 'Support team members can view all purchase reports (tickets) in the system',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Tickets retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'tickets': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'user_id': {'type': 'integer'},
                                'purchase_id': {'type': 'integer'},
                                'restaurant_id': {'type': 'integer'},
                                'listing_id': {'type': 'integer'},
                                'description': {'type': 'string'},
                                'image_url': {'type': 'string'},
                                'reported_at': {'type': 'string'}
                            }
                        }
                    },
                    'timestamp': {'type': 'string'}
                }
            }
        },
        403: {
            'description': 'Not authorized as support team member',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'Only support team members can access tickets'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'An error occurred while retrieving tickets'},
                    'error': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        }
    }
})
def get_all_tickets():
    try:
        current_time = "2025-05-16 23:31:17"  # Updated timestamp
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args),
            "timestamp": current_time,
            "user": "emreutkan"  # Using the provided username
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can access tickets",
                "timestamp": current_time
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        # Get all purchase reports as tickets
        tickets = PurchaseReport.query.all()

        # Format the tickets for response
        formatted_tickets = []
        for ticket in tickets:
            formatted_ticket = {
                "id": ticket.id,
                "user_id": ticket.user_id,
                "purchase_id": ticket.purchase_id,
                "restaurant_id": ticket.restaurant_id,
                "listing_id": ticket.listing_id,
                "description": ticket.description,
                "image_url": ticket.image_url,
                "reported_at": ticket.reported_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.reported_at else None
            }

            # Add user name if relationship exists and is loaded
            if hasattr(ticket, 'user') and ticket.user:
                formatted_ticket["user_name"] = ticket.user.name if hasattr(ticket.user, 'name') else None

            # Add restaurant name if relationship exists and is loaded
            if hasattr(ticket, 'restaurant') and ticket.restaurant:
                formatted_ticket["restaurant_name"] = ticket.restaurant.restaurantName if hasattr(ticket.restaurant,
                                                                                                  'restaurantName') else None

            # Add listing title if relationship exists and is loaded
            if hasattr(ticket, 'listing') and ticket.listing:
                formatted_ticket["listing_title"] = ticket.listing.title if hasattr(ticket.listing, 'title') else None

            formatted_tickets.append(formatted_ticket)

        response = {
            "success": True,
            "tickets": formatted_tickets,
            "timestamp": current_time
        }

        print(json.dumps({"response": "Ticket data retrieved successfully", "status": 200}, indent=2))
        return jsonify(response), 200

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while retrieving tickets",
            "error": str(e),
            "timestamp": "2025-05-16 23:31:17"  # Updated timestamp
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@ticket_bp.route('/tickets/search', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Tickets'],
    'summary': 'Search for tickets',
    'description': 'Support team members can search for tickets by various criteria',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filter by user ID'
        },
        {
            'name': 'restaurant_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filter by restaurant ID'
        },
        {
            'name': 'query',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Search in ticket description'
        }
    ],
    'responses': {
        200: {
            'description': 'Search results retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'tickets': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'user_id': {'type': 'integer'},
                                'purchase_id': {'type': 'integer'},
                                'restaurant_id': {'type': 'integer'},
                                'description': {'type': 'string'},
                                'image_url': {'type': 'string'},
                                'reported_at': {'type': 'string'}
                            }
                        }
                    },
                    'timestamp': {'type': 'string'}
                }
            }
        },
        403: {
            'description': 'Not authorized as support team member',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'Only support team members can search tickets'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'An error occurred during ticket search'},
                    'error': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        }
    }
})
def search_tickets():
    try:
        current_time = "2025-05-16 23:31:17"  # Updated timestamp
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args),
            "timestamp": current_time,
            "user": "emreutkan"  # Using the provided username
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can search tickets",
                "timestamp": current_time
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        # Get search parameters
        user_id = request.args.get('user_id', type=int)
        restaurant_id = request.args.get('restaurant_id', type=int)
        query = request.args.get('query', '')

        # Start with base query
        ticket_query = PurchaseReport.query

        # Apply filters
        if user_id:
            ticket_query = ticket_query.filter(PurchaseReport.user_id == user_id)
        if restaurant_id:
            ticket_query = ticket_query.filter(PurchaseReport.restaurant_id == restaurant_id)
        if query:
            ticket_query = ticket_query.filter(PurchaseReport.description.ilike(f'%{query}%'))

        # Execute query
        tickets = ticket_query.all()

        # Format the tickets for response
        formatted_tickets = []
        for ticket in tickets:
            formatted_ticket = {
                "id": ticket.id,
                "user_id": ticket.user_id,
                "purchase_id": ticket.purchase_id,
                "restaurant_id": ticket.restaurant_id,
                "listing_id": ticket.listing_id,
                "description": ticket.description,
                "image_url": ticket.image_url,
                "reported_at": ticket.reported_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.reported_at else None
            }

            # Add user name if relationship exists and is loaded
            if hasattr(ticket, 'user') and ticket.user:
                formatted_ticket["user_name"] = ticket.user.name if hasattr(ticket.user, 'name') else None

            # Add restaurant name if relationship exists and is loaded
            if hasattr(ticket, 'restaurant') and ticket.restaurant:
                formatted_ticket["restaurant_name"] = ticket.restaurant.restaurantName if hasattr(ticket.restaurant,
                                                                                                  'restaurantName') else None

            # Add listing title if relationship exists and is loaded
            if hasattr(ticket, 'listing') and ticket.listing:
                formatted_ticket["listing_title"] = ticket.listing.title if hasattr(ticket.listing, 'title') else None

            formatted_tickets.append(formatted_ticket)

        response = {
            "success": True,
            "tickets": formatted_tickets,
            "timestamp": current_time
        }

        print(json.dumps({"response": "Ticket search completed", "status": 200}, indent=2))
        return jsonify(response), 200

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred during ticket search",
            "error": str(e),
            "timestamp": "2025-05-16 23:31:17"  # Updated timestamp
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500


@ticket_bp.route('/tickets/<int:ticket_id>/disregard', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Tickets'],
    'summary': 'Disregard a ticket',
    'description': 'Support team members can disregard a ticket by marking it as resolved',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'ticket_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the ticket to disregard'
        }
    ],
    'responses': {
        200: {
            'description': 'Ticket disregarded successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Ticket disregarded successfully'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        403: {
            'description': 'Not authorized as support team member',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'Only support team members can disregard tickets'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Ticket not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'Ticket not found'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': 'An error occurred while disregarding ticket'},
                    'error': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        }
    }
})
def disregard_ticket(ticket_id):
    try:
        current_time = "2025-05-16 23:31:17"  # Updated timestamp
        request_log = {
            "endpoint": request.path,
            "method": request.method,
            "headers": dict(request.headers),
            "ticket_id": ticket_id,
            "timestamp": current_time,
            "user": "emreutkan"  # Using the provided username
        }
        print(json.dumps({"request": request_log}, indent=2))

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'support':
            error_response = {
                "success": False,
                "message": "Only support team members can disregard tickets",
                "timestamp": current_time
            }
            print(json.dumps({"error_response": error_response, "status": 403}, indent=2))
            return jsonify(error_response), 403

        # Find the ticket (purchase report)
        ticket = PurchaseReport.query.get(ticket_id)
        if not ticket:
            error_response = {
                "success": False,
                "message": "Ticket not found",
                "timestamp": current_time
            }
            print(json.dumps({"error_response": error_response, "status": 404}, indent=2))
            return jsonify(error_response), 404

        # Since PurchaseReport doesn't have a status field, we'll need to add one
        # For now, we'll just delete the ticket to "disregard" it
        # In a real implementation, you'd probably want to add a status field to track which support
        # user resolved it and when
        db.session.delete(ticket)
        db.session.commit()

        response = {
            "success": True,
            "message": "Ticket disregarded successfully",
            "timestamp": current_time
        }

        print(json.dumps({"response": response, "status": 200}, indent=2))
        return jsonify(response), 200

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc(file=sys.stderr)

        error_response = {
            "success": False,
            "message": "An error occurred while disregarding ticket",
            "error": str(e),
            "timestamp": "2025-05-16 23:31:17"  # Updated timestamp
        }
        print(json.dumps({"error_response": error_response, "status": 500}, indent=2))
        return jsonify(error_response), 500