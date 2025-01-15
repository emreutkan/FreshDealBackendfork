from src.models import db, UserCart, Listing, Purchase, Restaurant
from sqlalchemy.exc import SQLAlchemyError

from src.models.purchase_model import PurchaseStatus


def create_purchase_order_service(user_id, delivery_info=None):
    """
    First step: Creates a pending purchase order
    """
    try:
        cart_items = UserCart.query.filter_by(user_id=user_id).all()

        if not cart_items:
            return {"message": "Cart is empty"}, 400

        purchases = []
        for item in cart_items:
            listing = item.listing
            if not listing:
                return {"message": f"Listing (ID: {item.listing_id}) not found"}, 404

            # Validate stock
            if item.count > listing.count:
                return {
                    "message": f"Cannot purchase {item.count} of {listing.title}. Only {listing.count} left in stock."
                }, 400

            price_to_use = (listing.pick_up_price if not delivery_info
                            else listing.delivery_price
                                 or listing.original_price)

            total_price = price_to_use * item.count

            # Create pending purchase record
            purchase = Purchase(
                user_id=user_id,
                listing_id=listing.id,
                quantity=item.count,
                total_price=total_price,
                status=PurchaseStatus.PENDING,
                is_delivery=bool(delivery_info),
                delivery_address=delivery_info.get('address') if delivery_info else None,
                delivery_notes=delivery_info.get('notes') if delivery_info else None
            )
            db.session.add(purchase)
            purchases.append(purchase)

        db.session.commit()
        return {
            "message": "Purchase order created successfully, waiting for restaurant approval",
            "purchases": [
                {
                    "purchase_id": p.id,
                    "listing_id": p.listing_id,
                    "quantity": p.quantity,
                    "total_price": str(p.total_price),
                    "status": p.status.value
                }
                for p in purchases
            ]
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"message": "An error occurred", "error": str(e)}, 500


def handle_restaurant_response_service(purchase_id, restaurant_id, action, completion_image=None):
    """
    Second step: Restaurant accepts or rejects the order
    """
    try:
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return {"message": "Purchase not found"}, 404

        # Verify the restaurant owns this listing
        if purchase.listing.restaurant_id != restaurant_id:
            return {"message": "Unauthorized"}, 403

        if action not in ['accept', 'reject']:
            return {"message": "Invalid action"}, 400

        if action == 'accept':
            purchase.status = PurchaseStatus.ACCEPTED

            # Handle the actual stock reduction here
            listing = purchase.listing
            listing.count -= purchase.quantity
            if listing.count == 0:
                restaurant = Restaurant.query.get(listing.restaurant_id)
                if restaurant and restaurant.listings > 0:
                    restaurant.listings -= 1

            # Clear cart items
            UserCart.query.filter_by(
                user_id=purchase.user_id,
                listing_id=purchase.listing_id
            ).delete()

        else:  # reject
            purchase.status = PurchaseStatus.REJECTED

        db.session.commit()
        return {
            "message": f"Purchase {action}ed successfully",
            "purchase_id": purchase.id,
            "status": purchase.status.value
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"message": "An error occurred", "error": str(e)}, 500


def add_completion_image_service(purchase_id, restaurant_id, image_url):
    """
    Add completion image to an accepted purchase
    """
    try:
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return {"message": "Purchase not found"}, 404

        if purchase.listing.restaurant_id != restaurant_id:
            return {"message": "Unauthorized"}, 403

        if purchase.status != PurchaseStatus.ACCEPTED:
            return {"message": "Purchase must be accepted to add completion image"}, 400

        purchase.completion_image_url = image_url
        purchase.status = PurchaseStatus.COMPLETED
        db.session.commit()

        return {
            "message": "Completion image added successfully",
            "purchase_id": purchase.id,
            "image_url": image_url
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"message": "An error occurred", "error": str(e)}, 500

# In your purchase_service.py

def get_restaurant_purchases_service(restaurant_id):
    """
    Get all purchases for a restaurant
    """
    try:
        purchases = Purchase.get_restaurant_purchases(restaurant_id)
        return {
            "purchases": [purchase.to_dict() for purchase in purchases]
        }, 200
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}, 500