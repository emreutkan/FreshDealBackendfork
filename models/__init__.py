from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .customerAddress import CustomerAddress
from .restaurant import Restaurant
from .listings import Listing
from .userFavorites import UserFavorites