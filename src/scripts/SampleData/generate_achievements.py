import json
import os
from datetime import datetime, timedelta


def generate_achievements_and_user_achievements():
    """
    Generates achievements.json (7 static achievements) and user_achievements.json based on
    purchases and comments. Only FIRST_PURCHASE, Regular Buyer (5 purchases), and
    Weekly Champion (5 purchases in a 7-day window) are awarded here.
    """
    # static achievements
    achievements = [
        {
            "id": 1,
            "name": "First Purchase",
            "description": "Made your first purchase on FreshDeal",
            "badge_image_url": "/static/badges/first_purchase.png",
            "achievement_type": "FIRST_PURCHASE",
            "threshold": 1,
            "is_active": True
        },
        {
            "id": 2,
            "name": "Regular Buyer",
            "description": "Completed 5 purchases",
            "badge_image_url": "/static/badges/regular_buyer.png",
            "achievement_type": "PURCHASE_COUNT",
            "threshold": 5,
            "is_active": True
        },
        {
            "id": 3,
            "name": "Loyal Customer",
            "description": "Completed 25 purchases",
            "badge_image_url": "/static/badges/loyal_customer.png",
            "achievement_type": "PURCHASE_COUNT",
            "threshold": 25,
            "is_active": True
        },
        {
            "id": 4,
            "name": "FreshDeal VIP",
            "description": "Completed 50 purchases",
            "badge_image_url": "/static/badges/vip_customer.png",
            "achievement_type": "PURCHASE_COUNT",
            "threshold": 50,
            "is_active": True
        },
        {
            "id": 5,
            "name": "FreshDeal Legend",
            "description": "Completed 100 purchases",
            "badge_image_url": "/static/badges/legend_customer.png",
            "achievement_type": "PURCHASE_COUNT",
            "threshold": 100,
            "is_active": True
        },
        {
            "id": 6,
            "name": "Weekly Champion",
            "description": "Made 5 purchases in a week",
            "badge_image_url": "/static/badges/weekly_champion.png",
            "achievement_type": "WEEKLY_PURCHASE",
            "threshold": 5,
            "is_active": True
        },
        {
            "id": 7,
            "name": "Regular Commenter",
            "description": "Posted 100 comments in 90 days",
            "badge_image_url": "/static/badges/regular_commenter.png",
            "achievement_type": "REGULAR_COMMENTER",
            "threshold": 100,
            "is_active": True
        }
    ]

    # load purchases
    with open('../exported_json/purchases.json', 'r', encoding='utf-8') as f:
        purchases = json.load(f)

    # sort purchases by date
    for p in purchases:
        p['purchase_date'] = datetime.fromisoformat(p['purchase_date']) if 'T' in p['purchase_date'] else datetime.strptime(p['purchase_date'], "%Y-%m-%d %H:%M:%S")
    purchases.sort(key=lambda x: x['purchase_date'])

    # group by user
    users = {}
    for p in purchases:
        users.setdefault(p['user_id'], []).append(p['purchase_date'])

    user_achievements = []
    ua_id = 1

    for user_id, dates in users.items():
        # First Purchase
        first_date = dates[0]
        user_achievements.append({
            'id': ua_id,
            'user_id': user_id,
            'achievement_id': 1,
            'earned_at': first_date.strftime("%Y-%m-%d %H:%M:%S")
        })
        ua_id += 1

        # Regular Buyer (5 purchases)
        if len(dates) >= 5:
            fifth_date = dates[4]
            user_achievements.append({
                'id': ua_id,
                'user_id': user_id,
                'achievement_id': 2,
                'earned_at': fifth_date.strftime("%Y-%m-%d %H:%M:%S")
            })
            ua_id += 1

        # Weekly Champion: check any 7-day window with >=5
        for i in range(len(dates) - 4):
            if (dates[i+4] - dates[i]).days < 7:
                user_achievements.append({
                    'id': ua_id,
                    'user_id': user_id,
                    'achievement_id': 6,
                    'earned_at': dates[i+4].strftime("%Y-%m-%d %H:%M:%S")
                })
                ua_id += 1
                break

    # write outputs
    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/achievements.json', 'w', encoding='utf-8') as f:
        json.dump(achievements, f, ensure_ascii=False, indent=2)
    with open('../exported_json/user_achievements.json', 'w', encoding='utf-8') as f:
        json.dump(user_achievements, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(achievements)} achievements and {len(user_achievements)} user achievements.")

if __name__ == '__main__':
    generate_achievements_and_user_achievements()
