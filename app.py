import os
import sqlalchemy
from flask import Flask, render_template, jsonify,send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from models import db
from routes import init_app
import yaml

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
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

    ### JWT Configuration ###
    app.config['JWT_SECRET_KEY'] = required_env_vars['JWT_SECRET_KEY']
    JWTManager(app)

    db.init_app(app)  # Initialize the database

    with app.app_context():
        db.create_all()

    # Check database connection
    try:
        engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        connection.close()
        print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

    init_app(app)  # Register the blueprints using the init_app function

    @app.route('/recreate_tables', methods=['POST'])
    def recreate_tables():
        with app.app_context():
            db.drop_all()
            db.create_all()
            return "All tables recreated!", 200

    ### Initialize CORS ###
    CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (adjust as needed)

    ### Serve Swagger
    ### Set up Swagger UI ###
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.yaml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI endpoint
        API_URL,  # Swagger spec URL
        config={  # Swagger UI config overrides
            'app_name': "FreshDeal API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    ### Serve Swagger YAML ###
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)
    ### Home Route ###
    @app.route('/')
    def index():
        return render_template('index.html')
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)
