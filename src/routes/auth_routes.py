# routes/auth_routes.py

import logging
import coloredlogs
from flask import Blueprint, request, jsonify
from src.services.auth_service import login_user, register_user, verify_email_code

auth_bp = Blueprint("auth", __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
coloredlogs.install(level="INFO", logger=logger, fmt=log_format)


def get_client_ip():
    """Retrieve the client's IP address."""
    return request.headers.get("X-Forwarded-For", request.remote_addr) or "no_ip"


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User Login Endpoint
    ---
    tags:
      - Authentication
    summary: Authenticate user and generate access token
    description: |
      Handles user authentication through email/phone and password or verification code.
      Supports multi-step authentication process including code verification.

      Authentication steps:
      1. send_code: Sends verification code to email/phone
      2. verify_code: Verifies the sent code
      3. skip_verification: Direct password-based login

      Note: Current time (UTC): 2025-01-15 15:12:48
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
                example: "user@example.com"
                description: Required if login_type is "email"
              phone_number:
                type: string
                example: "+1234567890"
                description: Required if login_type is "phone_number"
              password:
                type: string
                description: Required if password_login is true
              login_type:
                type: string
                enum: [email, phone_number]
                description: Method of authentication
              password_login:
                type: boolean
                description: If true, uses password authentication instead of code
              step:
                type: string
                enum: [send_code, verify_code, skip_verification]
                description: Current authentication step
            example:
              email: "user@example.com"
              login_type: "email"
              password_login: true
              step: "skip_verification"
              password: "userpassword123"
    responses:
      200:
        description: Successful authentication or code sent
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                token:
                  type: string
                  description: JWT access token (only provided on successful login)
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                message:
                  type: string
                  example: "Login successful"
      400:
        description: Invalid request parameters
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Invalid credentials"
                details:
                  type: object
                  properties:
                    error_code:
                      type: string
                      example: "INVALID_CREDENTIALS"
      401:
        description: Authentication failed
      404:
        description: User not found
      429:
        description: Too many login attempts
    """
    data = request.get_json()
    client_ip = get_client_ip()
    response, status = login_user(data, client_ip)
    return jsonify(response), status


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    User Registration Endpoint
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: |
      Creates a new user account with the provided details.
      Supports both customer and owner roles.
      Validates email and phone number formats.
      Automatically sends verification email if email is provided.

      Note: Current time (UTC): 2025-01-15 15:12:48
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
                example: "John Doe"
                description: Full name of the user
              email:
                type: string
                example: "john.doe@example.com"
                description: Valid email address (optional if phone_number provided)
              phone_number:
                type: string
                example: "+1234567890"
                description: Valid phone number (optional if email provided)
              password:
                type: string
                format: password
                example: "SecurePass123!"
                description: User password (min 8 characters)
              role:
                type: string
                enum: [customer, owner]
                default: customer
                description: User role in the system
    responses:
      201:
        description: User successfully registered
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "User registered successfully!"
      400:
        description: Invalid input data
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Invalid email format"
      409:
        description: Email or phone number already exists
      500:
        description: Server error during registration
    """
    data = request.get_json()
    response, status = register_user(data)
    return jsonify(response), status


@auth_bp.route("/verify_email", methods=["POST"])
def verify_email():
    """
    Email Verification Endpoint
    ---
    tags:
      - Authentication
    summary: Verify user's email address
    description: |
      Verifies user's email address using a verification code.
      The code should have been sent during registration or login process.

      Note: Current time (UTC): 2025-01-15 15:12:48
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
                example: "user@example.com"
                description: Email address to verify
              verification_code:
                type: string
                example: "123456"
                description: 6-digit verification code sent to email
    responses:
      200:
        description: Email successfully verified
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Email verified successfully."
      400:
        description: Invalid or expired verification code
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Invalid or expired verification code"
                details:
                  type: object
                  properties:
                    error_code:
                      type: string
                      example: "INVALID_CODE"
      404:
        description: User not found
      500:
        description: Server error during verification
    """
    data = request.get_json()
    client_ip = get_client_ip()
    response, status = verify_email_code(data, client_ip)
    return jsonify(response), status