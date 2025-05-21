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

    # Create 15 restaurant owners (increased from 10)
    for i in range(15):
        owner = {
            "id": i + 1,
            "name": f"{random.choice(['Ali', 'Ahmet', 'Mehmet', 'Mustafa', 'Hüseyin', 'Ibrahim', 'Murat', 'Kemal', 'Osman', 'Serkan', 'Emre', 'Burak', 'Erdem', 'Volkan', 'Cem'])} {random.choice(['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Öztürk', 'Aydın', 'Yıldız', 'Koç', 'Özdemir', 'Utkan', 'Yalçın', 'Arslan', 'Aktaş', 'Doğan'])}",
            "email": f"owner{i + 1}@example.com",
            "phone_number": "+905078905011" if i == 0 else f"+9053{random.randint(10000000, 99999999)}",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "owner",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
        users.append(owner)

    # Create 30 customers (increased from 20)
    for i in range(30):
        customer = {
            "id": i + 16,  # Adjusted for 15 owners
            "name": f"{random.choice(['Ali', 'Ayşe', 'Mehmet', 'Fatma', 'Mustafa', 'Zeynep', 'Ahmet', 'Emine', 'Hüseyin', 'Elif', 'Deniz', 'Selin', 'Kerem', 'Zehra', 'Yusuf'])} {random.choice(['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Öztürk', 'Aydın', 'Yıldız', 'Koç', 'Özdemir', 'Kılıç', 'Aksoy', 'Taş', 'Aslan', 'Çetin'])}",
            "email": f"customer{i + 1}@example.com",
            "phone_number": "+905078905010" if i == 0 else f"+9053{random.randint(10000000, 99999999)}",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
        users.append(customer)

    # Create 5 support team members (increased from 3)
    for i in range(5):
        support = {
            "id": i + 46,  # Adjusted for 15 owners + 30 customers
            "name": f"{random.choice(['Support', 'Admin', 'Helper', 'Moderator', 'Assistant'])} {i + 1}",
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
            # Expanded districts and neighborhoods
            district = random.choice(["Karşıyaka", "Bornova", "Konak", "Bayraklı", "Çiğli"])

            if district == "Karşıyaka":
                neighborhood = random.choice([
                    "Bostanlı", "Atakent", "Mavişehir", "Alaybey", "Tersane",
                    "Donanmacı", "Tuna", "Bahariye", "Yalı", "Goncalar"
                ])
            elif district == "Bornova":
                neighborhood = random.choice([
                    "Atatürk", "Evka 3", "Evka 4", "Kazımdirik", "Özkanlar",
                    "Ergene", "Mevlana", "Barbaros", "Kızılay", "Yeşilova"
                ])
            elif district == "Konak":
                neighborhood = random.choice([
                    "Alsancak", "Göztepe", "Güzelyalı", "Hatay", "Konak Merkez",
                    "Çankaya", "Kemeraltı", "Kahramanlar", "Basmane", "Gündoğdu"
                ])
            elif district == "Bayraklı":
                neighborhood = random.choice([
                    "Adalet", "Mansuroğlu", "Bayraklı Merkez", "Osmangazi", "Manavkuyu",
                    "Postacılar", "Fuat Edip Baksı", "Doğançay", "Cengizhan", "Yamanlar"
                ])
            else:  # Çiğli
                neighborhood = random.choice([
                    "Ataşehir", "Balatçık", "Çiğli Merkez", "Küçük Çiğli", "Harmandalı",
                    "Maltepe", "Güzeltepe", "Sasalı", "Evka 5", "Buruncuk"
                ])

            address = {
                "id": len(addresses) + 1,
                "user_id": customer_id,
                "title": random.choice(
                    ["Ev", "İş", "Yazlık", "Kış Evi", "Arkadaş Evi", "Okul", "Ofis", "Anne Evi", "Tatil Evi",
                     "Yeni Ev"]),
                "longitude": float(27.1 + random.random() * 0.2),
                "latitude": float(38.4 + random.random() * 0.2),
                "street": f"{random.randint(1, 100)}. {random.choice(['Sokak', 'Cadde', 'Bulvar'])}",
                "neighborhood": neighborhood,
                "district": district,
                "province": "İzmir",
                "country": "Türkiye",
                "postalCode": f"35{random.randint(100, 999)}",
                "apartmentNo": random.randint(1, 30),
                "floor": random.randint(1, 15),  # New field
                "doorNo": str(random.randint(1, 50)),
                "building_name": random.choice(
                    [None, "Leylak Apt", "Güneş Apt", "Deniz Apt", "Yıldız Apt", "Kardelen Apt"]),  # New field
                "is_primary": j == 0,  # First address is primary
                "delivery_instructions": random.choice(
                    [None, "Kapıya bırakın", "Arayın", "Zili çalmayın", "Köpek var dikkat"])  # New field
            }
            addresses.append(address)

    # Generate food categories with more options
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
        {"id": 10, "name": "Vegan", "icon": "🥗", "display_order": 10},
        {"id": 11, "name": "Indian", "icon": "🍛", "display_order": 11},  # New
        {"id": 12, "name": "Japanese", "icon": "🍱", "display_order": 12},  # New
        {"id": 13, "name": "Mexican", "icon": "🌮", "display_order": 13},  # New
        {"id": 14, "name": "Greek", "icon": "🥙", "display_order": 14},  # New
        {"id": 15, "name": "Thai", "icon": "🥘", "display_order": 15}  # New
    ]

    # Generate restaurants with more variety
    restaurants = []
    owner_ids = [user["id"] for user in users if user["role"] == "owner"]

    for i, owner_id in enumerate(owner_ids):
        district = random.choice(["Karşıyaka", "Bornova", "Konak", "Bayraklı", "Çiğli"])

        # Select appropriate neighborhood for district
        if district == "Karşıyaka":
            neighborhood = random.choice([
                "Bostanlı", "Atakent", "Mavişehir", "Alaybey", "Tersane", "Donanmacı"
            ])
        elif district == "Bornova":
            neighborhood = random.choice([
                "Atatürk", "Evka 3", "Evka 4", "Kazımdirik", "Özkanlar", "Ergene"
            ])
        elif district == "Konak":
            neighborhood = random.choice([
                "Alsancak", "Göztepe", "Güzelyalı", "Hatay", "Konak Merkez"
            ])
        elif district == "Bayraklı":
            neighborhood = random.choice([
                "Adalet", "Mansuroğlu", "Bayraklı Merkez", "Osmangazi", "Manavkuyu"
            ])
        else:  # Çiğli
            neighborhood = random.choice([
                "Ataşehir", "Balatçık", "Çiğli Merkez", "Küçük Çiğli", "Harmandalı"
            ])

        # More diverse restaurant names
        first_names = ["Lezzet", "Tadım", "Keyif", "Sofra", "Afiyet", "Çiçek", "Yöresel", "Özgür", "Kral", "Usta",
                       "Meşhur", "Ege", "Deniz", "Güzel", "Özel"]
        last_names = ["Restaurant", "Cafe", "Köşesi", "Yeri", "Lokantası", "Mutfağı", "Sofrası", "Gurme", "Bahçesi",
                      "Ocakbaşı", "Evi", "Dürüm", "Pide", "Döner", "Mangal"]
        restaurant_name = f"{random.choice(first_names)} {random.choice(last_names)}"

        # Select from expanded categories
        category = random.choice([
            "Turkish", "Italian", "Fast Food", "Chinese", "Seafood", "Kebab", "Bakery",
            "Dessert", "Breakfast", "Vegan", "Indian", "Japanese", "Mexican", "Greek", "Thai"
        ])

        restaurant = {
            "id": i + 1,
            "owner_id": owner_id,
            "restaurantName": restaurant_name,
            "restaurantDescription": f"{restaurant_name} - {random.choice(['En taze ve lezzetli yemekleri sunan', 'Kaliteli malzemelerle hazırlanan', 'Geleneksel tarifleri modern sunan', 'Yöresel lezzetleri keşfedeceğiniz', 'Sağlıklı ve lezzetli seçenekler sunan'])} işletme",
            "restaurantEmail": f"info@{restaurant_name.lower().replace(' ', '')}.com",
            "restaurantPhone": f"+9053{random.randint(10000000, 99999999)}",
            "longitude": float(27.1 + random.random() * 0.2),
            "latitude": float(38.4 + random.random() * 0.2),
            "full_address": f"{random.choice(['Atatürk', 'Cumhuriyet', 'İnönü', 'Gazi'])} {random.choice(['Caddesi', 'Bulvarı', 'Meydanı'])} No:{random.randint(1, 200)}, {neighborhood}, {district}, İzmir",
            # New field
            "category": category,
            "workingDays": f"{random.choice(['Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday', 'Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday'])}",
            "workingHoursStart": f"{random.randint(7, 12)}:{random.choice(['00', '30'])}",
            "workingHoursEnd": f"{random.randint(19, 23)}:{random.choice(['00', '30'])}",
            "listings": 0,
            "rating": float(round(3.5 + random.random() * 1.5, 2)),
            "ratingCount": random.randint(0, 200),  # Increased max count
            "image_url": f"https://example.com/images/restaurants/{i + 1}.jpg",
            "cover_image_url": f"https://example.com/images/restaurant_covers/{i + 1}.jpg",  # New field
            "logo_url": f"https://example.com/images/restaurant_logos/{i + 1}.png",  # New field
            "pickup": True,
            "delivery": random.choice([True, False]),
            "maxDeliveryDistance": random.uniform(1.0, 7.0) if random.choice([True, False]) else None,
            # Increased max distance
            "deliveryFee": float(round(random.uniform(5.0, 25.0), 2)) if random.choice([True, False]) else None,
            # Increased max fee
            "minOrderAmount": float(round(random.uniform(20.0, 70.0), 2)) if random.choice([True, False]) else None,
            # Increased max amount
            "averagePreparationTime": random.randint(10, 45),  # New field - in minutes
            "flash_deals_available": random.choice([True, False]),
            "flash_deals_count": random.randint(0, 7),  # Increased max count
            "has_sustainable_packaging": random.choice([True, False]),  # New field
            "offers_contactless_delivery": random.choice([True, False]),  # New field
            "established_year": random.randint(1990, 2024),  # New field
            "cuisine_specialties": random.sample(
                ["Local", "Fusion", "Gourmet", "Homemade", "Organic", "Diet", "Spicy", "Traditional"],
                random.randint(1, 3))  # New field
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
            "notCustomerFriendlyPoint": random.randint(0, 20),
            "sustainabilityPoint": random.randint(0, 100),  # New field
            "foodQualityPoint": random.randint(0, 100),  # New field
            "valueForMoneyPoint": random.randint(0, 100)  # New field
        }
        restaurant_badge_points.append(badge_points)

    # Generate restaurant categories (mapping)
    restaurant_categories = []
    category_id = 1

    for restaurant in restaurants:
        # Each restaurant gets its main category plus 0-3 additional categories (increased from 0-2)
        main_category_name = restaurant["category"]
        main_category_id = next(cat["id"] for cat in categories if cat["name"] == main_category_name)

        restaurant_categories.append({
            "id": category_id,
            "restaurant_id": restaurant["id"],
            "category_id": main_category_id,
            "is_primary": True
        })
        category_id += 1

        # Add 0-3 additional categories (increased from 0-2)
        num_additional = random.randint(0, 3)
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

    # Generate menu categories with more options
    menu_categories = []
    menu_cat_id = 1

    # Expanded menu category names
    menu_category_names = [
        "Başlangıçlar", "Ana Yemekler", "Tatlılar", "İçecekler", "Burgerler",
        "Pizzalar", "Salatalar", "Çorbalar", "Kahvaltı", "Ara Sıcaklar",
        "Makarnalar", "Tavuk Menüler", "Vejeteryan", "Mezeler", "Özel Menüler",
        "Dönerler", "Kebaplar", "Balıklar", "Pideler", "Sandviçler",
        "Sıcak İçecekler", "Soğuk İçecekler", "Atıştırmalıklar", "Çocuk Menüler", "Vegan Seçenekler",
        "Glutensiz", "Etler", "Fırından", "Fast Food", "Dünya Mutfağı"
    ]

    for restaurant in restaurants:
        # Each restaurant has 4-7 menu categories (increased from 3-5)
        num_categories = random.randint(4, 7)
        categories_added = []

        for j in range(num_categories):
            category_name = random.choice(menu_category_names)

            # Avoid duplicate category names for the same restaurant
            while category_name in categories_added:
                category_name = random.choice(menu_category_names)

            categories_added.append(category_name)

            menu_categories.append({
                "id": menu_cat_id,
                "restaurant_id": restaurant["id"],
                "name": category_name,
                "description": f"{restaurant['restaurantName']} restoranın {category_name} kategorisi",
                "display_order": j + 1,
                "image_url": f"https://example.com/images/menu_categories/{restaurant['id']}_{j + 1}.jpg",  # New field
                "is_available": random.choice([True, True, True, False]),  # New field - mostly available
                "item_count": random.randint(3, 12)  # New field
            })
            menu_cat_id += 1

    # Generate listings with more variety
    listings = []

    # More variety in food names
    food_adjectives = ["Taze", "Günlük", "Özel", "Lezzetli", "Ev Yapımı", "Organik", "Sınırlı", "Seçkin", "Geleneksel",
                       "Premium"]
    food_items = ["Menü", "Tabak", "Porsiyon", "Paket", "Set", "Dürüm", "Sandviç", "Pizza", "Burger", "Salata",
                  "Çorba", "Makarna", "Kebap", "Tatlı", "Kahvaltı", "Pide", "Lahmacun", "Balık", "Köfte", "Pilav"]

    for restaurant in restaurants:
        # Get menu categories for this restaurant
        rest_menu_categories = [c for c in menu_categories if c["restaurant_id"] == restaurant["id"]]

        num_listings = random.randint(7, 15)  # Increased from 5-10
        restaurant["listings"] = num_listings

        for j in range(num_listings):
            consume_within = random.randint(6, 72)  # Extended from 48 to 72 hours
            expires_at = datetime.now(UTC) + timedelta(hours=consume_within)

            original_price = round(random.uniform(30.0, 200.0), 2)  # Increased max price
            discount_percentage = random.randint(20, 40)  # Explicit discount percentage
            pickup_price = round(original_price * (1 - (discount_percentage / 100)), 2) if restaurant[
                "pickup"] else None
            delivery_price = round(original_price * (1 - (discount_percentage / 100) + 0.05), 2) if restaurant[
                "delivery"] else None  # 5% more than pickup

            # Assign to a random menu category for this restaurant
            menu_category = random.choice(rest_menu_categories) if rest_menu_categories else None

            # Generate more descriptive listing details
            food_adjective = random.choice(food_adjectives)
            food_item = random.choice(food_items)

            # More detailed descriptions
            descriptions = [
                "Günün sonunda kalan taze yiyecekleri değerlendirmek için indirimli fiyatla sunuyoruz.",
                f"Bu {food_adjective.lower()} {food_item.lower()} için özel indirim fırsatı. Aynı gün içinde tüketilmelidir.",
                f"Taze hazırlanmış ve sınırlı sayıda kalan bu {food_item.lower()} indirimli fiyatla sizin olabilir.",
                "Fazla stokları azaltmak için sınırlı sayıda indirimli yemek sunuyoruz. Kaçırmayın!",
                f"Bugüne özel hazırlanan {food_item.lower()}leri için özel bir fırsat. Çevre dostu bir seçim yapın.",
                f"Bugüne özel hazırlanan {food_adjective.lower()} {food_item.lower()}, belirtilen süre içinde tüketilmelidir."
            ]

            listing = {
                "id": len(listings) + 1,
                "restaurant_id": restaurant["id"],
                "menu_category_id": menu_category["id"] if menu_category else None,
                "title": f"{food_adjective} {food_item}",
                "description": random.choice(descriptions),
                "image_url": f"https://example.com/images/listings/{len(listings) + 1}.jpg",
                "count": random.randint(1, 15),  # Increased max count
                "original_price": original_price,
                "discount_percentage": discount_percentage,  # New field
                "pick_up_price": pickup_price,
                "delivery_price": delivery_price,
                "consume_within": consume_within,
                "consume_within_type": "HOURS",
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 10))).strftime(
                    "%Y-%m-%d %H:%M:%S"),  # More variation
                "update_count": random.randint(0, 3),  # More variation
                "fresh_score": round(random.uniform(80.0, 100.0), 1),  # More variation
                "estimated_saving": round(original_price - pickup_price, 2) if pickup_price else None,  # New field
                "ingredients": random.sample(
                    ["Un", "Süt", "Yumurta", "Domates", "Salatalık", "Peynir", "Et", "Tavuk", "Pirinç", "Bulgur",
                     "Maydonoz", "Nane", "Soğan", "Sarımsak", "Biber"], random.randint(3, 8)),  # New field
                "allergens": random.sample(["Gluten", "Süt", "Yumurta", "Kuruyemiş", "Soya", "Balık"],
                                           random.randint(0, 3)),  # New field
                "calories": random.randint(200, 1200),  # New field
                "preparation_time": random.randint(5, 30),  # New field (minutes)
                "serving_size": random.choice(["1 Kişilik", "2 Kişilik", "Aile Boyu", "Tek Porsiyon"]),  # New field
                "available_for_pickup": restaurant["pickup"],
                "available_for_delivery": restaurant["delivery"],
                "is_vegetarian": random.choice([True, False]),  # New field
                "is_vegan": random.choice([True, False]),  # New field
                "is_spicy": random.choice([True, False, False, False])  # New field - 25% chance of being spicy
            }
            listings.append(listing)

    # Generate flash deals with more variety
    flash_deals = []
    flash_deal_id = 1

    for restaurant in restaurants:
        if restaurant["flash_deals_available"]:
            # Generate 1-5 flash deals for eligible restaurants (increased from 1-3)
            num_deals = random.randint(1, 5)
            restaurant_listings = [l for l in listings if l["restaurant_id"] == restaurant["id"]]

            if restaurant_listings:
                # Choose random listings for this restaurant to make flash deals
                deal_listings = random.sample(restaurant_listings, min(num_deals, len(restaurant_listings)))

                for listing in deal_listings:
                    # Flash deals have even deeper discounts
                    flash_discount = random.randint(30, 60)  # 30-60% discount (increased from 30-50%)
                    flash_price = round(listing["original_price"] * (100 - flash_discount) / 100, 2)

                    # Flash deals expire more quickly but with more variety
                    start_time = datetime.now(UTC) + timedelta(hours=random.randint(1, 24))
                    end_time = start_time + timedelta(hours=random.randint(1, 8))  # Extended from 1-6 to 1-8

                    flash_deal = {
                        "id": flash_deal_id,
                        "restaurant_id": restaurant["id"],
                        "listing_id": listing["id"],
                        "flash_price": flash_price,
                        "discount_percentage": flash_discount,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_active": True,
                        "quantity_available": random.randint(1, 8),  # Increased from 1-5
                        "quantity_sold": 0,
                        "flash_title": f"FLASH! {listing['title']}",  # New field
                        "flash_description": f"Sadece {random.randint(1, 8)} saat için geçerli süper fırsat!",
                        # New field
                        "flash_badge": random.choice(["HOT", "SUPER", "FLASH", "LIMITED", "QUICK"]),  # New field
                        "notification_sent": random.choice([True, False])  # New field
                    }
                    flash_deals.append(flash_deal)
                    flash_deal_id += 1

    # Generate purchases with more variety
    purchases = []
    purchase_statuses = ["PENDING", "ACCEPTED", "PREPARING", "READY", "COMPLETED", "REJECTED", "CANCELLED"]
    status_weights = [0.05, 0.1, 0.05, 0.05, 0.65, 0.05, 0.05]  # More statuses with adjusted weights

    for i in range(150):  # Increased from 100
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
        quantity = random.randint(1, 4)  # Increased from 1-3
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

        # Generate purchase date (within the last 60 days - increased from 30)
        purchase_date = datetime.now(UTC) - timedelta(days=random.randint(0, 60))

        # Select status weighted by probability
        status = random.choices(purchase_statuses, status_weights)[0]

        # Only completed orders have a completion image
        completion_image_url = f"https://example.com/images/completions/{i + 1}.jpg" if status == "COMPLETED" else None

        # More varied delivery notes
        delivery_notes_options = [
            None,
            "Lütfen kapıya bırakınız.",
            "Zili çalmayın, bebek uyuyor.",
            "Apartman girişinde bekleyeceğim.",
            "Lütfen arayın, aşağıya ineceğim.",
            "Site güvenliğine bırakabilirsiniz.",
            "Arka kapıdan teslim ediniz.",
            "Köpek var, dikkatli olun."
        ]

        purchase = {
            "id": i + 1,
            "user_id": customer["id"],
            "listing_id": listing["id"],
            "restaurant_id": restaurant["id"],
            "quantity": quantity,
            "total_price": float(round(total_price, 2)),
            "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_delivery_time": (
                        datetime.strptime(purchase_date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") +
                        timedelta(minutes=random.randint(15, 60))).strftime(
                "%Y-%m-%d %H:%M:%S") if is_delivery else None,  # New field
            "status": status,
            "is_delivery": is_delivery,
            "is_flash_deal": is_flash_deal,
            "address_title": customer_address["title"],
            "delivery_address": f"{customer_address['street']}, {customer_address['neighborhood']}, {customer_address['district']}",
            "delivery_district": customer_address["district"],
            "delivery_province": customer_address["province"],
            "delivery_country": customer_address["country"],
            "delivery_notes": random.choice(delivery_notes_options) if is_delivery else None,
            "completion_image_url": completion_image_url,
            "rating_submitted": status == "COMPLETED" and random.random() < 0.7,  # New field
            "delivery_person": random.choice(
                ["Ali Y.", "Mehmet K.", "Ayşe D.", None]) if is_delivery and status not in ["PENDING", "REJECTED",
                                                                                            "CANCELLED"] else None,
            # New field
            "cancellation_reason": random.choice(
                ["Müşteri isteği", "Restoran kapandı", "Yanlış sipariş"]) if status == "CANCELLED" else None,
            # New field
            "saved_co2": round(random.uniform(0.2, 2.0), 2)  # New field - kg of CO2 saved
        }
        purchases.append(purchase)

    # Generate purchase status history with more detail
    purchase_status_history = []
    status_history_id = 1

    for purchase in purchases:
        # All purchases start as PENDING
        purchase_status_history.append({
            "id": status_history_id,
            "purchase_id": purchase["id"],
            "status": "PENDING",
            "timestamp": purchase["purchase_date"],
            "notes": "Sipariş oluşturuldu.",
            "user_id": purchase["user_id"],  # New field
            "restaurant_id": purchase["restaurant_id"],  # New field
            "created_by": "SYSTEM"  # New field
        })
        status_history_id += 1

        purchase_time = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S")

        # If not still pending, add additional statuses based on the final status
        if purchase["status"] == "ACCEPTED" or purchase["status"] in ["PREPARING", "READY", "COMPLETED"]:
            accepted_time = purchase_time + timedelta(minutes=random.randint(5, 15))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "ACCEPTED",
                "timestamp": accepted_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Sipariş restoran tarafından kabul edildi.",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "RESTAURANT"
            })
            status_history_id += 1

        if purchase["status"] == "PREPARING" or purchase["status"] in ["READY", "COMPLETED"]:
            preparing_time = purchase_time + timedelta(minutes=random.randint(20, 30))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "PREPARING",
                "timestamp": preparing_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Siparişiniz hazırlanıyor.",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "RESTAURANT"
            })
            status_history_id += 1

        if purchase["status"] == "READY" or purchase["status"] == "COMPLETED":
            ready_time = purchase_time + timedelta(minutes=random.randint(35, 50))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "READY",
                "timestamp": ready_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Siparişiniz hazır." if not purchase["is_delivery"] else "Siparişiniz teslimata hazır.",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "RESTAURANT"
            })
            status_history_id += 1

        if purchase["status"] == "COMPLETED":
            # For delivery orders, add "OUT_FOR_DELIVERY" status
            if purchase["is_delivery"]:
                out_time = purchase_time + timedelta(minutes=random.randint(50, 65))
                purchase_status_history.append({
                    "id": status_history_id,
                    "purchase_id": purchase["id"],
                    "status": "OUT_FOR_DELIVERY",
                    "timestamp": out_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": f"Siparişiniz {purchase['delivery_person'] or 'kurye'} ile yolda.",
                    "user_id": purchase["user_id"],
                    "restaurant_id": purchase["restaurant_id"],
                    "created_by": "DELIVERY"
                })
                status_history_id += 1

            completed_time = purchase_time + timedelta(minutes=random.randint(55, 90))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "COMPLETED",
                "timestamp": completed_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": "Sipariş teslim edildi.",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "SYSTEM"
            })
            status_history_id += 1

        elif purchase["status"] == "REJECTED":
            rejected_time = purchase_time + timedelta(minutes=random.randint(5, 20))
            reason = random.choice([
                "Restoran çok yoğun.",
                "Ürün stokta kalmadı.",
                "Restoran kapanma saati yaklaştı.",
                "Teslimat bölgesi çok uzak.",
                "Malzeme tedarik sorunu.",
                "Personel eksikliği.",
                "Mutfak ekipmanı arızası.",
                "Hava koşulları nedeniyle teslimat yapılamıyor."
            ])
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "REJECTED",
                "timestamp": rejected_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": f"Sipariş reddedildi. Sebep: {reason}",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "RESTAURANT"
            })
            status_history_id += 1

        elif purchase["status"] == "CANCELLED":
            cancelled_time = purchase_time + timedelta(minutes=random.randint(2, 30))
            purchase_status_history.append({
                "id": status_history_id,
                "purchase_id": purchase["id"],
                "status": "CANCELLED",
                "timestamp": cancelled_time.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": f"Sipariş iptal edildi. Sebep: {purchase['cancellation_reason']}",
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "created_by": "USER" if random.random() < 0.7 else "RESTAURANT"  # 70% cancelled by user
            })
            status_history_id += 1

    # Generate restaurant comments (reviews) with more variety
    restaurant_comments = []
    comment_count = 0

    # More varied comment texts
    positive_comments = [
        "Yemekler çok lezzetliydi, tavsiye ederim.",
        "Servis hızlı ve yemekler muhteşemdi.",
        "Fiyat performans açısından gayet iyi.",
        "Her zamanki gibi harika lezzetler.",
        "Harika bir deneyimdi, kesinlikle tekrar geleceğim.",
        "Çok beğendim, ailemle tekrar geleceğim.",
        "Personel çok ilgiliydi, teşekkürler.",
        "Temiz ve lezzetli, başka ne olsun!",
        "Ürünler tazeydi, fiyatlar uygundu.",
        "Hızlı teslimat ve sıcak yemekler için teşekkürler."
    ]

    neutral_comments = [
        "Ortalama bir yemek deneyimiydi.",
        "Fena değildi ama daha iyi olabilir.",
        "Bazı yemekler güzel bazıları vasat.",
        "İlk deneyimim daha iyiydi açıkçası.",
        "Yemekler iyi ama porsiyon küçüktü."
    ]

    negative_comments = [
        "Porsiyonlar küçüktü ve geç geldi.",
        "Beklentilerimi karşılamadı.",
        "Temizlik konusunda daha dikkatli olabilirler.",
        "Çok geç geldi ve soğuktu.",
        "Fiyatı hak etmiyor, bir daha tercih etmem.",
        "Siparişim eksikti, sorun çözülmedi.",
        "Lezzet beklediğim gibi değildi.",
        "Paketleme özensizdi, yemek dökülmüştü."
    ]

    for purchase in purchases:
        if purchase[
            "status"] == "COMPLETED" and random.random() < 0.75:  # 75% of completed purchases have reviews (increased from 70%)
            review_date = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 5))  # Increased max days
            rating = random.randint(1, 5)

            # Select comment based on rating
            if rating >= 4:
                comment_text = random.choice(positive_comments)
            elif rating == 3:
                comment_text = random.choice(neutral_comments)
            else:
                comment_text = random.choice(negative_comments)

            comment = {
                "id": comment_count + 1,
                "user_id": purchase["user_id"],
                "restaurant_id": purchase["restaurant_id"],
                "purchase_id": purchase["id"],
                "rating": rating,
                "comment": comment_text,
                "timestamp": review_date.strftime("%Y-%m-%d %H:%M:%S"),
                "helpful_count": random.randint(0, 25),  # New field
                "reply": random.choice(
                    [None, "Değerli yorumunuz için teşekkür ederiz.", "Deneyiminizi paylaştığınız için teşekkürler.",
                     "Sorun için özür dileriz, bir dahaki sefere daha iyi olacağız."]) if random.random() < 0.3 else None,
                # New field - 30% have replies
                "reply_timestamp": (review_date + timedelta(days=random.randint(1, 3))).strftime(
                    "%Y-%m-%d %H:%M:%S") if random.random() < 0.3 else None,  # New field
                "has_images": random.choice([True, False]) if rating <= 3 else False,
                # New field - negative reviews more likely to have images
                "image_urls": [f"https://example.com/images/reviews/{comment_count + 1}_{i}.jpg" for i in
                               range(1, random.randint(1, 3))] if rating <= 3 and random.random() < 0.4 else []
                # New field
            }
            restaurant_comments.append(comment)
            comment_count += 1

    # Generate comment badges with more variety
    comment_badges = []
    badge_id = 1

    for comment in restaurant_comments:
        # Each comment might have 0-4 badges (increased from 0-3)
        num_badges = random.randint(0, 4)
        positive_badges = ["Fresh Food", "Fast Delivery", "Customer Friendly", "Great Value",
                           "Eco Friendly"]  # Added 2 new badges
        negative_badges = ["Not Fresh", "Slow Delivery", "Not Customer Friendly", "Overpriced",
                           "Poor Packaging"]  # Added 2 new badges

        # If rating is high, bias towards positive badges
        available_badges = positive_badges + (negative_badges if comment["rating"] <= 3 else [])

        if num_badges > 0:
            selected_badges = random.sample(available_badges, min(num_badges, len(available_badges)))

            for badge_name in selected_badges:
                badge = {
                    "id": badge_id,
                    "comment_id": comment["id"],
                    "badge_name": badge_name,
                    "is_positive": badge_name in positive_badges,
                    "count": random.randint(1, 5)  # New field - how many users agreed with this badge
                }
                comment_badges.append(badge)
                badge_id += 1

    # Generate achievements with more options
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
        },
        {
            "id": 8,
            "name": "Local Champion",
            "description": "Made purchases from 10 different restaurants in your district",
            "badge_image_url": "https://example.com/badges/local_champion.png",
            "achievement_type": "LOCAL_RESTAURANTS",
            "threshold": 10,
            "is_active": True
        },
        {
            "id": 9,
            "name": "FreshDeal VIP",
            "description": "Spent over 1000₺ on FreshDeal",
            "badge_image_url": "https://example.com/badges/freshdeal_vip.png",
            "achievement_type": "TOTAL_SPENT",
            "threshold": 1000,
            "is_active": True
        },
        {
            "id": 10,
            "name": "Perfect Streak",
            "description": "Made a purchase every day for a week",
            "badge_image_url": "https://example.com/badges/perfect_streak.png",
            "achievement_type": "DAILY_PURCHASE",
            "threshold": 7,
            "is_active": True
        },
        {
            "id": 11,
            "name": "Night Owl",
            "description": "Made 5 purchases after 10PM",
            "badge_image_url": "https://example.com/badges/night_owl.png",
            "achievement_type": "NIGHT_PURCHASES",
            "threshold": 5,
            "is_active": True
        },
        {
            "id": 12,
            "name": "Top Reviewer",
            "description": "Got 50 'Helpful' votes on your reviews",
            "badge_image_url": "https://example.com/badges/top_reviewer.png",
            "achievement_type": "HELPFUL_REVIEWS",
            "threshold": 50,
            "is_active": True
        }
    ]

    # Generate user achievements with more variety
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
                "earned_at": user_purchases[0]["purchase_date"],
                "progress": 100,  # New field
                "notified": True  # New field
            })
            achievement_id += 1

        # Five Purchases achievement
        if len(user_purchases) >= 5:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 2,  # Five Purchases
                "earned_at": user_purchases[4]["purchase_date"],
                "progress": 100,
                "notified": True
            })
            achievement_id += 1
        elif len(user_purchases) > 0:  # In progress
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 2,  # Five Purchases
                "earned_at": None,
                "progress": (len(user_purchases) / 5) * 100,  # Calculate progress percentage
                "notified": False
            })
            achievement_id += 1

        # Regular Commenter
        if len(user_comments) >= 10:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 4,  # Regular Commenter
                "earned_at": user_comments[9]["timestamp"],
                "progress": 100,
                "notified": True
            })
            achievement_id += 1
        elif len(user_comments) > 0:  # In progress
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 4,  # Regular Commenter
                "earned_at": None,
                "progress": (len(user_comments) / 10) * 100,
                "notified": False
            })
            achievement_id += 1

        # Flash Deal Hunter
        flash_deal_purchases = [p for p in user_purchases if p["is_flash_deal"]]
        if len(flash_deal_purchases) >= 3:
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 6,  # Flash Deal Hunter
                "earned_at": flash_deal_purchases[2]["purchase_date"],
                "progress": 100,
                "notified": True
            })
            achievement_id += 1
        elif len(flash_deal_purchases) > 0:  # In progress
            user_achievements.append({
                "id": achievement_id,
                "user_id": user["id"],
                "achievement_id": 6,  # Flash Deal Hunter
                "earned_at": None,
                "progress": (len(flash_deal_purchases) / 3) * 100,
                "notified": False
            })
            achievement_id += 1

        # Food Explorer - ordered from different cuisines
        if len(user_purchases) > 0:
            # Get unique restaurant IDs
            user_restaurant_ids = list(set([p["restaurant_id"] for p in user_purchases]))
            # Get unique cuisines from these restaurants
            user_cuisines = list(set([r["category"] for r in restaurants if r["id"] in user_restaurant_ids]))

            if len(user_cuisines) >= 5:
                user_achievements.append({
                    "id": achievement_id,
                    "user_id": user["id"],
                    "achievement_id": 7,  # Food Explorer
                    "earned_at": user_purchases[-1]["purchase_date"],  # Use last purchase
                    "progress": 100,
                    "notified": True
                })
                achievement_id += 1
            elif len(user_cuisines) > 0:  # In progress
                user_achievements.append({
                    "id": achievement_id,
                    "user_id": user["id"],
                    "achievement_id": 7,  # Food Explorer
                    "earned_at": None,
                    "progress": (len(user_cuisines) / 5) * 100,
                    "notified": False
                })
                achievement_id += 1

        # FreshDeal VIP - spent over 1000₺
        if len(user_purchases) > 0:
            total_spent = sum([p["total_price"] for p in user_purchases])
            if total_spent >= 1000:
                # Find purchase that pushed user over the threshold
                spent_so_far = 0
                milestone_purchase_date = user_purchases[0]["purchase_date"]
                for p in sorted(user_purchases, key=lambda x: x["purchase_date"]):
                    spent_so_far += p["total_price"]
                    if spent_so_far >= 1000:
                        milestone_purchase_date = p["purchase_date"]
                        break

                user_achievements.append({
                    "id": achievement_id,
                    "user_id": user["id"],
                    "achievement_id": 9,  # FreshDeal VIP
                    "earned_at": milestone_purchase_date,
                    "progress": 100,
                    "notified": True
                })
                achievement_id += 1
            else:  # In progress
                user_achievements.append({
                    "id": achievement_id,
                    "user_id": user["id"],
                    "achievement_id": 9,  # FreshDeal VIP
                    "earned_at": None,
                    "progress": (total_spent / 1000) * 100,
                    "notified": False
                })
                achievement_id += 1

    # Generate environmental contributions
    environmental_contributions = []

    for i, purchase in enumerate(purchases):
        if purchase["status"] == "COMPLETED":
            # Calculate CO2 avoided based on purchase quantity and price
            co2_avoided = purchase["saved_co2"]

            contribution = {
                "id": i + 1,
                "user_id": purchase["user_id"],
                "purchase_id": purchase["id"],
                "co2_avoided": co2_avoided,
                "water_saved": round(co2_avoided * random.uniform(5.0, 15.0), 2),  # New field (liters)
                "food_saved": round(purchase["quantity"] * random.uniform(0.2, 0.8), 2),  # New field (kg)
                "created_at": purchase["purchase_date"],
                "impact_category": random.choice(["LOW", "MEDIUM", "HIGH"])  # New field
            }
            environmental_contributions.append(contribution)

    # Generate user environmental stats with more metrics
    user_env_stats = []

    for user in [u for u in users if u["role"] == "customer"]:
        user_contributions = [c for c in environmental_contributions if c["user_id"] == user["id"]]

        total_co2_saved = sum(c["co2_avoided"] for c in user_contributions)
        trees_equivalent = round(total_co2_saved / 25, 2)  # arbitrary conversion factor
        total_water_saved = sum(c["water_saved"] for c in user_contributions)
        total_food_saved = sum(c["food_saved"] for c in user_contributions)

        user_env_stats.append({
            "id": user["id"],
            "user_id": user["id"],
            "total_co2_saved": total_co2_saved,
            "trees_equivalent": trees_equivalent,
            "waste_reduced_kg": round(total_food_saved, 2),
            "water_saved_liters": round(total_water_saved, 2),
            "plastic_saved_kg": round(total_co2_saved * 0.1, 2),  # New field
            "rank": random.randint(1, len([u for u in users if u["role"] == "customer"])),  # New field
            "percentile": random.randint(1, 100),  # New field
            "monthly_impact": round(total_co2_saved / random.uniform(1.0, 6.0), 2),  # New field
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Generate user favorites with more metadata
    user_favorites = []
    favorite_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # Each customer might favorite 0-7 restaurants (increased from 0-5)
        num_favorites = random.randint(0, 7)

        if num_favorites > 0:
            # Randomly select restaurants to favorite without duplicates
            favorite_restaurants = random.sample(restaurants, min(num_favorites, len(restaurants)))

            for restaurant in favorite_restaurants:
                user_favorite = {
                    "id": favorite_id,
                    "user_id": user["id"],
                    "restaurant_id": restaurant["id"],
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 90))).strftime(
                        "%Y-%m-%d %H:%M:%S"),  # New field
                    "notes": random.choice([None, "İyi fiyatlar", "Hızlı teslimat", "Favori yerim", "Lezzetli"]),
                    # New field
                    "favorite_dishes": random.sample(
                        [l["title"] for l in listings if l["restaurant_id"] == restaurant["id"]], min(2, len([l for l in
                                                                                                                          listings
                                                                                                                          if l[
                                                                                                                              "restaurant_id"] ==
                                                                                                                          restaurant[
                                                                                                                              "id"]]))) if random.random() < 0.3 else []
                    # New field - 30% have favorite dishes
                }
                user_favorites.append(user_favorite)
                favorite_id += 1

    # Generate unique user recent restaurants list function
    def get_unique_recent_restaurants(user_id, max_count=5):
        """
        Get a list of unique recent restaurants for a user based on their purchase history.
        Only returns the most recent instance of each restaurant.
        """
        # Get all purchases for this user
        user_purchases = [p for p in purchases if p["user_id"] == user_id and p["status"] == "COMPLETED"]

        # Sort by purchase date, most recent first
        user_purchases.sort(key=lambda x: x["purchase_date"], reverse=True)

        # Track unique restaurants
        unique_restaurants = []
        restaurant_ids_added = set()

        # Add restaurants to the list if not already present
        for purchase in user_purchases:
            restaurant_id = purchase["restaurant_id"]
            if restaurant_id not in restaurant_ids_added:
                restaurant = next(r for r in restaurants if r["id"] == restaurant_id)
                unique_restaurants.append({
                    "restaurant_id": restaurant_id,
                    "restaurant_name": restaurant["restaurantName"],
                    "last_order_date": purchase["purchase_date"],
                    "items_ordered": purchase["quantity"],
                    "total_spent": purchase["total_price"]
                })
                restaurant_ids_added.add(restaurant_id)

            # Stop once we reach the desired count
            if len(unique_restaurants) >= max_count:
                break

        return unique_restaurants

    # Generate user recent restaurants data
    user_recent_restaurants = []

    for user in [u for u in users if u["role"] == "customer"]:
        recent_restaurants = get_unique_recent_restaurants(user["id"], max_count=5)

        if recent_restaurants:
            user_recent_restaurants.append({
                "user_id": user["id"],
                "recent_restaurants": recent_restaurants,
                "last_updated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            })

    # Generate user devices with more details
    user_devices = []
    device_id = 1

    device_types = ["iOS", "Android", "Web"]
    ios_platforms = ["iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15", "iPad Pro", "iPad Air", "iPad Mini"]
    android_platforms = ["Samsung Galaxy S22", "Samsung Galaxy S23", "Google Pixel 7", "Google Pixel 8",
                         "Xiaomi 13", "OnePlus 11", "Oppo Find X5"]
    web_browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
    os_versions = ["iOS 16.5", "iOS 17.1", "Android 13", "Android 14", "Windows 11", "macOS Sonoma",
                   "Linux Ubuntu 22.04"]

    for user in users:
        # Each user might have 1-4 devices (increased from 1-3)
        num_devices = random.randint(1, 4)

        for _ in range(num_devices):
            device_type = random.choice(device_types)

            if device_type == "iOS":
                platform = random.choice(ios_platforms)
                os_version = random.choice([v for v in os_versions if v.startswith("iOS")])
            elif device_type == "Android":
                platform = random.choice(android_platforms)
                os_version = random.choice([v for v in os_versions if v.startswith("Android")])
            else:  # Web
                platform = random.choice(web_browsers)
                os_version = random.choice(
                    [v for v in os_versions if not v.startswith("iOS") and not v.startswith("Android")])

            user_device = {
                "id": device_id,
                "user_id": user["id"],
                "push_token": str(uuid.uuid4()),
                "web_push_token": str(uuid.uuid4()) if device_type == "Web" else None,
                "device_type": device_type,
                "platform": platform,
                "os_version": os_version,  # New field
                "app_version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}" if device_type != "Web" else None,
                # New field
                "created_at": (datetime.now(UTC) - timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d %H:%M:%S"),
                "last_used": (datetime.now(UTC) - timedelta(days=random.randint(0, 15))).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True,
                "device_name": random.choice(["Ana Cihaz", "İş Telefonu", "Ev Tableti", None]),  # New field
                "location_services_enabled": random.choice([True, False])  # New field
            }
            user_devices.append(user_device)
            device_id += 1

    # Generate restaurant punishments with more details
    restaurant_punishments = []
    punishment_id = 1
    punishment_types = ["PERMANENT", "TEMPORARY", "TEMPORARY", "WARNING"]  # Added WARNING type
    support_user_ids = [user["id"] for user in users if user["role"] == "support"]

    for restaurant in restaurants:
        # 15% chance of a restaurant having a punishment (increased from 10%)
        if random.random() < 0.15:
            punishment_type = random.choice(punishment_types)
            punishment_start = datetime.now(UTC) - timedelta(days=random.randint(1, 20))
            support_user_id = random.choice(support_user_ids)

            # For temporary punishments, set end date
            if punishment_type == "TEMPORARY":
                duration_days = random.choice([3, 7, 14, 30, 60])  # Added 60 days option
                punishment_end = punishment_start + timedelta(days=duration_days)
            else:
                duration_days = None
                punishment_end = None

            # 25% chance the punishment is reverted (increased from 20%)
            is_reverted = random.random() < 0.25 if punishment_type != "WARNING" else random.random() < 0.5  # Warnings more likely to be reverted
            is_active = not is_reverted

            reverted_at = None
            reverted_by = None
            reversion_reason = None

            if is_reverted:
                reverted_at = punishment_start + timedelta(days=random.randint(1, 5))  # Extended from 1-3 to 1-5
                reverted_by = random.choice(support_user_ids)
                reversion_reason = random.choice([
                    "Punishment was issued by mistake",
                    "Issue resolved with restaurant",
                    "Restaurant appealed successfully",
                    "Investigation completed, punishment no longer needed",
                    "Restaurant provided evidence contradicting accusations",
                    "Issue was due to system error",
                    "Restaurant completed required improvements"
                ])

            punishment = {
                "id": punishment_id,
                "restaurant_id": restaurant["id"],
                "reason": random.choice([
                    "Multiple reported issues with food quality",
                    "Late deliveries",
                    "Poor customer service",
                    "Hygiene concerns",
                    "Multiple cancellations",
                    "Incorrect menu information",
                    "Pricing discrepancies",
                    "Health code violations",
                    "Staff conduct issues",
                    "False advertising"
                ]),
                "punishment_type": punishment_type,
                "duration_days": duration_days,
                "start_date": punishment_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": punishment_end.strftime("%Y-%m-%d %H:%M:%S") if punishment_end else None,
                "created_by": support_user_id,
                "created_at": punishment_start.strftime("%Y-%m-%d %H:%M:%S"),
                "severity_level": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),  # New field
                "investigation_notes": random.choice([
                    "Multiple customer complaints verified",
                    "Site inspection conducted on " + (
                                punishment_start - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
                    "Review of delivery performance metrics",
                    "Customer interview results",
                    "Health department coordination",
                    None
                ]),  # New field
                "is_active": is_active,
                "is_reverted": is_reverted,
                "reverted_by": reverted_by,
                "reverted_at": reverted_at.strftime("%Y-%m-%d %H:%M:%S") if reverted_at else None,
                "reversion_reason": reversion_reason,
                "follow_up_date": (punishment_start + timedelta(days=random.randint(30, 90))).strftime(
                    "%Y-%m-%d %H:%M:%S") if punishment_type != "PERMANENT" else None  # New field
            }
            restaurant_punishments.append(punishment)
            punishment_id += 1

    # Generate purchase reports with more detail
    purchase_reports = []
    report_id = 1

    # For each completed purchase, generate a report with specified probability
    for purchase in [p for p in purchases if p["status"] == "COMPLETED"]:
        if random.random() < 0.15:  # 15% chance of having a report (increased from 10%)
            report_status = random.choice(["active", "under_review", "resolved", "inactive"])
            reported_at = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 5))  # Increased from 1-3

            resolved_at = None
            resolved_by = None
            punishment_id_ref = None

            # Additional report details
            report_severity = random.choice(["LOW", "MEDIUM", "HIGH"])
            customer_compensation = None

            if report_status in ["resolved", "inactive"]:
                resolved_at = reported_at + timedelta(days=random.randint(1, 7))  # Increased from 1-5
                resolved_by = random.choice(support_user_ids)

                # Compensation for resolved reports
                if report_status == "resolved" and random.random() < 0.7:  # 70% chance for compensation
                    customer_compensation = round(purchase["total_price"] * random.choice([0.5, 0.75, 1.0, 1.25]), 2)

                # If resolved and 40% chance, link it to a punishment (increased from 30%)
                if report_status == "resolved" and random.random() < 0.4:
                    # Find punishments for this restaurant
                    restaurant_id = purchase["restaurant_id"]
                    restaurant_punishments_list = [p for p in restaurant_punishments if
                                                   p["restaurant_id"] == restaurant_id]
                    if restaurant_punishments_list:
                        punishment_id_ref = random.choice(restaurant_punishments_list)["id"]

            # Issue categories
            issue_categories = [
                "Food Quality", "Delivery Issue", "Packaging Problem", "Wrong Order",
                "Missing Items", "Temperature Issue", "Late Delivery", "Hygiene Concern",
                "Portion Size", "Customer Service", "Price Discrepancy"
            ]

            report_category = random.choice(issue_categories)

            # Generate report descriptions based on category
            if report_category == "Food Quality":
                description = random.choice([
                    "The food was cold when it arrived",
                    "The quality was not as described",
                    "Food seemed spoiled",
                    "The food tasted bad",
                    "Items were undercooked"
                ])
            elif report_category == "Delivery Issue":
                description = random.choice([
                    "Very long delivery time",
                    "Delivery person was rude",
                    "Delivery to wrong address",
                    "Courier refused to come to the door"
                ])
            elif report_category == "Packaging Problem":
                description = random.choice([
                    "Food was spilled in the bag",
                    "Packaging was damaged",
                    "Containers were leaking",
                    "No utensils included as requested"
                ])
            else:
                description = random.choice([
                    "The order was incomplete",
                    "Wrong items in the order",
                    "Portion size was much smaller than expected",
                    "Item was not as described on menu",
                    "Too spicy despite requesting mild"
                ])

            report = {
                "id": report_id,
                "user_id": purchase["user_id"],
                "purchase_id": purchase["id"],
                "restaurant_id": purchase["restaurant_id"],
                "listing_id": purchase["listing_id"],
                "report_category": report_category,  # New field
                "severity": report_severity,  # New field
                "image_url": f"https://example.com/images/reports/{report_id}.jpg",
                "image_count": random.randint(1, 3),  # New field
                "description": description,
                "status": report_status,
                "reported_at": reported_at.strftime("%Y-%m-%d %H:%M:%S"),
                "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else None,
                "resolved_by": resolved_by,
                "punishment_id": punishment_id_ref,
                "customer_contacted": random.choice([True, False]),  # New field
                "restaurant_contacted": random.choice([True, False]),  # New field
                "compensation_amount": customer_compensation,  # New field
                "restaurant_response": random.choice([
                    "We apologize for the issue and will improve our service.",
                    "This was a one-time error that has been addressed.",
                    "We will retrain our staff to prevent this in the future.",
                    "We've identified the problem and fixed our processes.",
                    None
                ]) if random.random() < 0.6 else None  # New field - 60% have a response
            }
            purchase_reports.append(report)
            report_id += 1

    # Generate refund records with more details
    refund_records = []
    refund_id = 1

    refund_reasons = [
        "Food quality issues",
        "Late delivery",
        "Wrong order",
        "Customer complaint",
        "Restaurant request",
        "Order cancellation",
        "App technical issue",
        "Payment processing error",
        "Missing items",
        "Health concern"
    ]

    for purchase in purchases:
        # 8% chance of a purchase having a refund if it's COMPLETED, REJECTED, or CANCELLED (increased from 5%)
        if purchase["status"] in ["COMPLETED", "REJECTED", "CANCELLED"] and random.random() < 0.08:
            refund_date = datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                days=random.randint(1, 5))

            # Determine refund percentage
            refund_percentage = random.choice([25, 50, 75, 100])
            refund_amount = round((purchase["total_price"] * refund_percentage) / 100, 2)

            # Select refund reason
            refund_reason = random.choice(refund_reasons)

            # Determine processing time
            processing_days = random.randint(1, 5)
            processed_date = refund_date + timedelta(days=processing_days)

            # Determine who requested the refund
            requested_by = random.choice(["CUSTOMER", "RESTAURANT", "SUPPORT"])

            refund = {
                "id": refund_id,
                "restaurant_id": purchase["restaurant_id"],
                "user_id": purchase["user_id"],
                "order_id": purchase["id"],
                "amount": refund_amount,
                "percentage": refund_percentage,  # New field
                "reason": refund_reason,
                "detailed_reason": f"{refund_reason} - {random.choice(['Customer was unsatisfied', 'Service standards not met', 'Policy compliance', 'Goodwill gesture'])}",
                # New field
                "requested_by": requested_by,  # New field
                "processed": True,
                "processing_time_days": processing_days,  # New field
                "payment_method": random.choice(["ORIGINAL_PAYMENT", "ACCOUNT_CREDIT", "BANK_TRANSFER"]),
                # New field
                "created_by": random.choice(support_user_ids),
                "created_at": refund_date.strftime("%Y-%m-%d %H:%M:%S"),
                "processed_at": processed_date.strftime("%Y-%m-%d %H:%M:%S"),  # New field
                "customer_notified": random.choice([True, False]),  # New field
                "restaurant_charged": random.choice([True, False]),  # New field
                "notes": random.choice([
                    "Customer was very upset, approved full refund",
                    "Partial refund as compromise solution",
                    "Restaurant agreed to cover full refund cost",
                    "System issue, refund processed as goodwill",
                    None
                ])  # New field
            }
            refund_records.append(refund)
            refund_id += 1

    # Generate user cart items with more detail
    user_cart_items = []
    cart_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # 50% chance of a user having items in cart (increased from 40%)
        if random.random() < 0.5:
            # 1-5 items in cart (increased from 1-3)
            num_items = random.randint(1, 5)

            # Randomly select listings to add to cart
            cart_listings = random.sample(listings, min(num_items, len(listings)))

            for listing in cart_listings:
                restaurant = next(r for r in restaurants if r["id"] == listing["restaurant_id"])
                quantity = random.randint(1, 4)

                cart_item = {
                    "id": cart_id,
                    "user_id": user["id"],
                    "listing_id": listing["id"],
                    "restaurant_id": restaurant["id"],
                    "count": quantity,
                    "added_at": (datetime.now(UTC) - timedelta(hours=random.randint(1, 96))).strftime(
                        "%Y-%m-%d %H:%M:%S"),  # Increased from 72 hours
                    "price_at_add": listing["pick_up_price"] if listing["pick_up_price"] else listing[
                                                                                                  "original_price"] * 0.7,
                    # New field
                    "notes": random.choice([None, "Az baharatlı", "Soğansız", "Fazla ketçap", "Ekstra malzeme"]),
                    # New field
                    "is_flash_deal": random.choice([True, False]) if any(
                        fd["listing_id"] == listing["id"] for fd in flash_deals) else False  # New field
                }
                user_cart_items.append(cart_item)
                cart_id += 1

    # Generate discounts earned with more variety
    discounts_earned = []
    discount_id = 1

    discount_types = ["WELCOME", "LOYALTY", "REFERRAL", "SPECIAL", "COMPENSATION"]

    for user in [u for u in users if u["role"] == "customer"]:
        # 40% chance of a user having earned discounts (increased from 30%)
        if random.random() < 0.4:
            # 1-5 discounts earned (increased from 1-3)
            num_discounts = random.randint(1, 5)

            for i in range(num_discounts):
                discount_type = random.choice(discount_types)

                if discount_type == "WELCOME":
                    discount_amount = 15.0  # Fixed welcome discount
                    description = "Hoş geldin indirimi"
                    expiry_days = 7
                elif discount_type == "LOYALTY":
                    discount_amount = round(random.uniform(10.0, 25.0), 2)
                    description = f"{random.randint(5, 15)}. siparişinize özel indirim"
                    expiry_days = 30
                elif discount_type == "REFERRAL":
                    discount_amount = 20.0  # Fixed referral discount
                    description = "Arkadaş davet indirimi"
                    expiry_days = 14
                elif discount_type == "SPECIAL":
                    discount_amount = round(random.uniform(15.0, 30.0), 2)
                    description = random.choice(["Bayram indirimi", "Doğum günü hediyesi", "Yıldönümü indirimi"])
                    expiry_days = 10
                else:  # COMPENSATION
                    discount_amount = round(random.uniform(10.0, 50.0), 2)
                    description = "Yaşadığınız sorun için telafi indirimi"
                    expiry_days = 45

                earned_date = (datetime.now(UTC) - timedelta(days=random.randint(1, 45))).strftime(
                    "%Y-%m-%d %H:%M:%S")
                expiry_date = (datetime.strptime(earned_date, "%Y-%m-%d %H:%M:%S") + timedelta(
                    days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")

                # Determine if the discount has been used
                is_used = random.choice([True, False])
                used_date = (datetime.strptime(earned_date, "%Y-%m-%d %H:%M:%S") + timedelta(
                    days=random.randint(1, expiry_days))).strftime("%Y-%m-%d %H:%M:%S") if is_used else None

                # Determine if the discount has expired (if not used)
                is_expired = not is_used and datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC) < datetime.now(UTC)

                discount = {
                    "id": discount_id,
                    "user_id": user["id"],
                    "discount": discount_amount,
                    "discount_type": discount_type,  # New field
                    "description": description,  # New field
                    "earned_at": earned_date,
                    "expires_at": expiry_date,  # New field
                    "is_used": is_used,  # New field
                    "used_at": used_date,  # New field
                    "is_expired": is_expired,  # New field
                    "minimum_order_amount": round(discount_amount * random.uniform(2.0, 4.0), 2),  # New field
                    "code": f"FRESH{user['id']}{discount_id}{random.randint(1000, 9999)}".upper()  # New field
                }
                discounts_earned.append(discount)
                discount_id += 1

    # Generate notification settings with more options
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
            "achievement_notifications": random.choice([True, False]),
            "reminder_notifications": random.choice([True, False]),  # New field
            "environmental_impact_updates": random.choice([True, False]),  # New field
            "favorite_restaurant_deals": random.choice([True, False]),  # New field
            "weekly_summary": random.choice([True, False]),  # New field
            "quiet_hours_enabled": random.choice([True, False]),  # New field
            "quiet_hours_start": f"{random.randint(20, 23)}:00" if random.choice([True, False]) else None,
            # New field
            "quiet_hours_end": f"{random.randint(6, 9)}:00" if random.choice([True, False]) else None,  # New field
            "notification_sounds_enabled": random.choice([True, False])  # New field
        }
        notification_settings.append(settings)

    # Generate user notifications with more variety
    user_notifications = []
    notification_id = 1

    notification_categories = [
        "ORDER_STATUS", "FLASH_DEAL", "ACHIEVEMENT", "MARKETING",
        "REFUND", "SYSTEM", "ENVIRONMENTAL", "REMINDER", "SUPPORT"
    ]

    for user in [u for u in users if u["role"] == "customer"]:
        # Generate 5-20 random notifications for each user (increased from 5-15)
        num_notifications = random.randint(5, 20)

        for _ in range(num_notifications):
            # Generate a notification date within the last 45 days (increased from 30)
            notification_date = datetime.now(UTC) - timedelta(days=random.randint(0, 45),
                                                              hours=random.randint(0, 23),
                                                              minutes=random.randint(0, 59))

            notification_type = random.choice(notification_categories)

            # Generate notification content based on type
            if notification_type == "ORDER_STATUS":
                title = "Sipariş Durumu Güncellendi"
                message = f"Siparişiniz {random.choice(['hazırlanıyor', 'yola çıktı', 'teslim edildi', 'kabul edildi', 'hazır'])}"
                priority = "HIGH"
            elif notification_type == "FLASH_DEAL":
                title = "Yeni Flash İndirim!"
                message = f"Son {random.randint(1, 8)} saate özel %{random.randint(30, 70)} indirim fırsatı kaçırmayın!"
                priority = "MEDIUM"
            elif notification_type == "ACHIEVEMENT":
                title = "Yeni Başarı Kazandınız!"
                message = f"Tebrikler! '{random.choice([a['name'] for a in achievements])}' başarısını kazandınız."
                priority = "MEDIUM"
            elif notification_type == "MARKETING":
                title = "Özel Teklif"
                message = f"Bu hafta sonu siparişlerinizde %{random.randint(10, 30)} indirim sizleri bekliyor."
                priority = "LOW"
            elif notification_type == "REFUND":
                title = "İade İşlemi Tamamlandı"
                message = "Talebiniz üzerine iade işleminiz tamamlandı. Tutar hesabınıza aktarıldı."
                priority = "HIGH"
            elif notification_type == "ENVIRONMENTAL":
                title = "Çevresel Etkiniz"
                message = f"Bu ay yaptığınız alışverişlerle {random.randint(1, 10)} kg CO2 salınımını önlediniz!"
                priority = "LOW"
            elif notification_type == "REMINDER":
                title = "Sepetiniz Sizi Bekliyor"
                message = "Sepetinizdeki ürünler tükenmeden siparişinizi tamamlayın."
                priority = "MEDIUM"
            elif notification_type == "SUPPORT":
                title = "Destek Yanıtı"
                message = "Gönderdiğiniz destek talebine yanıt geldi. İncelemek için tıklayın."
                priority = "HIGH"
            else:  # SYSTEM
                title = "Sistem Bildirimi"
                message = "Uygulamamızı güncelledik! Yeni özellikleri keşfedin."
                priority = "MEDIUM"

            # Determine if notification was read
            is_read = random.random() < 0.7  # 70% chance notification is read
            read_time = (notification_date + timedelta(minutes=random.randint(1, 120))).strftime(
                "%Y-%m-%d %H:%M:%S") if is_read else None

            notification = {
                "id": notification_id,
                "user_id": user["id"],
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "priority": priority,  # New field
                "read": is_read,
                "sent_at": notification_date.strftime("%Y-%m-%d %H:%M:%S"),
                "read_at": read_time,
                "expires_at": (notification_date + timedelta(days=random.randint(7, 30))).strftime(
                    "%Y-%m-%d %H:%M:%S") if notification_type in ["FLASH_DEAL", "MARKETING"] else None,  # New field
                "action_link": f"/orders/{random.randint(1, 100)}" if notification_type == "ORDER_STATUS" else None,
                "action_text": random.choice(
                    ["Görüntüle", "İncele", "Sipariş Detayı", "Devam Et"]) if random.random() < 0.5 else None,
                # New field
                "image_url": f"https://example.com/images/notifications/{notification_id}.jpg" if random.random() < 0.3 else None
                # New field - 30% have images
            }
            user_notifications.append(notification)
            notification_id += 1

    # Generate payment methods with more variety
    payment_methods = []
    payment_id = 1

    for user in [u for u in users if u["role"] == "customer"]:
        # Each customer has 1-4 payment methods (increased from 1-3)
        num_methods = random.randint(1, 4)

        for i in range(num_methods):
            payment_type = random.choice(
                ["CREDIT_CARD", "DEBIT_CARD", "ONLINE_BANKING", "WALLET", "MOBILE_PAYMENT"])

            if payment_type in ["CREDIT_CARD", "DEBIT_CARD"]:
                card_provider = random.choice(["Visa", "Mastercard", "Amex", "Troy"])
                card_program = random.choice(
                    ["Bonus", "World", "Axess", "Maximum", "Cardfinans", "Paraf", "Wings", "Advantage"])

                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "provider": card_provider,  # New field
                    "card_name": card_program,
                    "card_holder_name": user["name"],  # New field
                    "last_four": f"{random.randint(1000, 9999)}",
                    "expiry_month": random.randint(1, 12),
                    "expiry_year": random.randint(2025, 2030),
                    "is_default": i == 0,  # First payment method is default
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    "card_color": random.choice(["BLUE", "BLACK", "RED", "GOLD", "PLATINUM"]),  # New field
                    "supports_installments": payment_type == "CREDIT_CARD",  # New field
                    "supports_contactless": random.choice([True, False])  # New field
                }
            elif payment_type == "ONLINE_BANKING":
                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "provider": "BANK",  # New field
                    "bank_name": random.choice(
                        ["Garanti", "İş Bankası", "Akbank", "Yapı Kredi", "Ziraat", "Vakıfbank", "QNB Finansbank",
                         "Halkbank"]),
                    "account_name": user["name"],
                    "last_four": None,
                    "expiry_month": None,
                    "expiry_year": None,
                    "is_default": i == 0,
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    "account_type": random.choice(["CHECKING", "SAVINGS"])  # New field
                }
            elif payment_type == "WALLET":
                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "provider": "FreshDeal Wallet",  # New field
                    "wallet_name": "FreshDeal Wallet",
                    "account_name": user["name"],
                    "last_four": None,
                    "expiry_month": None,
                    "expiry_year": None,
                    "is_default": i == 0,
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    "balance": round(random.uniform(0, 200), 2)  # New field
                }
            else:  # MOBILE_PAYMENT
                eligible_devices = [
                    d["id"]
                    for d in user_devices
                    if d["user_id"] == user["id"] and d["device_type"] in ["iOS", "Android"]
                ]
                method = {
                    "id": payment_id,
                    "user_id": user["id"],
                    "payment_type": payment_type,
                    "provider": random.choice(["Apple Pay", "Google Pay", "BKM Express", "Troy Pay"]),  # New field
                    "mobile_payment_name": random.choice(["Apple Pay", "Google Pay", "BKM Express", "Troy Pay"]),
                    "account_name": user["name"],
                    "last_four": None,
                    "expiry_month": None,
                    "expiry_year": None,
                    "is_default": i == 0,
                    "created_at": (datetime.now(UTC) - timedelta(days=random.randint(1, 365))).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "device_linked": random.choice(eligible_devices) if eligible_devices else None  # New field
                }

            payment_methods.append(method)
            payment_id += 1

    # Generate payments with more detail
    payments = []
    payment_record_id = 1

    for purchase in purchases:
        # Get a payment method for this user
        user_payment_methods = [p for p in payment_methods if p["user_id"] == purchase["user_id"]]

        if user_payment_methods:
            payment_method = random.choice(user_payment_methods)

            # Determine payment status based on purchase status
            if purchase["status"] == "REJECTED":
                payment_status = random.choice(["FAILED", "REFUNDED"])
            elif purchase["status"] == "CANCELLED":
                payment_status = random.choice(["REFUNDED", "CANCELLED"])
            else:
                payment_status = "COMPLETED"

            # Determine payment provider based on payment method
            if payment_method["payment_type"] in ["CREDIT_CARD", "DEBIT_CARD"]:
                payment_provider = random.choice(["iyzico", "PayTR", "BeinConnect", "Masterpass"])

                # Generate installment details if credit card
                installments = 0
                if payment_method["payment_type"] == "CREDIT_CARD" and payment_method.get("supports_installments", False) and payment_status == "COMPLETED":
                    installments = random.choice([0, 0, 0, 3, 6, 9])

                payment_details = {
                    "card_type": payment_method.get("card_name"),
                    "card_provider": payment_method.get("provider"),
                    "installments": installments,
                    "installment_fee": round(purchase["total_price"] * 0.03, 2) if installments > 0 else 0
                }
            elif payment_method["payment_type"] == "ONLINE_BANKING":
                payment_provider = payment_method.get("bank_name")
                payment_details = {
                    "bank_name": payment_method.get("bank_name"),
                    "transfer_id": str(uuid.uuid4())[:8].upper(),
                    "account_type": payment_method.get("account_type")
                }
            elif payment_method["payment_type"] == "WALLET":
                payment_provider = "FreshDeal Wallet"
                payment_details = {
                    "wallet_name": payment_method.get("wallet_name"),
                    "wallet_transaction_id": str(uuid.uuid4())[:10].upper(),
                    "previous_balance": round(payment_method.get("balance", 0) + purchase["total_price"], 2),
                    "new_balance": payment_method.get("balance", 0)
                }
            else:  # MOBILE_PAYMENT
                payment_provider = payment_method.get("provider")
                payment_details = {
                    "mobile_payment_name": payment_method.get("mobile_payment_name"),
                    "device_id": payment_method.get("device_linked"),
                    "authentication_method": random.choice(["BIOMETRIC", "PIN", "PASSWORD"])
                }

            # Add failure details if payment failed
            if payment_status == "FAILED":
                payment_details["failure_reason"] = random.choice([
                    "Insufficient funds", "Card expired", "Authentication failed",
                    "Bank declined transaction", "Network error", "Timeout"
                ])
                payment_details["failure_code"] = f"ERR{random.randint(1000, 9999)}"

            payment = {
                "id": payment_record_id,
                "purchase_id": purchase["id"],
                "user_id": purchase["user_id"],
                "payment_method_id": payment_method["id"],
                "amount": purchase["total_price"],
                "status": payment_status,
                "transaction_id": str(uuid.uuid4()),
                "payment_date": purchase["purchase_date"],
                "payment_provider": payment_provider,
                "payment_details": json.dumps(payment_details),
                "processing_fee": round(purchase["total_price"] * random.uniform(0.01, 0.03), 2),  # New field
                "currency": "TRY",  # New field
                "is_test_payment": False,  # New field
                "received_at": (datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                    seconds=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"),  # New field
                "refunded_at": (datetime.strptime(purchase["purchase_date"], "%Y-%m-%d %H:%M:%S") + timedelta(
                    hours=random.randint(1, 48))).strftime(
                    "%Y-%m-%d %H:%M:%S") if payment_status == "REFUNDED" else None  # New field
            }
            payments.append(payment)
            payment_record_id += 1

    # Save data to JSON files
    def save_to_json(data, filename):
        with open(f"../exported_json/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Save files with names matching the database table names
    save_to_json(users, 'users.json')
    save_to_json(addresses, 'customeraddresses.json')
    save_to_json(restaurants, 'restaurants.json')
    save_to_json(restaurant_badge_points, 'restaurant_badge_points.json')
    save_to_json(categories, 'categories.json')
    save_to_json(restaurant_categories, 'restaurant_categories.json')
    save_to_json(menu_categories, 'menu_categories.json')
    save_to_json(listings, 'listings.json')
    save_to_json(flash_deals, 'flash_deals.json')
    save_to_json(purchases, 'purchases.json')
    save_to_json(purchase_status_history, 'purchase_status_history.json')
    save_to_json(restaurant_comments, 'restaurant_comments.json')
    save_to_json(comment_badges, 'comment_badges.json')
    save_to_json(achievements, 'achievements.json')
    save_to_json(user_achievements, 'user_achievements.json')
    save_to_json(environmental_contributions, 'environmental_contributions.json')
    save_to_json(user_env_stats, 'user_environmental_stats.json')
    save_to_json(user_favorites, 'user_favorites.json')
    save_to_json(user_recent_restaurants, 'user_recent_restaurants.json')  # New file with unique restaurants
    save_to_json(user_devices, 'user_devices.json')
    save_to_json(restaurant_punishments, 'restaurant_punishments.json')
    save_to_json(refund_records, 'refund_records.json')
    save_to_json(user_cart_items, 'user_cart.json')
    save_to_json(discounts_earned, 'discountearned.json')
    save_to_json(notification_settings, 'notification_settings.json')
    save_to_json(user_notifications, 'user_notifications.json')
    save_to_json(payment_methods, 'payment_methods.json')
    save_to_json(payments, 'payments.json')
    save_to_json(purchase_reports, 'purchase_reports.json')

    print("Enhanced sample data has been generated and saved to JSON files in ../exported_json/ directory:")
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
    print(f"- {len(user_recent_restaurants)} user recent restaurants (unique)")  # New stat
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
    print("\nAll locations are in İzmir districts: Karşıyaka, Bornova, Konak, Bayraklı, and Çiğli as expanded.")
    print("All passwords are set to the scrypt hash format as requested.")
    print("Environmental contributions have been set based on purchases.")
    print(
        "\nIMPORTANT: The unique recent restaurants function has been implemented - each restaurant appears only once in a user's recent restaurant list.")

if __name__ == "__main__":
    generate_sample_data()
