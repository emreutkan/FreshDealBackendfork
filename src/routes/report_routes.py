# routes/report_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.report_service import create_purchase_report_service, get_user_reports_service

report_bp = Blueprint("report", __name__)

@report_bp.route("/report", methods=["POST"])
@jwt_required()
def create_report():
    """
    Create a new report for a particular purchase.
    Expects JSON with:
      - purchase_id: int (required)
      - image_url: str (optional)
      - description: str (required)
    ---
    tags:
      - Reports
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - purchase_id
              - description
            properties:
              purchase_id:
                type: integer
              image_url:
                type: string
              description:
                type: string
    responses:
      201:
        description: Report created successfully
      400:
        description: Invalid request (missing fields)
      404:
        description: Purchase not found
      500:
        description: Error creating the report
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        purchase_id = data.get("purchase_id")
        image_url = data.get("image_url")
        description = data.get("description")

        if not purchase_id or not description:
            return jsonify({"message": "Missing required fields (purchase_id, description)."}), 400

        response, status = create_purchase_report_service(user_id, purchase_id, image_url, description)
        return jsonify(response), status

    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500


@report_bp.route("/report", methods=["GET"])
@jwt_required()
def get_user_reports():
    """
    Get all reports created by the current user.
    ---
    tags:
      - Reports
    security:
      - BearerAuth: []
    responses:
      200:
        description: A list of user reports
      500:
        description: Error fetching the reports
    """
    try:
        user_id = get_jwt_identity()
        response, status = get_user_reports_service(user_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500
