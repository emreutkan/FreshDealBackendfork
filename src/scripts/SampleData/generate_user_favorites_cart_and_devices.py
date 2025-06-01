import json
import os
import random
from datetime import datetime, timezone


def generate_user_favorites_cart_and_devices():
    """
    Generates three files:
      - user_favorites.json: each customer (IDs 3-7) has 0-3 favorite restaurants, no duplicates.
      - user_cart.json: empty list (no cart items).
      - user_devices.json: empty list (no devices).
    """
    random.seed(42)

    # load users, restaurants, listings
    with open('../exported_json/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    with open('../exported_json/restaurants.json', 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    with open('../exported_json/listings.json', 'r', encoding='utf-8') as f:
        listings = json.load(f)

    # filter customer IDs
    customer_ids = [u['id'] for u in users if u['role']=='customer']
    restaurant_ids = [r['id'] for r in restaurants]
    listing_map = {l['id']: l for l in listings}

    # generate favorites
    favorites = []
    fav_id = 1
    for uid in customer_ids:
        num_fav = random.randint(0, 3)
        fav_restaurants = random.sample(restaurant_ids, num_fav)
        for rid in fav_restaurants:
            favorites.append({
                'id': fav_id,
                'user_id': uid,
                'restaurant_id': rid
            })
            fav_id += 1

    # generate cart items
    cart_items = []  # All carts empty

    # devices: empty
    devices = []

    # ensure output dir
    os.makedirs('../exported_json', exist_ok=True)

    # write JSON files
    with open('../exported_json/user_favorites.json', 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
    with open('../exported_json/user_cart.json', 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)  # Always empty
    with open('../exported_json/user_devices.json', 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

    print(f"Saved {len(favorites)} favorites, {len(cart_items)} cart items, and {len(devices)} devices to ../exported_json/")


if __name__ == '__main__':
    generate_user_favorites_cart_and_devices()
