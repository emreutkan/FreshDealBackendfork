from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user_model import User
from .address_model import CustomerAddress
from .restaurant_model import Restaurant
from .listing_model import Listing
from .user_favorites_model import UserFavorites
from .user_cart_model import UserCart
from .purchase_model import Purchase
from .restaurant_comments_model import RestaurantComment