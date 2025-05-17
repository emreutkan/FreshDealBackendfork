import json
import random
from datetime import datetime, timedelta, timezone, UTC
import uuid
import os
import hashlib


def generate_sample_data():
    # Check if data already exists
    if os.path.exists('../exported_json/users.json') and os.path.exists('../exported_json/restaurants.json'):
        print("Sample data already loaded.")
        return

    # Create export directory if it doesn't exist
    os.makedirs('../exported_json', exist_ok=True)

    # Set random seed for reproducibility
    random.seed(42)

    # Generate users (owners and customers)
    users = []

    # Create 10 restaurant owners
    for i in range(10):
        owner = {
            "id": i + 1,
            "name": f"{random.choice(['Ali', 'Ahmet', 'Mehmet', 'Mustafa', 'Hüseyin', 'Ibrahim', 'Murat', 'Kemal', 'Osman', 'Serkan'])} {random.choice(['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Öztürk', 'Aydın', 'Yıldız', 'Koç', 'Özdemir'])}",
            "email": f"owner{i + 1}@example.com",
            "phone_number": "+905078905011" if i == 0 else f"+9053{random.randint(10000000, 99999999)}",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "owner",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
        users.append(owner)

    # Create 20 customers
    for i in range(20):
        customer = {
            "id": i + 11,
            "name": f"{random.choice(['Ali', 'Ayşe', 'Mehmet', 'Fatma', 'Mustafa', 'Zeynep', 'Ahmet', 'Emine', 'Hüseyin', 'Elif'])} {random.choice(['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Öztürk', 'Aydın', 'Yıldız', 'Koç', 'Özdemir'])}",
            "email": f"customer{i + 1}@example.com",
            "phone_number": "+905078905010" if i == 0 else f"+9053{random.randint(10000000, 99999999)}",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
        users.append(customer)

    # Create 3 support team members
    for i in range(3):
        support = {
            "id": i + 31,
            "name": f"{random.choice(['Support', 'Admin', 'Helper'])} {i + 1}",
            "email": f"support{i + 1}@example.com",
            "phone_number": f"+9053{random.randint(10000000, 99999999)}",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "support",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
        users.append(support)

    # Generate customer addresses
    addresses = []
    customer_ids = [user["id"] for user in users if user["role"] == "customer"]

    for customer_id in customer_ids:
        num_addresses = random.randint(3, 5)
        for j in range(num_addresses):
            district = random.choice(["Karşıyaka", "Bornova"])
            neighborhood = random.choice([
                                             "Bostanlı", "Atakent", "Mavişehir", "Alaybey", "Tersane"
                                         ] if district == "Karşıyaka" else [
                "Atatürk", "Evka 3", "Evka 4", "Kazımdirik", "Özkanlar"
            ])

            address = {
                "id": len(addresses) + 1,
                "user_id": customer_id,
                "title": random.choice(["Ev", "İş", "Yazlık", "Kış Evi", "Arkadaş Evi"]),
                "longitude": float(27.1 + random.random() * 0.1),
                "latitude": float(38.4 + random.random() * 0.1),
                "street": f"{random.randint(1, 100)}. Sokak",
                "neighborhood": neighborhood,
                "district": district,
                "province": "İzmir",
                "country": "Türkiye",
                "postalCode": f"35{random.randint(100, 999)}",
                "apartmentNo": random.randint(1, 20),
                "doorNo": str(random.randint(1, 50)),
                "is_primary": j == 0  # First address is primary
            }
            addresses.append(address)

    # Generate restaurants
    restaurants = []
    owner_ids = [user["id"] for user in users if user["role"] == "owner"]

    for i, owner_id in enumerate(owner_ids):
        district = random.choice(["Karşıyaka", "Bornova"])
        neighborhood = random.choice([
                                         "Bostanlı", "Atakent", "Mavişehir", "Alaybey", "Tersane"
                                     ] if district == "Karşıyaka" else [
            "Atatürk", "Evka 3", "Evka 4", "Kazımdirik", "Özkanlar"
        ])

        restaurant_name = f"{random.choice(['Lezzet', 'Tadım', 'Keyif', 'Sofra', 'Afiyet'])} {random.choice(['Restaurant', 'Cafe', 'Köşesi', 'Yeri', 'Lokantası'])}"

        restaurant = {
            "id": i + 1,
            "owner_id": owner_id,
            "restaurantName": restaurant_name,
            "restaurantDescription": f"{restaurant_name} - En taze ve lezzetli yemekleri sunan işletme",
            "restaurantEmail": f"info@{restaurant_name.lower().replace(' ', '')}.com",
            "restaurantPhone": f"+9053{random.randint(10000000, 99999999)}",
            "longitude": float(27.1 + random.random() * 0.1),
            "latitude": float(38.4 + random.random() * 0.1),
            "category": random.choice(
                ["Turkish", "Italian", "Fast Food", "Chinese", "Seafood", "Kebab", "Bakery", "Dessert", "Breakfast",
                 "Vegan"]),
            "workingDays": "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday",
            "workingHoursStart": f"{random.randint(8, 11)}:00",
            "workingHoursEnd": f"{random.randint(19, 23)}:00",
            "listings": 0,
            "rating": float(round(3.5 + random.random() * 1.5, 2)),
            "ratingCount": random.randint(0, 100),
            "image_url": f"https://example.com/images/restaurants/{i + 1}.jpg",
            "pickup": True,
            "delivery": random.choice([True, False]),
            "maxDeliveryDistance": random.uniform(1.0, 5.0) if random.choice([True, False]) else None,
            "deliveryFee": float(round(random.uniform(5.0, 20.0), 2)) if random.choice([True, False]) else None,
            "minOrderAmount": float(round(random.uniform(20.0, 50.0), 2)) if random.choice([True, False]) else None,
            "flash_deals_available": random.choice([True, False]),
            "flash_deals_count": random.randint(0, 5)
        }
        restaurants.append(restaurant)

    # Generate restaurant badge points
    restaurant_badge_points = []
    for restaurant in restaurants:
        badge_points = {
            "id": restaurant["id"],
            "restaurantID": restaurant["id"],
            "freshPoint": random.randint(0, 100),
            "fastDeliveryPoint": random.randint(0, 100),
            "customerFriendlyPoint": random.randint(0, 100),
            "notFreshPoint": random.randint(0, 20),
            "slowDeliveryPoint": random.randint(0, 20),
            "notCustomerFriendlyPoint": random.randint(0, 20)
        }
        restaurant_badge_points.append(badge_points)

    # Generate categories (new)
    categories = [
        {"id": 1, "name": "Turkish", "icon": "🇹🇷", "display_order": 1},
        {"id": 2, "name": "Italian", "icon": "🍕", "display_order": 2},
        {"id": 3, "name": "Fast Food", "icon": "🍔", "display_order": 3},
        {"id": 4, "name": "Chinese", "icon": "🥢", "display_order": 4},
        {"id": 5, "name": "Seafood", "icon": "🐟", "display_order": 5},
        {"id": 6, "name": "Kebab", "icon": "🍖", "display_order": 6},
        {"id": 7, "name": "Bakery", "icon": "🥐", "display_order": 7},
        {"id": 8, "name": "Dessert", "icon": "🍰", "display_order": 8},
        {"id": 9, "name": "Breakfast", "icon": "☕", "display_order": 9},
        {"id": 10, "name": "Vegan", "icon": "🥗", "display_order": 10}
    ]

    # Generate restaurant categories (mapping) (new)
    restaurant_categories = []
    category_id = 1

    for restaurant in restaurants:
        # Each restaurant gets its main category plus 0-2 additional categories
        main_category_name = restaurant["category"]
        main_category_id = next(cat["id"] for cat in categories if cat["name"] == main_category_name)

        restaurant_categories.append({
            "id": category_id,
            "restaurant_id": restaurant["id"],
            "category_id": main_category_id,
            "is_primary": True
        })
        category_id += 1

        # Add 0-2 additional categories
        num_additional = random.randint(0, 2)
        available_categories = [c for c in categories if c["name"] != main_category_name]

        if num_additional > 0 and available_categories:
            additional_cats = random.sample(available_categories, min(num_additional, len(available_categories)))
            for cat in additional_cats:
                restaurant_categories.append({
                    "id": category_id,
                    "restaurant_id": restaurant["id"],
                    "category_id": cat["id"],
                    "is_primary": False
                })
                category_id += 1

    # Generate menu categories (new)
    menu_categories = []
    menu_cat_id = 1

    for restaurant in restaurants:
        # Each restaurant has 3-5 menu categories
        num_categories = random.randint(3, 5)
        categories_added = []

        for j in range(num_categories):
            category_name = random.choice([
                "Başlangıçlar", "Ana Yemekler", "Tatlılar", "İçecekler", "Burgerler",
                "Pizzalar", "Salatalar", "Çorbalar", "Kahvaltı", "Ara Sıcaklar",
                "Makarnalar", "Tavuk Menüler", "Vejeteryan", "Mezeler", "Özel Menüler"
            ])

            # Avoid duplicate category names for the same restaurant
            while category_name in categories_added:
                category_name = random.choice([
                    "Başlangıçlar", "Ana Yemekler", "Tatlılar", "İçecekler", "Burgerler",
                    "Pizzalar", "Salatalar", "Çorbalar", "Kahvaltı", "Ara Sıcaklar",
                    "Makarnalar", "Tavuk Menüler", "Vejeteryan", "Mezeler", "Özel Menüler"
                ])

            categories_added.append(category_name)

            menu_categories.append({
                "id": menu_cat_id,
                "restaurant_id": restaurant["id"],
                "name": category_name,
                "description": f"{restaurant['restaurantName']} restoranın {category_name} kategorisi",
                "display_order": j + 1
            })
            menu_cat_id += 1

    # Generate listings
    listings = []
    for restaurant in restaurants:
        # Get menu categories for this restaurant
        rest_menu_categories = [c for c in menu_categories if c["restaurant_id"] == restaurant["id"]]

        num_listings = random.randint(5, 10)
        restaurant["listings"] = num_listings

        for j in range(num_listings):
            consume_within = random.randint(6, 48)
            expires_at = datetime.now(UTC) + timedelta(hours=consume_within)

            original_price = round(random.uniform(30.0, 150.0), 2)
            pickup_price = round(original_price * 0.7, 2) if restaurant["pickup"] else None
            delivery_price = round(original_price * 0.8, 2) if restaurant["delivery"] else None

            # Assign to a random menu category for this restaurant
            menu_category = random.choice(rest_menu_categories) if rest_menu_categories else None

            listing = {
                "id": len(listings) + 1,
                "restaurant_id": restaurant["id"],
                "menu_category_id": menu_category["id"] if menu_category else None,
                "title": f"{random.choice(['Taze', 'Günlük', 'Özel', 'Lezzetli'])} {random.choice(['Menü', 'Tabak', 'Porsiyon', 'Paket'])}",
                "description": "Günün sonunda kalan taze yiyecekleri değerlendirmek için indirimli fiyatla sunuyoruz.",
                "image_url": f"https://example.com/images/listings/{len(listings) + 1}.jpg",
                "count": random.randint(1, 10),
                "original_price": original_price,
                "pick_up_price": pickup_price,
                "delivery_price": delivery_price,
                "consume_within": consume_within,
                "consume_within_type": "HOURS",
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 7))).strftime(
                    "%Y-%m-%d %H:%M:%S"),
                "update_count": 0,
                "fresh_score": 100.0,
                "available_for_pickup": restaurant["pickup"],
                "available_for_delivery": restaurant["delivery"]
            }
            listings.append(listing)

    # Generate flash deals (new)
    flash_deals = []
    flash_deal_id = 1

    for restaurant in restaurants:
        if restaurant["flash_deals_available"]:
            # Generate 1-3 flash deals for eligible restaurants
            num_deals = random.randint(1, 3)
            restaurant_listings = [l for l in listings if l["restaurant_id"] == restaurant["id"]]

            if restaurant_listings:
                # Choose random listings for this restaurant to make flash deals
                deal_listings = random.sample(restaurant_listings, min(num_deals, len(restaurant_listings)))

                for listing in deal_listings:
                    # Flash deals have even deeper discounts
                    flash_discount = random.randint(30, 50)  # 30-50% discount
                    flash_price = round(listing["original_price"] * (100 - flash_discount) / 100, 2)

                    # Flash deals expire more quickly
                    start_time = datetime.now(UTC) + timedelta(hours=random.randint(1, 12))
                    end_time = start_time + timedelta(hours=random.randint(1, 6))

                    flash_deal = {
                        "id": flash_deal_id,
                        "restaurant_id": restaurant["id"],
                        "listing_id": listing["id"],
                        "flash_price": flash_price,
                        "discount_percentage": flash_discount,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_active": True,
                        "quantity_available": random.randint(1, 5),
                        "quantity_sold": 0
                    }
                    flash_deals.append(flash_deal)
                    flash_deal_id += 1

    # Generate purchases
    purchases = []
    purchase_statuses = ["PENDING", "ACCEPTED", "COMPLETED", "REJECTED"]
    status_weights = [0.15, 0.15, 0.6, 0.1]

    for i in range(100):
        customer = random.choice([user for user in users if user["role"] == "customer"])
        listing = random.choice(listings)
        restaurant = next(r for r in restaurants if r["id"] == listing["restaurant_id"])

        # Get an address for this customer
        customer_address = random.choice([a for a in addresses if a["user_id"] == customer["id"]])

        # Determine if this is a delivery or pickup
        is_delivery = random.choice([True, False]) if restaurant["delivery"] else False

        # Determine if this is a flash deal purchase
        listing_flash_deals = [fd for fd in flash_deals if fd["listing_id"] == listing["id"]]
        is_flash_deal = bool(listing_flash_deals) and random.random() < 0.3  # 30% chance if flash deal exists

        # Calculate price based on delivery/pickup and flash deal status
        quantity = random.randint(1, 3)
        if is_flash_deal and listing_flash_deals:
            flash_deal = random.choice(listing_flash_deals)
            total_price = quantity * flash_deal["flash_price"]
            flash_deal["quantity_sold"] += quantity
        elif is_delivery and listing["delivery_price"]:
            total_price = quantity * listing["delivery_price"]
        elif not is_delivery and listing["pick_up_price"]:
            total_price = quantity * listing["pick_up_price"]
        else:
            total_price = quantity * listing["original_price"] * 0.7  # Default discount

        # Generate purchase date (within the last 30 days)
        purchase_date = datetime.now(UTC) - timedelta(days=random.randint(0, 30))

        # Select status weighted by probability
        status = random.choices(purchase_statuses, status_weights)[0]

        # Only completed orders have a completion image
        completion_image_url = f"https://example.com/images/completions/{i + 1}.jpg" if status == "COMPLETED" else None

        purchase = {
            "id": i + 1,
            "user_id": customer["id"],
            "listing_id": listing["id"],
            "restaurant_id": restaurant["id"],
            "quantity": quantity,
            "total_price": float(round(total_price, 2)),
            "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "is_delivery": is_delivery,
            "is_flash_deal": is_flash_deal,
            "address_title": customer_address["title"],
            "delivery_address": f"{customer_address['street']}, {customer_address['neighborhood']}, {customer_address['district']}",
            "delivery_district": customer_address["district"],
            "delivery_province": customer_address["province"],
            "delivery_country": customer_address["country"],
            "delivery_notes": "Lütfen kapıya bırakınız." if is_delivery else None,
            "completion_image_url": completion_image_url
        }
        purchases.append(purchase)

    # Generate purchase status history (new)
    purchase_status_history = []
    status_history_id = 1

    for purchase in purchases:
        # All purchases start as PENDING
        purchase_status_history.append({
            "id": status_history_id,
            "purchase_id": purchase["id"],
            "status": "PENDING",
            "timestamp": purchase["purchase_date"],
            "notes": "Sipariş oluşturuldu."
        })
        status_history_id += 1

        # If not still pending, add accepted status
        if purchase["status"] != "PENDING":
            accepted_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                minutes=random.randint(5, 15))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "ACCEPTED",
                "timestamp": accepted_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Sipariş restoran tarafından kabul edildi."
            })
            status_history_id += 1

        # If completed, add preparing, ready, and completed statuses
        if purchase["status"] == "COMPLETED":
            # Preparing
            preparing_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                minutes=random.randint(20, 30))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "PREPARING",
                "timestamp": preparing_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Siparişiniz hazırlanıyor."
            })
            status_history_id += 1

            # Ready
            ready_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                minutes=random.randint(35, 50))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "READY",
                "timestamp": ready_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Siparişiniz hazır." if not purchase["is_delivery"] else "Siparişiniz teslimata hazır."
            })
            status_history_id += 1

            # Completed
            completed_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                minutes=random.randint(55, 90))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "COMPLETED",
                "timestamp": completed_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Sipariş teslim edildi."
            })
            status_history_id += 1

        # If rejected, add rejection status
        elif purchase["status"] == "REJECTED":
            rejected_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                minutes=random.randint(5, 20))
            reason = random.choice([
                "Restoran çok yoğun.",
                "Ürün stokta kalmadı.",
                "Restoran kapanma saati yaklaştı.",
                "Teslimat bölgesi çok uzak."
            ])
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "REJECTED",
                "timestamp": rejected_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": f"Sipariş reddedildi. Sebep: {reason}"
            })
            status_history_id += 1

    # Generate restaurant comments (reviews)
    restaurant_comments = []
    comment_count = 0

    for purchase in purchases:
        if purchase["status"] == "COMPLETED" and random.random() < 0.7:  # 70% of completed purchases have reviews
            review_date = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 3))
            rating = random.randint(1, 5)

            comment = {
                "id": comment_count + 1,
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "purchase_id": purchase["id"],
                "rating": rating,
                "comment": random.choice([
                    "Yemekler çok lezzetliydi, tavsiye ederim.",
                    "Servis biraz yavaştı ama yemekler güzeldi.",
                    "Fiyat performans açısından gayet iyi.",
                    "Porsiyonlar küçüktü ama lezzeti iyiydi.",
                    "Harika bir deneyimdi, kesinlikle tekrar geleceğim.",
                    "Ortalama bir yemek deneyimiydi.",
                    "Çok beğendim, ailemle tekrar geleceğim.",
                    "Beklentilerimi karşılamadı.",
                    "Temizlik konusunda daha dikkatli olabilirler.",
                    "Personel çok ilgiliydi, teşekkürler."
                ]),
                "timestamp": review_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            restaurant_comments.append(comment)
            comment_count += 1

    # Generate comment badges
    comment_badges = []
    badge_id = 1

    for comment in restaurant_comments:
        # Each comment might have 0-3 badges
        num_badges = random.randint(0, 3)
        positive_badges = ["Fresh Food", "Fast Delivery", "Customer Friendly"]
        negative_badges = ["Not Fresh", "Slow Delivery", "Not Customer Friendly"]

        # If rating is high, bias towards positive badges
        available_badges = positive_badges + (negative_badges if comment["rating"] <= 3 else [])

        if num_badges > 0:
            selected_badges = random.sample(available_badges, min(num_badges, len(available_badges)))

            for badge_name in selected_badges:
                badge = {
                    "id": badge_id,
                    "comment_id": comment["id"],
                    "badge_name": badge_name,
                    "is_positive": badge_name in positive_badges
                }
                comment_badges.append(badge)
                badge_id += 1

    # Generate achievements
    achievements = [
        {
            "id": 1,
            "name": "First Purchase",
            "description": "Made your first purchase",
            "badge_image_url": "https://example.com/badges/first_purchase.png",
            "achievement_type": "FIRST_PURCHASE",
            "threshold": None,
            "is_active": True
        },
        {
            "id": 2,
            "name": "Five Purchases",
            "description": "Made five purchases",
            "badge_image_url": "https://example.com/badges/five_purchases.png",
            "achievement_type": "PURCHASE_COUNT",
            "threshold": 5,
            "is_active": True
        },
        {
            "id": 3,
            "name": "Weekly Buyer",
            "description": "Made at least one purchase every week for a month",
            "badge_image_url": "https://example.com/badges/weekly_buyer.png",
            "achievement_type": "WEEKLY_PURCHASE",
            "threshold": 4,
            "is_active": True
        },
        {
            "id": 4,
            "name": "Regular Commenter",
            "description": "Left 10 comments on restaurants",
            "badge_image_url": "https://example.com/badges/regular_commenter.png",
            "achievement_type": "REGULAR_COMMENTER",
            "threshold": 10,
            "is_active": True
        },
        {
            "id": 5,
            "name": "Eco Warrior",
            "description": "Saved 5kg of CO2 through purchases",
            "badge_image_url": "https://example.com/badges/eco_warrior.png",
            "achievement_type": "CO2_SAVED",
            "threshold": 5,
            "is_active": True
        },
        {
            "id": 6,
            "name": "Flash Deal Hunter",
            "description": "Purchased 3 flash deals",
            "badge_image_url": "https://example.com/badges/flash_hunter.png",
            "achievement_type": "FLASH_DEALS",
            "threshold": 3,
            "is_active": True
        },
        {
            "id": 7,
            "name": "Food Explorer",
            "description": "Ordered from 5 different cuisines",
            "badge_image_url": "https://example.com/badges/food_explorer.png",
            "achievement_type": "CUISINE_VARIETY",
            "threshold": 5,
            "is_active": True
        }
    ]

    # Generate user achievements
    user_achievements = []
    achievement_id = 1

    # For each customer, look at their purchases and comments to decide achievements
    for user in [u for u in users if u["role"] == "customer"]:
        user_purchases = [p for p in purchases if p["user_id"] == user["id"]]
        user_comments = [c for c in restaurant_comments if c["user_id"] == user["id"]]

        # First Purchase achievement for everyone who made a purchase
        if len(user_purchases) > 0:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 1,  # First Purchase
                "earned_at": user_purchases[0]["purchase_date"]
            })
            achievement_id += 1

        # Five Purchases achievement
        if len(user_purchases) >= 5:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 2,  # Five Purchases
                "earned_at": user_purchases[4]["purchase_date"]
            })
            achievement_id += 1

        # Regular Commenter
        if len(user_comments) >= 10:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 4,  # Regular Commenter
                "earned_at": user_comments[9]["timestamp"]
            })
            achievement_id += 1

        # Flash Deal Hunter
        flash_deal_purchases = [p for p in user_purchases if p["is_flash_deal"]]
        if len(flash_deal_purchases) >= 3:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 6,  # Flash Deal Hunter
                "earned_at": flash_deal_purchases[2]["purchase_date"]
            })
            achievement_id += 1

    # Generate environmental contributions
    environmental_contributions = []

    for i, purchase in enumerate(purchases):
        if purchase["status"] == "COMPLETED":
            # Calculate CO2 avoided based on purchase quantity and price
            co2_avoided = round(purchase["total_price"] * random.uniform(0.1, 0.3), 2)

            contribution = {
                "id": i + 1,
                "user_id": purchase["user_id"],
                "purchase_id": purchase["id"],
                "co2_avoided": co2_avoided,
                "created_at": purchase["purchase_date"]
            }
            environmental_contributions.append(contribution)

    # Generate user environmental stats (new)
    user_env_stats = []

    for user in [u for u in users if u["role"] == "customer"]:
        user_contributions = [c for c in environmental_contributions if c["user_id"] == user["id"]]

        total_co2_saved = sum(c["co2_avoided"] for c in user_contributions)
        trees_equivalent = round(total_co2_saved / 25, 2)  # arbitrary conversion factor

        user_env_stats.append({
            "id": user["id"],
            "user_id": user["id"],
            "total_co2_saved": total_co2_saved,
            "trees_equivalent": trees_equivalent,
            "waste_reduced_kg": round(total_co2_saved * 0.5, 2),  # another arbitrary factor
            "water_saved_liters": round(total_co2_saved * 10, 2),  # another arbitrary factor
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Generate user favorites
    user_favorites = []
    favorite_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # Each customer might favorite 0-5 restaurants
        num_favorites = random.randint(0, 5)

        if num_favorites > 0:
            # Randomly select restaurants to favorite without duplicates
            favorite_restaurants = random.sample(restaurants, min(num_favorites, len(restaurants)))

            for restaurant in favorite_restaurants:
                user_favorite = {
                    "id": favorite_id,
                    "user_id": user["id"],
                    "restaurant_id": restaurant["id"]
                }
                user_favorites.append(user_favorite)
                favorite_id += 1

    # Generate user devices
    user_devices = []
    device_id = 1

    device_types = ["iOS", "Android", "Web"]
    platforms = ["iPhone", "Samsung Galaxy", "Chrome", "Firefox", "Safari"]

    for user in users:
        # Each user might have 1-3 devices
        num_devices = random.randint(1, 3)

        for _ in range(num_devices):
            device_type = random.choice(device_types)
            platform = random.choice(platforms)

            user_device = {
                "id": device_id,
                "user_id": user["id"],
                "push_token": str(uuid.uuid4()),
                "web_push_token": str(uuid.uuid4()) if device_type == "Web" else None,
                "device_type": device_type,
                "platform": platform,
                "created_at": (datetime.now(UTC) - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d %H:%M:%S"),
                "last_used": (datetime.now(UTC) - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True
            }
            user_devices.append(user_device)
            device_id += 1

    # Generate restaurant punishments with the new fields
    restaurant_punishments = []
    punishment_id = 1
    punishment_types = ["PERMANENT", "TEMPORARY", "TEMPORARY"]  # weighted towards TEMPORARY
    support_user_ids = [user["id"] for user in users if user["role"] == "support"]

    for restaurant in restaurants:
        # 10% chance of a restaurant having a punishment
        if random.random() < 0.1:
            punishment_type = random.choice(punishment_types)
            punishment_start = datetime.now(UTC) - timedelta(days=random.randint(1, 10))
            support_user_id = random.choice(support_user_ids)

            # For temporary punishments, set end date
            if punishment_type == "TEMPORARY":
                duration_days = random.choice([3, 7, 14, 30])
                punishment_end = punishment_start + timedelta(days=duration_days)
            else:
                duration_days = None
                punishment_end = None

            # 20% chance the punishment is reverted
            is_reverted = random.random() < 0.2
            is_active = not is_reverted

            reverted_at = None
            reverted_by = None
            reversion_reason = None

            if is_reverted:
                reverted_at = punishment_start + timedelta(days=random.randint(1, 3))
                reverted_by = random.choice(support_user_ids)
                reversion_reason = random.choice([
                    "Punishment was issued by mistake",
                    "Issue resolved with restaurant",
                    "Restaurant appealed successfully",
                    "Investigation completed, punishment no longer needed"
                ])

            punishment = {
                "id": punishment_id,
                "restaurant_id": restaurant["id"],
                "reason": random.choice([
                    "Multiple reported issues with food quality",
                    "Late deliveries",
                    "Poor customer service",
                    "Hygiene concerns",
                    "Multiple cancellations"
                ]),
                "punishment_type": punishment_type,
                "duration_days": duration_days,
                "start_date": punishment_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": punishment_end.strftime("%Y-%m-%d %H:%M:%S") if punishment_end else None,
                "created_by": support_user_id,
                "created_at": punishment_start.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": is_active,
                "is_reverted": is_reverted,
                "reverted_by": reverted_by,
                "reverted_at": reverted_at.strftime("%Y-%m-%d %H:%M:%S") if reverted_at else None,
                "reversion_reason": reversion_reason
            }
            restaurant_punishments.append(punishment)
            punishment_id += 1

    # Generate purchase reports with status
    purchase_reports = []
    report_id = 1

    # For each 10th completed purchase, generate a report
    for purchase in [p for p in purchases if p["status"] == "COMPLETED"]:
        if random.random() < 0.1:  # 10% chance of having a report
            report_status = random.choice(["active", "resolved", "inactive"])
            reported_at = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 3))

            resolved_at = None
            resolved_by = None
            punishment_id = None

            if report_status != "active":
                resolved_at = reported_at + timedelta(days=random.randint(1, 5))
                resolved_by = random.choice(support_user_ids)

                # If resolved and 30% chance, link it to a punishment
                if report_status == "resolved" and random.random() < 0.3:
                    # Find punishments for this restaurant
                    restaurant_id = purchase["restaurant_id"]
                    restaurant_punishments_list = [p for p in restaurant_punishments if
                                                   p["restaurant_id"] == restaurant_id]
                    if restaurant_punishments_list:
                        punishment_id = random.choice(restaurant_punishments_list)["id"]

            report = {
                "id": report_id,
                "user_id": purchase["user_id"],
                "purchase_id": purchase["id"],
                "restaurant_id": purchase["restaurant_id"],
                "listing_id": purchase["listing_id"],
                "image_url": f"https://example.com/images/reports/{report_id}.jpg",
                "description": random.choice([
                    "The food was cold when it arrived",
                    "The order was incomplete",
                    "The quality was not as described",
                    "Very long delivery time",
                    "Wrong items in the order",
                    "Food seemed spoiled",
                    "Portion size was much smaller than expected"
                ]),
                "status": report_status,
                "reported_at": reported_at.strftime("%Y-%m-%d %H:%M:%S"),
                "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else None,
                "resolved_by": resolved_by,
                "punishment_id": punishment_id
            }
            purchase_reports.append(report)
            report_id += 1

    # Generate refund records
    refund_records = []
    refund_id = 1

    for purchase in purchases:
        # 5% chance of a purchase having a refund if it's COMPLETED or REJECTED
        if purchase["status"] in ["COMPLETED", "REJECTED"] and random.random() < 0.05:
            refund_date = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 3))

            refund = {
                "id": refund_id,
                "restaurant_id": purchase["restaurant_id"],
                "user_id": purchase["user_id"],
                "order_id": purchase["id"],
                "amount": purchase["total_price"],
                "reason": random.choice([
                    "Food quality issues",
                    "Late delivery",
                    "Wrong order",
                    "Customer complaint",
                    "Restaurant request"
                ]),
                "processed": True,
                "created_by": random.choice(support_user_ids),
                "created_at": refund_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            refund_records.append(refund)
            refund_id += 1

    # Generate user cart items
    user_cart_items = []
    cart_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # 40% chance of a user having items in cart
        if random.random() < 0.4:
            # 1-3 items in cart
            num_items = random.randint(1, 3)

            # Randomly select listings to add to cart
            for _ in range(num_items):
                listing = random.choice(listings)
                restaurant = next(r for r in restaurants if r["id"] == listing["restaurant_id"])

                cart_item = {
                    "id": cart_id,
                    "user_id": user["id"],
                    "listing_id": listing["id"],
                    "restaurant_id": restaurant["id"],
                    "count": random.randint(1, 3),
                    "added_at": (datetime.now(UTC) - timedelta(hours=random.randint(1, 72))).strftime(
                        "%Y-%m-%d %H:%M:%S")
                }
                user_cart_items.append(cart_item)
                cart_id += 1

    # Generate discount earned
    discounts_earned = []
    discount_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # 30% chance of a user having earned discounts
        if random.random() < 0.3:
            # 1-3 discounts earned
            num_discounts = random.randint(1, 3)

            for _ in range(num_discounts):
                discount_amount = round(random.uniform(5.0, 20.0), 2)
                earned_date = (datetime.now(UTC) - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")

                discount = {
                    "id": discount_id,
                    "user_id": user["id"],
                    "discount": discount_amount,
                    "earned_at": earned_date
                }
                discounts_earned.append(discount)
                discount_id += 1

    # Generate notification settings (new)
    notification_settings = []

    for user in users:
        settings = {
            "id": user["id"],
            "user_id": user["id"],
            "push_enabled": random.choice([True, False]),
            "email_enabled": random.choice([True, False]),
            "sms_enabled": random.choice([True, False]),
            "flash_deals_notifications": random.choice([True, False]),
            "order_status_notifications": True,  # Most users want order updates
            "marketing_notifications": random.choice([True, False]),
            "achievement_notifications": random.choice([True, False])
        }
        notification_settings.append(settings)

    # Generate user notifications (new)
    user_notifications = []
    notification_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # Generate 5-15 random notifications for each user
        num_notifications = random.randint(5, 15)

        for _ in range(num_notifications):
            # Generate a notification date within the last 30 days
            notification_date = datetime.now(UTC) - timedelta(days=random.randint(0, 30),
                                                              hours=random.randint(0, 23),
                                                              minutes=random.randint(0, 59))

            # Types of notifications
            notification_types = [
                "ORDER_STATUS", "FLASH_DEAL", "ACHIEVEMENT", "MARKETING", "REFUND", "SYSTEM"
            ]

            notification_type = random.choice(notification_types)

            # Generate notification content based on type
            if notification_type == "ORDER_STATUS":
                title = "Sipariş Durumu Güncellendi"
                message = f"Siparişiniz {random.choice(['hazırlanıyor', 'yola çıktı', 'teslim edildi'])}"
            elif notification_type == "FLASH_DEAL":
                title = "Yeni Flash İndirim!"
                message = f"Son {random.randint(1, 6)} saate özel %{random.randint(30, 70)} indirim fırsatı kaçırmayın!"
            elif notification_type == "ACHIEVEMENT":
                title = "Yeni Başarı Kazandınız!"
                message = f"Tebrikler! '{random.choice([a['name'] for a in achievements])}' başarısını kazandınız."
            elif notification_type == "MARKETING":
                title = "Özel Teklif"
                message = f"Bu hafta sonu siparişlerinizde %{random.randint(10, 25)} indirim sizleri bekliyor."
            elif notification_type == "REFUND":
                title = "İade İşlemi Tamamlandı"
                message = "Talebiniz üzerine iade işleminiz tamamlandı. Tutar hesabınıza aktarıldı."
            else:  # SYSTEM
                title = "Sistem Bildirimi"
                message = "Uygulamamızı güncelledik! Yeni özellikleri keşfedin."

            notification = {
                "id": notification_id,
                "user_id": user["id"],
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "read": random.random() < 0.7,  # 70% chance notification is read
                "sent_at": notification_date.strftime("%Y-%m-%d %H:%M:%S"),
                "read_at": (notification_date + timedelta(minutes=random.randint(1, 60))).strftime(
                    "%Y-%m-%d %H:%M:%S") if random.random() < 0.7 else None,
                "action_link": f"/orders/{random.randint(1, 100)}" if notification_type == "ORDER_STATUS" else None
            }
            user_notifications.append(notification)
            notification_id += 1

    # Generate payment methods (new)
    payment_methods = []
    payment_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # Each customer has 1-3 payment methods
        num_methods = random.randint(1, 3)

        for i in range(num_methods):
            payment_type = random.choice(["CREDIT_CARD", "DEBIT_CARD", "ONLINE_BANKING"])

            if payment_type in ["CREDIT_CARD", "DEBIT_CARD"]:
                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "card_name": random.choice(["Bonus", "World", "Axess", "Maximum", "Cardfinans"]),
                    "last_four": f"{random.randint(1000, 9999)}",
                    "expiry_month": random.randint(1, 12),
                    "expiry_year": random.randint(2025, 2030),
                    "is_default": i == 0,  # First payment method is default
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S")
                }
            else:  # ONLINE_BANKING
                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "bank_name": random.choice(["Garanti", "İş Bankası", "Akbank", "Yapı Kredi", "Ziraat"]),
                    "account_name": user["name"],
                    "last_four": None,
                    "expiry_month": None,
                    "expiry_year": None,
                    "is_default": i == 0,  # First payment method is default
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S")
                }

            payment_methods.append(method)
            payment_id += 1

    # Generate payments (new)
    payments = []
    payment_record_id = 1

    for purchase in purchases:
        # Get a payment method for this user
        user_payment_methods = [p for p in payment_methods if p["user_id"] == purchase["user_id"]]

        if user_payment_methods:
            payment_method = random.choice(user_payment_methods)

            payment = {
                "id": payment_record_id,
                "purchase_id": purchase["id"],
                "user_id": purchase["user_id"],
                "payment_method_id": payment_method["id"],
                "amount": purchase["total_price"],
                "status": "COMPLETED" if purchase["status"] != "REJECTED" else random.choice(["FAILED", "REFUNDED"]),
                "transaction_id": str(uuid.uuid4()),
                "payment_date": purchase["purchase_date"],
                "payment_provider": random.choice(["iyzico", "PayTR", "BeinConnect", "Internal"]),
                "payment_details": json.dumps({
                    "card_type": payment_method.get("card_name"),
                    "installments": random.choice([0, 0, 0, 3, 6]) if payment_method.get(
                        "payment_type") == "CREDIT_CARD" else 0
                })
            }
            payments.append(payment)
            payment_record_id += 1

    # Save data to JSON files
    def save_to_json(data, filename):
        with open(f"../exported_json/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Save files with names matching the database table names from the image
    save_to_json(users, 'users.json')
    save_to_json(addresses, 'customeraddresses.json')
    save_to_json(restaurants, 'restaurants.json')
    save_to_json(restaurant_badge_points, 'restaurant_badge_points.json')
    save_to_json(categories, 'categories.json')  # New
    save_to_json(restaurant_categories, 'restaurant_categories.json')  # New
    save_to_json(menu_categories, 'menu_categories.json')  # New
    save_to_json(listings, 'listings.json')
    save_to_json(flash_deals, 'flash_deals.json')  # New
    save_to_json(purchases, 'purchases.json')
    save_to_json(purchase_status_history, 'purchase_status_history.json')  # New
    save_to_json(restaurant_comments, 'restaurant_comments.json')
    save_to_json(comment_badges, 'comment_badges.json')
    save_to_json(achievements, 'achievements.json')
    save_to_json(user_achievements, 'user_achievements.json')
    save_to_json(environmental_contributions, 'environmental_contributions.json')
    save_to_json(user_env_stats, 'user_environmental_stats.json')  # New
    save_to_json(user_favorites, 'user_favorites.json')
    save_to_json(user_devices, 'user_devices.json')
    save_to_json(restaurant_punishments, 'restaurant_punishments.json')
    save_to_json(refund_records, 'refund_records.json')
    save_to_json(user_cart_items, 'user_cart.json')
    save_to_json(discounts_earned, 'discountearned.json')
    save_to_json(notification_settings, 'notification_settings.json')  # New
    save_to_json(user_notifications, 'user_notifications.json')  # New
    save_to_json(payment_methods, 'payment_methods.json')  # New
    save_to_json(payments, 'payments.json')  # New
    save_to_json(purchase_reports, 'purchase_reports.json')  # New

    print("Sample data has been generated and saved to JSON files in ../exported_json/ directory:")
    print(
        f"- {len(users)} users ({len([u for u in users if u['role'] == 'owner'])} owners, {len([u for u in users if u['role'] == 'customer'])} customers, {len([u for u in users if u['role'] == 'support'])} support team members)")
    print(f"- {len(addresses)} customer addresses")
    print(f"- {len(restaurants)} restaurants")
    print(f"- {len(restaurant_badge_points)} restaurant badge points records")
    print(f"- {len(categories)} food categories")
    print(f"- {len(restaurant_categories)} restaurant category mappings")
    print(f"- {len(menu_categories)} menu categories")
    print(f"- {len(listings)} listings")
    print(f"- {len(flash_deals)} flash deals")
    print(f"- {len(purchases)} purchases")
    print(f"- {len(purchase_status_history)} purchase status history records")
    print(f"- {len(restaurant_comments)} restaurant comments")
    print(f"- {len(comment_badges)} comment badges")
    print(f"- {len(achievements)} achievements")
    print(f"- {len(user_achievements)} user achievements")
    print(f"- {len(environmental_contributions)} environmental contributions")
    print(f"- {len(user_env_stats)} user environmental stats")
    print(f"- {len(user_favorites)} user favorites")
    print(f"- {len(user_devices)} user devices")
    print(f"- {len(restaurant_punishments)} restaurant punishments")
    print(f"- {len(refund_records)} refund records")
    print(f"- {len(purchase_reports)} purchase reports")
    print(f"- {len(user_cart_items)} user cart items")
    print(f"- {len(discounts_earned)} discounts earned")
    print(f"- {len(notification_settings)} notification settings")
    print(f"- {len(user_notifications)} user notifications")
    print(f"- {len(payment_methods)} payment methods")
    print(f"- {len(payments)} payment records")
    print("\nAll locations are in either İzmir Karşıyaka or İzmir Bornova as requested.")
    print("All passwords are set to the scrypt hash format as requested.")
    print("Environmental contributions have been set based on purchases.")


if __name__ == "__main__":
    generate_sample_data()