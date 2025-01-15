# services/cart_service.py
from src.models import db, UserCart, Listing

def get_cart_items_service(user_id):
    """
    Retrieve all cart items for the given user.
    """
    cart_items = UserCart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return [], 200

    cart = [
        {
            "id": item.id,
            "listing_id": item.listing_id,
            "title": item.listing.title,
            "count": item.count,
            "added_at": item.added_at
        }
        for item in cart_items
    ]
    return cart, 200


def add_to_cart_service(user_id, listing_id, count=1):
    """
    Add an item to the user's cart. If the item is already present,
    increment the count. Check if there's enough stock before committing.
    """
    # Check if the listing exists:
    listing = Listing.query.get(listing_id)
    if not listing:
        return {"message": "Listing not found"}, 404

    # Check if the item already exists in the cart:
    cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()

    # Calculate the new total quantity that the user wants to have in the cart
    new_quantity = (cart_item.count + count) if cart_item else count

    # Check if there is enough stock
    if new_quantity > listing.count:
        return {
            "message": (f"Insufficient stock for '{listing.title}'. "
                        f"Requested: {new_quantity}, Available: {listing.count}")
        }, 400

    # If there's enough stock, proceed
    if cart_item:
        cart_item.count = new_quantity
    else:
        cart_item = UserCart(user_id=user_id, listing_id=listing_id, count=new_quantity)
        db.session.add(cart_item)

    db.session.commit()
    return {"message": "Item added to cart"}, 201


def update_cart_item_service(user_id, listing_id, count):
    """
    Update the quantity of an item in the user's cart.
    Check if there's enough stock before committing.
    """
    cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()
    if not cart_item:
        return {"message": "Item not found in cart"}, 404

    listing = Listing.query.get(listing_id)
    if not listing:
        return {"message": "Listing not found"}, 404

    # Check if there is enough stock
    if count > listing.count:
        return {
            "message": (f"Insufficient stock for '{listing.title}'. "
                        f"Requested: {count}, Available: {listing.count}")
        }, 400

    cart_item.count = count
    db.session.commit()
    return {"message": "Cart item updated"}, 200


def remove_from_cart_service(user_id, listing_id):
    """
    Remove an item from the user's cart.
    """
    cart_item = UserCart.query.filter_by(user_id=user_id, listing_id=listing_id).first()
    if not cart_item:
        return {"message": "Item not found in cart"}, 404

    db.session.delete(cart_item)
    db.session.commit()
    return {"message": "Item removed from cart"}, 200
