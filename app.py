import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes import init_app

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    @app.route('/ping', methods=['GET'])
    def ping():
        return "Pong", 200

    ### Database Configuration ###
    required_env_vars = {
        "DB_SERVER": os.getenv("DB_SERVER"), # test
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USERNAME": os.getenv("DB_USERNAME"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_DRIVER": os.getenv("DB_DRIVER"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
    }

    # Check for missing environment variables
    missing_vars = [var for var, value in required_env_vars.items() if not value]
    if missing_vars:
        raise SystemExit(f"Error: Missing environment variables: {', '.join(missing_vars)}")

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mssql+pyodbc://{required_env_vars['DB_USERNAME']}:"
        f"{required_env_vars['DB_PASSWORD']}@"
        f"{required_env_vars['DB_SERVER']}/"
        f"{required_env_vars['DB_NAME']}?driver={required_env_vars['DB_DRIVER']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ### JWT Configuration ###
    app.config['JWT_SECRET_KEY'] = required_env_vars['JWT_SECRET_KEY']
    JWTManager(app)

    db.init_app(app)  # Initialize the database
    init_app(app)  # Register the blueprints using the init_app function

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)
