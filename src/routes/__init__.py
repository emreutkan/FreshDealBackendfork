from flask import Blueprint

from src.routes.auth_routes import auth_bp
from src.routes.address_routes import addresses_bp
from src.routes.report_routes import report_bp
from src.routes.restaurant_routes import restaurant_bp
from src.routes.user_routes import user_bp
from src.routes.listing_routes import listings_bp
from src.routes.cart_routes import cart_bp
from src.routes.search_routes import search_bp
from src.routes.purchase_routes import purchase_bp
def init_app(app):
    # Create a versioned API blueprint
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')

    # Register all version 1 blueprints under the API v1 blueprint
    api_v1.register_blueprint(auth_bp)
    api_v1.register_blueprint(addresses_bp)
    api_v1.register_blueprint(restaurant_bp)
    api_v1.register_blueprint(user_bp)
    api_v1.register_blueprint(listings_bp)
    api_v1.register_blueprint(cart_bp)
    api_v1.register_blueprint(search_bp)
    api_v1.register_blueprint(purchase_bp)
    api_v1.register_blueprint(report_bp)
    # Register the versioned API blueprint with the main app
    app.register_blueprint(api_v1)