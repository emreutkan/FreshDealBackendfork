# data_populator.py

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User  # Adjust the import path based on your project structure
import logging
import coloredlogs

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
coloredlogs.install(level='INFO', logger=logger, fmt=log_format)

def create_app():
    """
    Factory to create and configure the Flask app.
    Adjust configurations as necessary.
    """
    app = Flask(__name__)

    # Configuration
    # You can set the DATABASE_URI as an environment variable or hardcode it here
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///freshdeal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    return app

def populate_users(app):
    """
    Populate the database with sample users.
    """
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            logger.info("Database tables created or already exist.")

            # Define sample users
            sample_users = [
                {
                    "name": "John Doe",
                    "email": "johndoe@example.com",
                    "phone_number": "+14155552671",
                    "password": "SecurePass123",
                    "role": "customer"
                },
                {
                    "name": "Jane Smith",
                    "email": "janesmith@example.com",
                    "phone_number": "+14155552672",
                    "password": "AnotherPass456",
                    "role": "customer"
                },
                {
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "phone_number": "+14155552673",
                    "password": "StrongPass789",
                    "role": "owner"
                },
                {
                    "name": "Bob Brown",
                    "email": "bobbrown@example.com",
                    "phone_number": "+14155552674",
                    "password": "Password123",
                    "role": "owner"
                },
                # Add more users as needed
            ]

            for user_data in sample_users:
                # Check if user already exists by email or phone number
                existing_user = None
                if user_data.get("email"):
                    existing_user = User.query.filter_by(email=user_data["email"]).first()
                if not existing_user and user_data.get("phone_number"):
                    existing_user = User.query.filter_by(phone_number=user_data["phone_number"]).first()

                if existing_user:
                    logger.info(f"User already exists: {user_data['email'] or user_data['phone_number']}")
                    continue  # Skip to the next user

                # Create new user instance
                new_user = User(
                    name=user_data["name"],
                    email=user_data.get("email"),
                    phone_number=user_data.get("phone_number"),
                    password=generate_password_hash(user_data["password"]),
                    role=user_data["role"]
                )

                # Add to session
                db.session.add(new_user)
                logger.info(f"Added user: {new_user.email or new_user.phone_number}")

            # Commit the session
            db.session.commit()
            logger.info("All sample users have been added successfully.")

        except Exception as e:
            logger.error(f"An error occurred while populating users: {str(e)}")
            db.session.rollback()
            sys.exit(1)

def main():
    app = create_app()
    populate_users(app)

if __name__ == "__main__":
    main()
