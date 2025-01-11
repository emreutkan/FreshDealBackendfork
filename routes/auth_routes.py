# routes/auth_routes.py

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number
from flask_jwt_extended import create_access_token
from models import db, User
from services.communication import auth_code_generator, email_service
import logging
import coloredlogs

from services.communication.email_service import send_email

# Initialize Blueprint
auth_bp = Blueprint("auth", __name__)

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set to INFO since all logs are at this level

# Define log format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Install coloredlogs with the defined format
coloredlogs.install(level='INFO', logger=logger, fmt=log_format)


def get_client_ip():
    """
    Retrieve the client's IP address.
    """
    return request.headers.get("X-Forwarded-For", request.remote_addr) or "no_ip"


def get_user_by_email(email):
    """
    Retrieve a user by their email.
    """
    return User.query.filter_by(email=email).first() if email else None


def get_user_by_phone(phone_number):
    """
    Retrieve a user by their phone number.
    """
    return User.query.filter_by(phone_number=phone_number).first() if phone_number else None


def generate_verification_code(ip=None, login_type=None):
    """
    Generate a verification code using the auth_code_generator service.
    """
    return auth_code_generator.generate_verification_code(ip=ip, identifier=login_type)  # Returns (bool, code)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handle user login.
    """
    data = request.json
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    verification_code = data.get("verification_code")
    step = data.get("step")  # "send_code", "verify_code", "skip_verification"
    login_type = data.get("login_type")  # "email", "phone_number"
    password_login = data.get("password_login")  # boolean
    ip = get_client_ip()

    # Log the login attempt
    logger.info(
        f"Login attempt from IP: {ip}, login_type: {login_type}, email: {email}, phone_number: {phone_number}, step: {step}, password_login: {password_login}"
    )

    # Validate login_type
    if not login_type:
        logger.info("Login attempt with missing login type.")
        return jsonify({
            "success": False,
            "message": "Missing login type.",
            "details": {
                "error_code": "MISSING_LOGIN_TYPE"
            }
        }), 400

    # Adjust step if password_login is True
    if password_login:
        step = 'skip_verification'

    # Ensure either email or phone_number is provided
    if not email and not phone_number:
        logger.info("Login attempt without email or phone number.")
        return jsonify({
            "success": False,
            "message": "Login using email or phone number",
            "details": {
                "error_code": "MISSING_EMAIL_OR_PHONE_NUMBER"
            }
        }), 400

    # Validate step
    if step not in ["send_code", "verify_code", "skip_verification"]:
        logger.info(f"Invalid step provided: {step}")
        return jsonify({"success": False, "message": "Invalid step"}), 400

    # Retrieve user based on login_type
    user = None
    if login_type == "email":
        user = get_user_by_email(email=email)
    elif login_type == "phone_number":
        user = get_user_by_phone(phone_number=phone_number)

    # If user not found
    if not user:
        logger.info(f"User not found for login_type: {login_type}, identifier: {email or phone_number}")
        return jsonify({"success": False, "message": "User not found"}), 404

    # Handle different steps
    if step == "skip_verification":
        if not password:
            logger.info("Password missing for password_login.")
            return jsonify({"success": False, "message": "Password is required for login."}), 400

        if check_password_hash(user.password, password):
            token = create_access_token(identity=str(user.id))
            logger.info(f"User_id {user.id} authenticated successfully with password.")
            return jsonify({"success": True, "token": token}), 200
        else:
            logger.info(f"Incorrect password for user_id: {user.id}")
            return jsonify({"success": False, "message": "Wrong password"}), 400

    elif step == "send_code":
        response, message = generate_verification_code(ip=ip, login_type=login_type)
        if response:
            # Here, you would typically send the verification code via email or SMS
            # For example:
            # email_service.send_verification_email(user.email, message)
            logger.info(f"Verification code sent to {login_type}: {email or phone_number}")
            return jsonify({
                "success": True,
                "message": "Verification code sent successfully.",
                "details": {}
            }), 200
        else:
            logger.info(f"Failed to send verification code - Reason: {message}")
            return jsonify({
                "success": False,
                "message": message,  # Return the error message from generate_verification_code
                "details": {}
            }), 400  # Adjust status code based on the error

    elif step == "verify_code":
        if not verification_code:
            logger.info("Verification code missing during verification step.")
            return jsonify({
                "success": False,
                "message": f"Enter Verification Code sent to your {login_type}",
                "details": {
                    "error_code": "MISSING_VERIFICATION_CODE"
                }
            }), 400

        verification_response = auth_code_generator.verify_code(identifier=login_type, provided_code=verification_code)
        if verification_response:
            token = create_access_token(identity=str(user.id))
            logger.info(f"User_id {user.id} authenticated successfully with verification code.")
            return jsonify({"success": True, "token": token}), 200
        else:
            logger.info("Invalid verification code provided.")
            return jsonify({"success": False, "message": "Invalid verification code."}), 400

    # Fallback in case step handling fails
    logger.info("Failed to process login step.")
    return jsonify({"success": False, "message": "Failed to process login."}), 400

# Helper to send a verification email
def send_verification_email(email, code):
    """
    Send a verification email with the given code.
    """
    subject = "Your Verification Code"
    message = f"Your verification code is: {code}. This code will expire in 10 minutes."
    send_email(email, subject, message)
    logger.info(f"Verification email sent to {email}")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Handle user registration.
    """
    data = request.json
    name_surname = data.get("name_surname")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    role = data.get("role")

    logger.info(f"Registration attempt for email: {email}, phone_number: {phone_number}, role: {role}")

    # Set default role if not provided
    if not role:
        role = "customer"
    elif role not in ["customer", "owner"]:
        logger.info(f"Invalid role provided during registration: {role}")
        return jsonify({"success": False, "message": "Invalid role"}), 400

    # Ensure either email or phone_number is provided
    if not email and not phone_number:
        logger.info("Registration attempt without email or phone number.")
        return jsonify({"success": False, "message": "Email or phone number is required"}), 400

    # Ensure password is provided
    if not password:
        logger.info("Registration attempt without password.")
        return jsonify({"success": False, "message": "Password is required"}), 400

    # Ensure name is provided
    if not name_surname:
        logger.info("Registration attempt without name.")
        return jsonify({"success": False, "message": "Name is required"}), 400

    # Initialize new_user
    new_user = User(
        name=name_surname,
        role=role
    )

    # Handle email
    if email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            logger.info(f"Invalid email provided during registration: {email} - Reason: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400

        existing_user = get_user_by_email(email=email)
        if existing_user:
            logger.info(f"Email already exists during registration: {email}")
            return jsonify({"success": False, "message": "Email already exists"}), 409  # 409 Conflict

        new_user.email = email
        new_user.email_verified = False  # Default to unverified

    # Handle phone number
    if phone_number:
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not is_valid_number(parsed_number):
                logger.info(f"Invalid phone number provided during registration: {phone_number}")
                return jsonify({"success": False, "message": "Invalid phone number"}), 400
        except NumberParseException:
            logger.info(f"Invalid phone number format during registration: {phone_number}")
            return jsonify({"success": False, "message": "Invalid phone number format"}), 400

        existing_phone_user = get_user_by_phone(phone_number=phone_number)
        if existing_phone_user:
            logger.info(f"Phone number already exists during registration: {phone_number}")
            return jsonify({"success": False, "message": "Phone number already exists"}), 409  # 409 Conflict

        new_user.phone_number = phone_number

    # Hash the password
    hashed_password = generate_password_hash(password)
    new_user.password = hashed_password

    # Add and commit the new user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {email or phone_number}")

        # Send a verification email if email is provided
        if email:
            code = auth_code_generator.set_verification_code()
            auth_code_generator.store_verification_code(identifier=email, code=code)
            send_verification_email(email, code)

        return jsonify({"success": True, "message": "User registered successfully!"}), 201
    except Exception as e:
        logger.info(f"Error during user registration: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "An error occurred during registration."}), 500


# ================== Verification Endpoint ==================

@auth_bp.route("/verify_email", methods=["POST"])
def verify_email():
    """
    Handle email verification by validating the provided verification code.
    """
    data = request.json
    email = data.get("email")
    verification_code = data.get("verification_code")

    ip = get_client_ip()

    logger.info(f"Email verification attempt from IP: {ip} for email: {email}")

    # Validate input presence
    if not email or not verification_code:
        logger.info("Email or verification code missing in verification request.")
        return jsonify({
            "success": False,
            "message": "Email and verification code are required.",
            "details": {
                "error_code": "MISSING_EMAIL_OR_CODE"
            }
        }), 400

    # Validate email format
    try:
        validate_email(email)
    except EmailNotValidError as e:
        logger.info(f"Invalid email format during verification: {email} - Reason: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Invalid email format.",
            "details": {
                "error_code": "INVALID_EMAIL_FORMAT"
            }
        }), 400

    # Retrieve user
    user = get_user_by_email(email=email)
    if not user:
        logger.info(f"User not found during verification for email: {email}")
        return jsonify({
            "success": False,
            "message": "User not found.",
            "details": {
                "error_code": "USER_NOT_FOUND"
            }
        }), 404

    # Check if email is already verified
    if user.email_verified:
        logger.info(f"Email already verified for user_id: {user.id}")
        return jsonify({
            "success": True,
            "message": "Email is already verified."
        }), 200

    # Verify the provided code
    is_verified = auth_code_generator.verify_code(identifier=email, provided_code=verification_code)

    if is_verified:
        try:
            user.email_verified = True
            db.session.commit()
            logger.info(f"Email verified successfully for user_id: {user.id}")

            return jsonify({
                "success": True,
                "message": "Email verified successfully."
            }), 200
        except Exception as e:
            logger.error(f"Error updating email_verified status for user_id: {user.id} - {str(e)}")
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "An error occurred while updating verification status.",
                "details": {
                    "error_code": "DATABASE_ERROR"
                }
            }), 500
    else:
        logger.info(f"Invalid verification code provided for email: {email}")
        return jsonify({
            "success": False,
            "message": "Invalid or expired verification code.",
            "details": {
                "error_code": "INVALID_CODE"
            }
        }), 400
