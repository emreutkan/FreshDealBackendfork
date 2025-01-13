# routes/auth_routes.py
import logging
import coloredlogs
from flask import Blueprint, request, jsonify
from app.services import (
    login_user,
    register_user,
    verify_email_code
)

auth_bp = Blueprint("auth", __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
coloredlogs.install(level="INFO", logger=logger, fmt=log_format)


def get_client_ip():
    """
    Retrieve the client's IP address.
    """
    return request.headers.get("X-Forwarded-For", request.remote_addr) or "no_ip"


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login endpoint.

    Expects a JSON payload with the following fields:
      - email (optional if using phone_number)
      - phone_number (optional if using email)
      - password (required if password_login is true)
      - login_type: "email" or "phone_number"
      - password_login: boolean
      - step: one of ["send_code", "verify_code", "skip_verification"]

    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - login_type
              - password_login
              - step
            properties:
              email:
                type: string
              phone_number:
                type: string
              password:
                type: string
              login_type:
                type: string
                enum: [email, phone_number]
              password_login:
                type: boolean
              step:
                type: string
                description: The current step in the login process.
                enum: [send_code, verify_code, skip_verification]
    responses:
      200:
        description: Successful login (or code sent).
        content:
          application/json:
            schema:
              type: object
      400:
        description: Missing or invalid input.
      404:
        description: User not found.
    """
    data = request.get_json()
    client_ip = get_client_ip()
    response, status = login_user(data, client_ip)
    return jsonify(response), status


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    User registration endpoint.

    Expects a JSON payload with:
      - name_surname (required)
      - email (optional, but if provided, must be valid)
      - phone_number (optional, but if provided, must be valid)
      - password (required)
      - role (optional; defaults to "customer"; allowed: "customer", "owner")

    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name_surname
              - password
            properties:
              name_surname:
                type: string
              email:
                type: string
              phone_number:
                type: string
              password:
                type: string
              role:
                type: string
                enum: [customer, owner]
    responses:
      201:
        description: User registered successfully.
      400:
        description: Invalid input.
      409:
        description: Conflict (email or phone number already exists).
      500:
        description: An error occurred during registration.
    """
    data = request.get_json()
    response, status = register_user(data)
    return jsonify(response), status


@auth_bp.route("/verify_email", methods=["POST"])
def verify_email():
    """
    Email verification endpoint.

    Expects a JSON payload with:
      - email (required)
      - verification_code (required)

    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - email
              - verification_code
            properties:
              email:
                type: string
              verification_code:
                type: string
    responses:
      200:
        description: Email verified successfully.
      400:
        description: Invalid input or verification code.
      404:
        description: User not found.
      500:
        description: An error occurred.
    """
    data = request.get_json()
    client_ip = get_client_ip()
    response, status = verify_email_code(data, client_ip)
    return jsonify(response), status
