# services/auth_service.py
import logging
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number
from flask_jwt_extended import create_access_token
from app.models import db, User
from app.services.communication import auth_code_generator
from app.services.communication.email_service import send_email

logger = logging.getLogger(__name__)


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
    Returns a tuple (success: bool, code/message: str)
    """
    return auth_code_generator.generate_verification_code(ip=ip, identifier=login_type)


def login_user(data, client_ip):
    """
    Process login request.

    Expected data keys:
      - email
      - phone_number
      - password
      - login_type ("email" or "phone_number")
      - password_login (boolean)
      - step: one of ["send_code", "verify_code", "skip_verification"]

    Returns a tuple: (response dict, status code)
    """
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    login_type = data.get("login_type")
    password_login = data.get("password_login")
    step = data.get("step", None)  # Expect caller to provide this now

    logger.info(f"Login attempt from IP: {client_ip}, login_type: {login_type}, "
                f"email: {email}, phone_number: {phone_number}, password_login: {password_login}")

    if not login_type:
        logger.info("Missing login type.")
        return ({
                    "success": False,
                    "message": "Missing login type.",
                    "details": {"error_code": "MISSING_LOGIN_TYPE"}
                }, 400)

    # If password_login is true, we assume we bypass code verification.
    if password_login:
        step = 'skip_verification'

    if not email and not phone_number:
        logger.info("Missing email or phone number.")
        return ({
                    "success": False,
                    "message": "Login using email or phone number",
                    "details": {"error_code": "MISSING_EMAIL_OR_PHONE_NUMBER"}
                }, 400)

    if step not in ["send_code", "verify_code", "skip_verification"]:
        logger.info(f"Invalid step provided: {step}")
        return {"success": False, "message": "Invalid step"}, 400

    # Retrieve the user according to login type
    user = None
    if login_type == "email":
        user = get_user_by_email(email=email)
    elif login_type == "phone_number":
        user = get_user_by_phone(phone_number=phone_number)

    if not user:
        logger.info(f"User not found for {login_type}: {email or phone_number}")
        return {"success": False, "message": "User not found"}, 404

    if step == "skip_verification":
        if not password:
            logger.info("Password missing for password login.")
            return {"success": False, "message": "Password is required for login."}, 400
        if check_password_hash(user.password, password):
            token = create_access_token(identity=str(user.id))
            logger.info(f"User_id {user.id} authenticated successfully with password.")
            return {"success": True, "token": token}, 200
        else:
            logger.info(f"Incorrect password for user_id: {user.id}")
            return {"success": False, "message": "Wrong password"}, 400
    elif step == "send_code":
        success, code_or_message = generate_verification_code(ip=client_ip, login_type=login_type)
        if success:
            # For example purposes, we call send_email here.
            # In a real implementation, you would call your SMS or email service.
            if login_type == "email" and email:
                subject = "Your Verification Code"
                message = f"Your verification code is: {code_or_message}. This code will expire in 10 minutes."
                send_email(email, subject, message)
            logger.info(f"Verification code sent to {login_type}: {email or phone_number}")
            return ({
                        "success": True,
                        "message": "Verification code sent successfully.",
                        "details": {}
                    }, 200)
        else:
            logger.info(f"Failed to send verification code: {code_or_message}")
            return ({
                        "success": False,
                        "message": code_or_message,
                        "details": {}
                    }, 400)
    # You could later add "verify_code" step here.
    logger.info("Failed to process login step.")
    return {"success": False, "message": "Failed to process login."}, 400


def register_user(data):
    """
    Process user registration.

    Expected keys: name_surname, email, phone_number, password, role.

    Returns a tuple (response dict, status code)
    """
    name_surname = data.get("name_surname")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    role = data.get("role", "customer")

    logger.info(f"Registration attempt for email: {email}, phone_number: {phone_number}, role: {role}")

    if role not in ["customer", "owner"]:
        logger.info(f"Invalid role: {role}")
        return {"success": False, "message": "Invalid role"}, 400

    if not email and not phone_number:
        logger.info("Registration attempt missing email or phone number")
        return {"success": False, "message": "Email or phone number is required"}, 400

    if not password:
        logger.info("Registration attempt missing password")
        return {"success": False, "message": "Password is required"}, 400

    if not name_surname:
        logger.info("Registration attempt missing name.")
        return {"success": False, "message": "Name is required"}, 400

    new_user = User(name=name_surname, role=role)

    # Process email
    if email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            logger.info(f"Invalid email provided: {email} - {str(e)}")
            return {"success": False, "message": str(e)}, 400
        if get_user_by_email(email=email):
            logger.info(f"Email already exists: {email}")
            return {"success": False, "message": "Email already exists"}, 409
        new_user.email = email
        new_user.email_verified = False

    # Process phone number
    if phone_number:
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not is_valid_number(parsed_number):
                logger.info(f"Invalid phone number: {phone_number}")
                return {"success": False, "message": "Invalid phone number"}, 400
        except NumberParseException:
            logger.info(f"Invalid phone number format: {phone_number}")
            return {"success": False, "message": "Invalid phone number format"}, 400
        if get_user_by_phone(phone_number=phone_number):
            logger.info(f"Phone number already exists: {phone_number}")
            return {"success": False, "message": "Phone number already exists"}, 409
        new_user.phone_number = phone_number

    new_user.password = generate_password_hash(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {email or phone_number}")
        # Optionally send a verification email:
        if email:
            code = auth_code_generator.set_verification_code()
            auth_code_generator.store_verification_code(identifier=email, code=code)
            subject = "Your Verification Code"
            message = f"Your verification code is: {code}. This code will expire in 10 minutes."
            send_email(email, subject, message)
        return {"success": True, "message": "User registered successfully!"}, 201
    except Exception as e:
        logger.info(f"Error during registration: {str(e)}")
        db.session.rollback()
        return {"success": False, "message": "An error occurred during registration."}, 500


def verify_email_code(data, client_ip):
    """
    Verify an email using the provided verification code.

    Expected keys: email, verification_code.
    """
    email = data.get("email")
    verification_code = data.get("verification_code")
    logger.info(f"Email verification attempt from IP: {client_ip} for email: {email}")

    if not email or not verification_code:
        logger.info("Missing email or verification code for verification")
        return ({"success": False, "message": "Email and verification code are required.",
                 "details": {"error_code": "MISSING_EMAIL_OR_CODE"}}, 400)

    # Validate email format
    try:
        validate_email(email)
    except EmailNotValidError as e:
        logger.info(f"Invalid email format during verification: {email} - {str(e)}")
        return ({"success": False, "message": "Invalid email format.",
                 "details": {"error_code": "INVALID_EMAIL_FORMAT"}}, 400)

    user = get_user_by_email(email=email)
    if not user:
        logger.info(f"User not found for email verification: {email}")
        return ({"success": False, "message": "User not found.",
                 "details": {"error_code": "USER_NOT_FOUND"}}, 404)

    if user.email_verified:
        logger.info(f"Email already verified for user_id: {user.id}")
        return {"success": True, "message": "Email is already verified."}, 200

    # Verify the code using the auth_code_generator service:
    is_verified = auth_code_generator.verify_code(identifier=email, provided_code=verification_code)
    if is_verified:
        try:
            user.email_verified = True
            db.session.commit()
            logger.info(f"Email verified successfully for user_id: {user.id}")
            return {"success": True, "message": "Email verified successfully."}, 200
        except Exception as e:
            logger.error(f"Error updating email_verified status for user_id: {user.id} - {str(e)}")
            db.session.rollback()
            return ({"success": False, "message": "An error occurred while updating verification status.",
                     "details": {"error_code": "DATABASE_ERROR"}}, 500)
    else:
        logger.info(f"Invalid verification code for email: {email}")
        return ({"success": False, "message": "Invalid or expired verification code.",
                 "details": {"error_code": "INVALID_CODE"}}, 400)
