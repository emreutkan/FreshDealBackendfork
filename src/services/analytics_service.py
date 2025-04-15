from datetime import datetime
from sqlalchemy import func, and_
from src.models import db, Restaurant, Purchase, PurchaseStatus, RestaurantComment
from decimal import Decimal


class RestaurantAnalyticsService:
    @staticmethod
    def get_owner_analytics(owner_id):
        """Get analytics for all restaurants owned by the user"""
        # Get the start date for current month
        today = datetime.utcnow()
        start_date = datetime(today.year, today.month, 1)

        # Get all restaurants owned by the user
        restaurants = Restaurant.query.filter_by(owner_id=owner_id).all()
        restaurant_ids = [r.id for r in restaurants]

        if not restaurant_ids:
            return {
                "success": False,
                "message": "No restaurants found for this owner"
            }, 404

        # Get all completed purchases for the month
        monthly_purchases = Purchase.query.filter(
            Purchase.restaurant_id.in_(restaurant_ids),
            Purchase.status == PurchaseStatus.COMPLETED,
            Purchase.purchase_date >= start_date
        ).all()

        # Calculate monthly metrics
        monthly_products = sum(p.quantity for p in monthly_purchases)
        monthly_revenue = sum(Decimal(p.total_price) for p in monthly_purchases)

        # Calculate regional distribution from delivery addresses
        regions = {}
        for purchase in monthly_purchases:
            if purchase.delivery_address:
                # Split address and get district/region
                parts = purchase.delivery_address.split(',')
                district = parts[2].strip() if len(parts) > 2 else 'Unknown'
                regions[district] = regions.get(district, 0) + 1

        # Get ratings and comments for all owner's restaurants
        restaurant_stats = {}
        for restaurant in restaurants:
            comments = RestaurantComment.query.filter_by(restaurant_id=restaurant.id) \
                .order_by(RestaurantComment.timestamp.desc()).all()

            restaurant_stats[restaurant.restaurantName] = {
                "id": restaurant.id,
                "average_rating": float(restaurant.rating) if restaurant.rating else 0,
                "total_ratings": restaurant.ratingCount,
                "recent_comments": [{
                    "user_name": comment.user.name,
                    "rating": float(comment.rating),
                    "comment": comment.comment,
                    "timestamp": comment.timestamp.isoformat()
                } for comment in comments[:5]]  # Get 5 most recent comments
            }

        return {
            "success": True,
            "data": {
                "monthly_stats": {
                    "total_products_sold": monthly_products,
                    "total_revenue": str(monthly_revenue),
                    "period": f"{today.year}-{today.month:02d}"
                },
                "regional_distribution": regions,
                "restaurant_ratings": restaurant_stats
            }
        }, 200