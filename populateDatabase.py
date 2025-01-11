from flask import current_app
from werkzeug.security import generate_password_hash
from models import db, User

def populate_users():
    """
    Populate the database with hashed passwords.
    """
    with current_app.app_context():
        try:
            # Create 'customer' users
            for i in range(0, 11):
                user = User(
                    name=f"name {i}",
                    email=f"{i}@",
                    phone_number=f"+90{i}",
                    password=generate_password_hash(f"{i}"),  # Hash passwords
                    role="customer"
                )
                db.session.add(user)

            # Create 'owner' users
            for i in range(11, 21):
                user = User(
                    name=f"name {i}",
                    email=f"{i}@",
                    phone_number=f"+90{i}",
                    password=generate_password_hash(f"{i}"),  # Hash passwords
                    role="owner"
                )
                db.session.add(user)

            db.session.commit()
            print("Users added successfully.")
        except Exception as e:
            print(f"Error adding users: {e}")
            db.session.rollback()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        populate_users()
