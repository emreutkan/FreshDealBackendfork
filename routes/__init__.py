from flask import Blueprint

from .auth_routes import auth_bp
from .customerAddressManager import customerAddressManager_bp
from .restaurantManager import restaurantManager_bp
from .user import user_bp
from .listings import listings_bp
from .cart import cart_bp
from .search import search_bp
from .Purchase import purchase_bp
def init_app(app):
    # Create a versioned API blueprint
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')

    # Register all version 1 blueprints under the API v1 blueprint
    api_v1.register_blueprint(auth_bp)
    api_v1.register_blueprint(customerAddressManager_bp)
    api_v1.register_blueprint(restaurantManager_bp)
    api_v1.register_blueprint(user_bp)
    api_v1.register_blueprint(listings_bp)
    api_v1.register_blueprint(cart_bp)
    api_v1.register_blueprint(search_bp)
    api_v1.register_blueprint(purchase_bp)
    # Register the versioned API blueprint with the main app
    app.register_blueprint(api_v1)