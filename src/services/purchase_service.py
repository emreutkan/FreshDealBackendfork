from sqlalchemy import and_

from src.models import db, UserCart, Listing, Purchase, Restaurant
from sqlalchemy.exc import SQLAlchemyError

from src.models.purchase_model import PurchaseStatus
def create_purchase_order_service(user_id, data=None):
    """
     Creates a pending purchase order
     data format:
     {
         "pickup_notes": "note text",  # optional
         "is_delivery": false,         # required, default false
         "delivery_address": "address" # required if is_delivery is true
     }
     """
    try:
        cart_items = UserCart.query.filter_by(user_id=user_id).all()

        if not cart_items:
            return {"message": "Cart is empty"}, 400

        purchases = []
        cart_items_to_clear = []

        # Get order type and notes from new format
        is_delivery = data.get('is_delivery', False) if data else False
        notes = data.get('pickup_notes') if not is_delivery else data.get('delivery_notes')
        delivery_address = data.get('delivery_address') if is_delivery else None

        for item in cart_items:
            listing = item.listing
            if not listing:
                return {"message": f"Listing (ID: {item.listing_id}) not found"}, 404

            # Validate stock
            if item.count > listing.count:
                return {
                    "message": f"Cannot purchase {item.count} of {listing.title}. Only {listing.count} left in stock."
                }, 400

            # Use appropriate price based on delivery type
            price_to_use = listing.delivery_price if is_delivery else listing.pick_up_price
            if price_to_use is None:
                price_to_use = listing.original_price


            restaurant = Restaurant.query.get(listing.restaurant_id)
            if not restaurant:
                return {"message": f"Restaurant (ID: {listing.restaurant_id}) not found"}, 404

            delivery_fee = restaurant.deliveryFee if is_delivery else 1

            # delivery_fee = listing.restaurant.delivery_fee if is_delivery else 1
            total_price = price_to_use * item.count * delivery_fee

            try:
                purchase = Purchase(
                    user_id=user_id,
                    listing_id=listing.id,
                    quantity=item.count,
                    restaurant_id=listing.restaurant_id,
                    total_price=total_price,
                    status=PurchaseStatus.PENDING,
                    is_delivery=is_delivery,
                    delivery_address=delivery_address,
                    delivery_notes=notes  # Added this line to save the notes
                )
            except ValueError as e:
                db.session.rollback()
                return {"message": str(e)}, 400

            # Decrease stock immediately
            if not listing.decrease_stock(item.count):
                db.session.rollback()
                return {
                    "message": f"Cannot create purchase. Not enough stock available for {listing.title}. Current stock: {listing.count}"
                }, 400

            db.session.add(purchase)
            purchases.append(purchase)
            cart_items_to_clear.append(item)

        # Clear cart items immediately after creating purchases
        for item in cart_items_to_clear:
            db.session.delete(item)

        db.session.commit()
        return {
            "message": "Purchase order created successfully, waiting for restaurant approval",
            "purchases": [p.to_dict() for p in purchases]  # Using new to_dict method
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

        if purchase.listing.restaurant_id != restaurant_id:
            return {"message": "Unauthorized"}, 403

        if action not in ['accept', 'reject']:
            return {"message": "Invalid action"}, 400

        try:
            new_status = PurchaseStatus.ACCEPTED if action == 'accept' else PurchaseStatus.REJECTED
            purchase.update_status(new_status)  # Using new status transition validation

            if action == 'reject':
                # Restore stock when rejected
                purchase.listing.count += purchase.quantity

            db.session.commit()
            return {
                "message": f"Purchase {action}ed successfully",
                "purchase": purchase.to_dict(include_relations=True)  # Using enhanced to_dict
            }, 200

        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": "Database error occurred", "error": str(e)}, 500
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

        try:
            purchase.completion_image_url = image_url
            purchase.update_status(PurchaseStatus.COMPLETED)  # Using new status transition validation
            db.session.commit()

            return {
                "message": "Completion image added successfully",
                "purchase": purchase.to_dict(include_relations=True)  # Using enhanced to_dict
            }, 200

        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400

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


def get_user_active_orders_service(user_id):
    """
    Get all active orders for a user (PENDING, ACCEPTED)
    """
    try:
        # Use the class method from the updated Purchase model
        active_orders = Purchase.get_active_purchases_for_user(user_id)

        return {
            "active_orders": [
                {
                    "purchase_id": order.id,
                    "restaurant_name": order.restaurant.restaurantName,
                    "listing_title": order.listing.title,
                    "quantity": order.quantity,
                    "total_price": order.formatted_total_price,  # Using new formatted_total_price property
                    "status": order.status.value,
                    "purchase_date": order.purchase_date.isoformat(),
                    "is_active": order.is_active,  # Added new property
                    "is_delivery": order.is_delivery,
                    "delivery_address": order.delivery_address if order.is_delivery else None,
                    "delivery_notes": order.delivery_notes if order.is_delivery else None,
                    "restaurant_details": {
                        "id": order.restaurant.id,
                        "name": order.restaurant.restaurantName,
                        "image_url": order.restaurant.image_url
                    }
                }
                for order in active_orders
            ]
        }, 200
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}, 500


def get_user_previous_orders_service(user_id, page=1, per_page=10):
    """
    Get completed or rejected orders for a user with pagination
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page

        # Query for completed and rejected orders
        previous_orders = Purchase.query.filter(
            and_(
                Purchase.user_id == user_id,
                Purchase.status.in_([PurchaseStatus.COMPLETED, PurchaseStatus.REJECTED])
            )
        ).order_by(Purchase.purchase_date.desc()) \
            .offset(offset) \
            .limit(per_page) \
            .all()

        # Get total count for pagination
        total_orders = Purchase.query.filter(
            and_(
                Purchase.user_id == user_id,
                Purchase.status.in_([PurchaseStatus.COMPLETED, PurchaseStatus.REJECTED])
            )
        ).count()

        # Calculate pagination metadata
        total_pages = (total_orders + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "orders": [
                order.to_dict(include_relations=True)  # Using enhanced to_dict method
                for order in previous_orders
            ],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "per_page": per_page,
                "total_orders": total_orders,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }, 200
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}, 500


# Add these helper methods to make the code more maintainable
def get_paginated_orders_query(user_id, status_list):
    """
    Helper method to create a base query for orders with specific statuses
    """
    return Purchase.query.filter(
        and_(
            Purchase.user_id == user_id,
            Purchase.status.in_(status_list)
        )
    ).order_by(Purchase.purchase_date.desc())


# You might also want to add this new service for getting order details
def get_order_details_service(user_id, purchase_id):
    """
    Get detailed information about a specific order
    """
    try:
        order = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()

        if not order:
            return {"message": "Order not found"}, 404

        return {
            "order": order.to_dict(include_relations=True)
        }, 200
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}, 500