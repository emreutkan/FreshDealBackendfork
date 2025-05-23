import json
import os
from datetime import datetime

def generate_purchases():
    """
    Generates one purchase per listing (40 total), assigns them round-robin to users 3–7,
    marks as COMPLETED, fills in address data, and flags flash-deals if present.
    """
    # load data
    with open('../exported_json/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    with open('../exported_json/listings.json', 'r', encoding='utf-8') as f:
        listings = json.load(f)

    # try to load flash deals so we can mark is_flash_deal
    flash_listing_ids = set()
    flash_path = '../exported_json/flash_deals.json'
    if os.path.exists(flash_path):
        with open(flash_path, 'r', encoding='utf-8') as f:
            flash_deals = json.load(f)
        flash_listing_ids = {fd['listing_id'] for fd in flash_deals}

    # load primary addresses
    with open('../exported_json/customeraddresses.json', 'r', encoding='utf-8') as f:
        addrs = json.load(f)
    primary_addrs = {a['user_id']: a for a in addrs if a.get('is_primary')}

    # customer IDs (from your script: 3–7)
    customer_ids = [u['id'] for u in users if u['role']=='customer']

    purchases = []
    pid = 1

    for idx, lst in enumerate(listings):
        user_id = customer_ids[idx % len(customer_ids)]
        addr = primary_addrs[user_id]

        # choose price: pickup if available, else delivery if available, else original
        if lst['available_for_pickup'] and lst['pick_up_price'] is not None:
            price = lst['pick_up_price']
            is_delivery = False
        elif lst['available_for_delivery'] and lst['delivery_price'] is not None:
            price = lst['delivery_price']
            is_delivery = True
        else:
            price = lst['original_price']
            is_delivery = False

        purchases.append({
            "id": pid,
            "user_id": user_id,
            "listing_id": lst['id'],
            "restaurant_id": lst['restaurant_id'],
            "quantity": 1,
            "total_price": price,
            "purchase_date": lst['created_at'],           # use listing creation as timestamp
            "status": "COMPLETED",
            "is_delivery": is_delivery,
            "is_flash_deal": lst['id'] in flash_listing_ids,
            "address_title": addr['title'],
            "delivery_address": addr['street'] + ", " + addr['neighborhood'] + ", " + addr['district'],
            "delivery_district": addr['district'],
            "delivery_province": addr['province'],
            "delivery_country": addr['country'],
            "delivery_notes": addr.get('delivery_instructions'),
            "completion_image_url": None
        })
        pid += 1

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/purchases.json', 'w', encoding='utf-8') as f:
        json.dump(purchases, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(purchases)} purchases to ../exported_json/purchases.json")

if __name__ == "__main__":
    generate_purchases()
