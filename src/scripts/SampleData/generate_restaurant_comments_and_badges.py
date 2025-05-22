import json
import os
import random
from datetime import datetime


def generate_comments_and_badges():
    """
    Generates restaurant_comments.json and comment_badges.json based
    on purchases. Reviews are assigned stars 1-5. Ratings >=3 are positive,
    ratings <=2 are negative. Positive reviews get 1-3 positive badges,
    negative reviews get 1-3 negative badges.
    """
    # load purchases, users, restaurants
    with open('../exported_json/purchases.json', 'r', encoding='utf-8') as f:
        purchases = json.load(f)

    # we only comment on completed purchases
    completed = [p for p in purchases if p['status'] == 'COMPLETED']

    # badge pools
    positive_badges = ['Fresh Food', 'Fast Delivery', 'Customer Friendly']
    negative_badges = ['Not Fresh', 'Slow Delivery', 'Not Customer Friendly']

    comments = []
    comment_badges = []
    comment_id = 1
    badge_id = 1

    for p in completed:
        # assign a deterministic star rating based on purchase_id
        # cycle: 1->5 stars, 2->4, 3->3, 4->2, 5->1
        cycle = p['id'] % 5
        rating = {1:5, 2:4, 3:3, 4:2, 0:1}[cycle]

        # simple comment text
        if rating >= 4:
            text = 'Yemek harikaydı, çok beğendim.'
        elif rating == 3:
            text = 'Fena değildi, ortalama bir deneyimdi.'
        else:
            text = 'Beklentimi karşılamadı, sorun vardı.'

        # timestamp use purchase_date
        ts = p['purchase_date']

        # build comment record
        comment = {
            'id': comment_id,
            'restaurant_id': p['restaurant_id'],
            'user_id': p['user_id'],
            'purchase_id': p['id'],
            'comment': text,
            'rating': float(rating),
            'timestamp': ts
        }
        comments.append(comment)

        # select badges
        if rating >= 3:
            # positive: choose 1-3 distinct positive badges
            count = random.randint(1,3)
            chosen = positive_badges[:count]
            for name in chosen:
                comment_badges.append({
                    'id': badge_id,
                    'comment_id': comment_id,
                    'badge_name': name,
                    'is_positive': True
                })
                badge_id += 1
        else:
            # negative: 1-3 negative
            count = random.randint(1,3)
            chosen = negative_badges[:count]
            for name in chosen:
                comment_badges.append({
                    'id': badge_id,
                    'comment_id': comment_id,
                    'badge_name': name,
                    'is_positive': False
                })
                badge_id += 1

        comment_id += 1

    # write outputs
    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/restaurant_comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    with open('../exported_json/comment_badges.json', 'w', encoding='utf-8') as f:
        json.dump(comment_badges, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(comments)} comments and {len(comment_badges)} badges to ../exported_json/")


if __name__ == '__main__':
    generate_comments_and_badges()
