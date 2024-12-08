import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    ### Home Route ###
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/ping', methods=['GET'])
    def ping():
        return "Pong", 200

    ### Database Configuration ###
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    driver = os.getenv('DB_DRIVER')

    if not all([server, database, username, password, driver]):
        raise SystemExit("Error: Missing database environment variables")

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ### JWT Configuration ###
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret:
        raise SystemExit("Error: Missing JWT secret key")

    app.config['JWT_SECRET_KEY'] = jwt_secret
    JWTManager(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1212, debug=False)
