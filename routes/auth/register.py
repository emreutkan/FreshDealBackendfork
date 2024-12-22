from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number
from models import db, User

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    name_surname = data.get("name_surname")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")

    if not email and not phone_number:
        return jsonify({"success": False, "message": "Email or phone number is required"}), 400

    if not password:
        return jsonify({"success": False, "message": "Password is required"}), 400

    print(name_surname)
    if not name_surname:
        return jsonify({"success": False, "message": "Name is required"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User()

    if email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "message": "Email already exists"}), 409  # 409 conflict

        new_user = User(
            name=name_surname,
            email=email,
            password=hashed_password,
            role='customer'
        )

    if phone_number:
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not is_valid_number(parsed_number):
                return jsonify({"success": False, "message": "Invalid phone number"}), 400
        except NumberParseException:
            return jsonify({"success": False, "message": "Invalid phone number format"}), 400

        existing_phone_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_phone_user:
            return jsonify({"success": False, "message": "Phone number already exists"}), 409

        new_user = User(
            name=name_surname,
            phone_number=phone_number,
            password=hashed_password,
            role='customer'
        )

    hashed_password = generate_password_hash(password)
    # Map the incoming field 'name_surname' to 'name'

    if email and phone_number:
        new_user = User(
            name=name_surname,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            role='customer'
        )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

    # new_user = User(email=email, phone_number=phone_number, password=hashed_password)
    # db.session.add(new_user)
    # db.session.commit()
    #
    # return jsonify({"success": True, "message": "User registered successfully"}), 201  # 201 created
