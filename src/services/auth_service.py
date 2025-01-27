# services/auth_service.py
import logging
from datetime import datetime, timedelta, UTC
from secrets import token_urlsafe

from flask import url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number
from flask_jwt_extended import create_access_token
from src.models import db, User
from src.services.communication import auth_code_generator
from src.services.communication.email_service import send_email

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
            token = create_access_token(identity=str(user.id), expires_delta=False)
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

    # Input validation
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
        # First save the user to the database
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {email or phone_number}")

        # Attempt to send verification email if email is provided
        # but don't let email sending failures affect registration
        if email:
            try:
                code = auth_code_generator.set_verification_code()
                auth_code_generator.store_verification_code(identifier=email, code=code)
                subject = "Your Verification Code"
                message = f"Your verification code is: {code}. This code will expire in 10 minutes."
                send_email(email, subject, message)
                logger.info(f"Verification email sent successfully to {email}")
            except Exception as email_error:
                # Log the email sending error but continue with registration
                logger.error(f"Failed to send verification email to {email}: {str(email_error)}")
                # Return success but indicate email sending failed
                return {
                    "success": True,
                    "message": "User registered successfully! Verification email could not be sent.",
                    "email_sent": False
                }, 201

        # Return success if everything went well
        return {
            "success": True,
            "message": "User registered successfully!",
            "email_sent": True if email else None
        }, 201

    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
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

def initiate_password_reset(data):
    """
    Initiate the password reset process by sending a reset link to user's email.

    Expected data keys:
    - email

    Returns tuple (response dict, status code)
    """
    email = data.get("email")
    logger.info(f"Password reset initiated for email: {email}")

    if not email:
        logger.info("Missing email for password reset")
        return {
            "success": False,
            "message": "Email is required",
            "details": {"error_code": "MISSING_EMAIL"}
        }, 400

    try:
        validate_email(email)
    except EmailNotValidError as e:
        logger.info(f"Invalid email format: {email} - {str(e)}")
        return {
            "success": False,
            "message": "Invalid email format",
            "details": {"error_code": "INVALID_EMAIL"}
        }, 400

    user = get_user_by_email(email)
    if not user:
        # For security reasons, still return success even if email doesn't exist
        logger.info(f"Password reset attempted for non-existent email: {email}")
        return {
            "success": True,
            "message": "If the email exists, a password reset link will be sent.",
        }, 200

    # Generate a secure token
    reset_token = token_urlsafe(32)
    # Use timezone-aware datetime
    expiration = datetime.now(UTC) + timedelta(hours=1)

    try:
        # Store the reset token in the user record
        user.reset_token = reset_token
        user.reset_token_expires = expiration
        db.session.commit()

        # Create the reset link for the web interface
        reset_base_url = current_app.config.get('BASE_URL', 'https://freshdealapi-fkfaajfaffh4c0ex.uksouth-01.azurewebsites.net')
        reset_link = f"{reset_base_url}/v1/reset-password/{reset_token}"

        # Send a user-friendly email
        subject = "Password Reset Request"
        message = f"""
        Hello,

        You have requested to reset your password. Please click the link below to set a new password:

        {reset_link}

        This link will expire in 1 hour.

        If you did not request this password reset, please ignore this email.

        Best regards,
        Your Application Team
        """

        send_email(email, subject, message)

        logger.info(f"Password reset token sent to: {email}")
        return {
            "success": True,
            "message": "Password reset instructions have been sent to your email.",
        }, 200

    except Exception as e:
        logger.error(f"Error during password reset initiation: {str(e)}")
        db.session.rollback()
        return {
            "success": False,
            "message": "An error occurred while processing your request.",
            "details": {"error_code": "SERVER_ERROR"}
        }, 500

def reset_password(data):
    """
    Complete the password reset process using the reset token.

    Expected data keys:
    - token: the reset token from the email
    - new_password: the new password to set

    Returns tuple (response dict, status code)
    """
    token = data.get("token")
    new_password = data.get("new_password")

    logger.info("Password reset attempt with token")

    if not token or not new_password:
        logger.info("Missing token or new password")
        return {
            "success": False,
            "message": "Token and new password are required",
            "details": {"error_code": "MISSING_REQUIRED_FIELDS"}
        }, 400

    # Find user with this token
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        logger.info("Invalid or expired reset token")
        return {
            "success": False,
            "message": "Invalid or expired reset token",
            "details": {"error_code": "INVALID_TOKEN"}
        }, 400

    # Check if token has expired - Make sure both times are timezone-aware
    current_time = datetime.now(UTC)
    if not user.reset_token_expires or user.reset_token_expires.replace(tzinfo=UTC) < current_time:
        logger.info(f"Expired reset token for user_id: {user.id}")
        return {
            "success": False,
            "message": "Reset token has expired",
            "details": {"error_code": "EXPIRED_TOKEN"}
        }, 400

    try:
        # Update password
        user.password = generate_password_hash(new_password)
        # Clear the reset token
        user.reset_token = None
        user.reset_token_expires = None

        db.session.commit()

        logger.info(f"Password reset successful for user_id: {user.id}")
        return {
            "success": True,
            "message": "Password has been reset successfully.",
        }, 200

    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        db.session.rollback()
        return {
            "success": False,
            "message": "An error occurred while resetting the password.",
            "details": {"error_code": "SERVER_ERROR"}
        }, 500