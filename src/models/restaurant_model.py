import os

from . import db
from sqlalchemy import Integer, String, DECIMAL, Boolean, Float
from sqlalchemy.orm import validates, relationship

from datetime import datetime, UTC



class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    owner_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)

    restaurantName = db.Column(String(80), nullable=False)
    restaurantDescription = db.Column(String(500), nullable=True)
    restaurantEmail = db.Column(String(80), nullable=True)
    restaurantPhone = db.Column(String(20), nullable=True)
    longitude = db.Column(DECIMAL(9, 6), nullable=False)
    latitude = db.Column(DECIMAL(9, 6), nullable=False)
    category = db.Column(String(80), nullable=False)

    workingDays = db.Column(String(500), nullable=True)
    workingHoursStart = db.Column(String(5), nullable=True)
    workingHoursEnd = db.Column(String(5), nullable=True)

    listings = db.Column(Integer, nullable=False, default=0)
    rating = db.Column(DECIMAL(3, 2), nullable=True)
    ratingCount = db.Column(Integer, nullable=False, default=0)

    image_url = db.Column(String(2083), nullable=True)

    pickup = db.Column(Boolean, nullable=False, default=False)
    delivery = db.Column(Boolean, nullable=False, default=False)

    maxDeliveryDistance = db.Column(Float, nullable=True)  # Radius in kilometers
    deliveryFee = db.Column(DECIMAL(10, 2), nullable=True)
    minOrderAmount = db.Column(DECIMAL(10, 2), nullable=True)

    comments = relationship("RestaurantComment", back_populates="restaurant", cascade="all, delete-orphan")
    purchases = relationship('Purchase', back_populates='restaurant')

    @validates('workingDays')
    def validate_working_days(self, key, working_days):
        valid_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
        days_list = working_days.split(',')

        if not all(day in valid_days for day in days_list):
            raise ValueError(f"Working days must be one of {', '.join(valid_days)}")

        return working_days

    @validates('workingHoursStart', 'workingHoursEnd')
    def validate_working_hours(self, key, value):
        try:
            hours, minutes = map(int, value.split(':'))
            if not (0 <= hours < 24) or not (0 <= minutes < 60):
                raise ValueError("Time must be in HH:MM format with valid hour (00-23) and minute (00-59).")
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM (24-hour format).")

        return value

    @validates('rating')
    def validate_rating(self, key, rating):
        if rating is not None and not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0.00 and 5.00.")
        return rating

    def update_rating(self, new_rating):
        """Update the restaurant's average rating and rating count."""
        from decimal import Decimal
        new_rating = Decimal(str(new_rating))
        if self.rating is None:
                self.rating = new_rating
                self.ratingCount = 1
        else:
            total_rating = self.rating * self.ratingCount
            self.ratingCount += 1
            self.rating = (total_rating + new_rating) / self.ratingCount

    def update_listings_count(self, increment=True):
        """
        Updates the restaurant's listings count
        Args:
            increment (bool): True to increment, False to decrement
        """
        if increment:
            self.listings += 1
        else:
            self.listings = max(0, self.listings - 1)
        db.session.add(self)

    def try_delete_image_file(self, image_url):
        """
        Attempt to delete image file without raising exceptions.
        Returns (success, message) tuple.
        """
        from ..routes.restaurant_routes import UPLOAD_FOLDER

        if not image_url:
            return True, "No image to delete"

        try:
            filename = image_url.split('/')[-1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, f"Successfully deleted image: {filename}"
            return True, f"Image file not found: {filename}"
        except Exception as e:
            return False, f"Failed to delete image file: {str(e)}"

    @classmethod
    def delete_restaurant_service(cls, restaurant_id, owner_id):
        """
        Delete a restaurant by its ID if it is owned by the specified owner.
        """
        from .listing_model import Listing  # Import here to avoid circular imports

        restaurant = cls.query.get(restaurant_id)
        if not restaurant:
            return {"success": False, "message": f"Restaurant with ID {restaurant_id} not found."}, 404

        if str(owner_id) != str(restaurant.owner_id):
            return {"success": False, "message": "You are not the owner of this restaurant."}, 403

        deletion_log = []
        image_url = restaurant.image_url  # Store for later use

        try:
            # Get all listings before deleting them
            listings = Listing.query.filter_by(restaurant_id=restaurant_id).all()

            # Handle each listing individually
            for listing in listings:
                print(f"[{datetime.now(UTC)}] Attempting to delete listing {listing.id}")
                success, message = Listing.delete_listing(listing.id)
                deletion_log.append({
                    "listing_id": listing.id,
                    "success": success,
                    "message": message,
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                })

                if not success:
                    print(f"[{datetime.now(UTC)}] Warning: Issue with listing {listing.id}: {message}")

            # Delete the restaurant from database
            db.session.delete(restaurant)
            db.session.commit()

            # After successful database operations, try to delete the image file
            image_delete_success, image_delete_message = restaurant.try_delete_image_file(image_url)

            response = {
                "success": True,
                "message": f"Restaurant with ID {restaurant_id} deleted successfully",
                "details": {
                    "restaurant_id": restaurant_id,
                    "listings_processed": len(listings),
                    "deletion_log": deletion_log,
                    "image_deletion": {
                        "success": image_delete_success,
                        "message": image_delete_message
                    },
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                }
            }

            print(f"[{datetime.now(UTC)}] Successfully deleted restaurant {restaurant_id} "
                  f"and {len(listings)} listings")

            return response, 200

        except Exception as e:
            db.session.rollback()
            error_message = f"Error during restaurant deletion: {str(e)}"
            print(f"[{datetime.now(UTC)}] {error_message}")
            return {
                "success": False,
                "message": error_message,
                "details": {
                    "restaurant_id": restaurant_id,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                }
            }, 500