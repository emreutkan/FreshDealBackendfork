import json
import os
import random
from datetime import datetime, timedelta

def generate_purchases():
    """
    Generates multiple purchases per user with overlapping listings to create
    better data for the recommendation system. Each customer will buy several
    listings with some intentional overlap to create patterns.
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

    # Create purchase clusters - groups of listings that certain user groups tend to buy together
    # This creates more meaningful patterns for the recommendation system
    listing_ids = [lst['id'] for lst in listings]

    # Cluster 1: Common items everyone buys (staples)
    common_items = random.sample(listing_ids, min(5, len(listing_ids)))

    # Cluster 2-4: Preference clusters (items that certain users prefer)
    preference_clusters = []
    remaining_listings = [lid for lid in listing_ids if lid not in common_items]

    # Create 3 preference clusters if we have enough listings
    cluster_count = min(3, len(remaining_listings) // 5)
    for i in range(cluster_count):
        if remaining_listings:
            cluster_size = min(len(remaining_listings), random.randint(4, 8))
            cluster = random.sample(remaining_listings, cluster_size)
            preference_clusters.append(cluster)
            remaining_listings = [lid for lid in remaining_listings if lid not in cluster]

    # Assign user preferences (which clusters they prefer)
    user_preferences = {}
    for user_id in customer_ids:
        # Each user likes 1-2 preference clusters plus the common items
        preferred_clusters = random.sample(range(len(preference_clusters)),
                                           min(random.randint(1, 2), len(preference_clusters)))
        user_preferences[user_id] = {
            'common': common_items,
            'preferences': [preference_clusters[i] for i in preferred_clusters]
        }

    purchases = []
    pid = 1

    # Generate base date for purchases
    base_date = datetime.now() - timedelta(days=30)  # Purchases over the last 30 days

    # Generate purchases for each user based on their preferences
    for user_id in customer_ids:
        user_listings = []

        # Add all common items
        user_listings.extend(user_preferences[user_id]['common'])

        # Add items from their preferred clusters
        for cluster in user_preferences[user_id]['preferences']:
            user_listings.extend(cluster)

        # Add a few random items for diversity
        random_count = random.randint(1, 3)
        random_listings = [lid for lid in listing_ids if lid not in user_listings]
        if random_listings:
            user_listings.extend(random.sample(random_listings, min(random_count, len(random_listings))))

        # Remove potential duplicates
        user_listings = list(set(user_listings))

        # For each listing this user will purchase
        for lst_id in user_listings:
            # Find the corresponding listing
            lst = next((l for l in listings if l['id'] == lst_id), None)
            if not lst:
                continue

            addr = primary_addrs[user_id]

            # Random purchase date within the last 30 days
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            purchase_date = base_date + timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            purchase_date_str = purchase_date.strftime("%Y-%m-%d %H:%M:%S")

            # Choose price: pickup if available, else delivery if available, else original
            if lst['available_for_pickup'] and lst['pick_up_price'] is not None:
                price = lst['pick_up_price']
                is_delivery = False
            elif lst['available_for_delivery'] and lst['delivery_price'] is not None:
                price = lst['delivery_price']
                is_delivery = True
            else:
                price = lst['original_price']
                is_delivery = False

            # Random quantity between 1 and 3
            quantity = random.randint(1, 3)
            total_price = price * quantity

            purchases.append({
                "id": pid,
                "user_id": user_id,
                "listing_id": lst_id,
                "restaurant_id": lst['restaurant_id'],
                "quantity": quantity,
                "total_price": total_price,
                "purchase_date": purchase_date_str,
                "status": "COMPLETED",
                "is_delivery": is_delivery,
                "is_flash_deal": lst_id in flash_listing_ids,
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
