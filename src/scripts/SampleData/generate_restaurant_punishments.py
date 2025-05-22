import json
import os
import random
from datetime import datetime, timedelta


def generate_restaurant_punishments():
    """
    Reads restaurants.json and users.json, then writes restaurant_punishments.json:
    - Exactly 3 or 4 restaurants get TEMPORARY punishments (no permanent or warning).
    - Types: always TEMPORARY.
    - All punishments took place in the past with random durations.
    - 20% chance to revert each punishment.
    """
    random.seed(42)
    # load restaurants and users
    with open('../exported_json/restaurants.json', 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    with open('../exported_json/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # choose 3 or 4 restaurants to punish
    num_punished = random.choice([3, 4])
    punished_rest_ids = random.sample([r['id'] for r in restaurants], num_punished)

    support_ids = [u['id'] for u in users if u['role'] in ('support', 'owner')]
    reasons = [
        "Multiple reported issues with food quality",
        "Late deliveries",
        "Poor customer service",
        "Hygiene concerns",
        "Multiple cancellations",
        "Incorrect menu information",
        "Pricing discrepancies",
        "Health code violations"
    ]
    reversion_reasons = [
        "Issue resolved with restaurant",
        "Restaurant appealed successfully",
        "Investigation completed, punishment no longer needed",
        "Punishment issued by mistake"
    ]
    severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    punishments = []
    pid = 1
    now = datetime.now()

    for rid in punished_rest_ids:
        punishment_type = "TEMPORARY"
        start_date = now - timedelta(days=random.randint(10, 30))
        duration_days = random.choice([3, 7, 14, 30])
        end_date = start_date + timedelta(days=duration_days)

        created_by = random.choice(support_ids)
        created_at = start_date.strftime("%Y-%m-%d %H:%M:%S")
        reason = random.choice(reasons)
        severity = random.choice(severity_levels)
        investigation_notes = f"Investigation conducted on {start_date.strftime('%Y-%m-%d')}"

        # determine reversion
        is_reverted = random.random() < 0.2
        reverted_by = None
        reverted_at = None
        reversion_reason = None
        if is_reverted:
            rv_days = random.randint(1, duration_days)
            reverted_at_dt = start_date + timedelta(days=rv_days)
            reverted_at = reverted_at_dt.strftime("%Y-%m-%d %H:%M:%S")
            reverted_by = random.choice(support_ids)
            reversion_reason = random.choice(reversion_reasons)

        # follow-up date
        follow_up_date = (start_date + timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d %H:%M:%S")

        punishments.append({
            'id': pid,
            'restaurant_id': rid,
            'reason': reason,
            'punishment_type': punishment_type,
            'duration_days': duration_days,
            'start_date': created_at,
            'end_date': end_date.strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': created_by,
            'created_at': created_at,
            'severity_level': severity,
            'investigation_notes': investigation_notes,
            'is_active': not is_reverted,
            'is_reverted': is_reverted,
            'reverted_by': reverted_by,
            'reverted_at': reverted_at,
            'reversion_reason': reversion_reason,
            'follow_up_date': follow_up_date
        })
        pid += 1

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/restaurant_punishments.json', 'w', encoding='utf-8') as f:
        json.dump(punishments, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(punishments)} restaurant punishments to ../exported_json/restaurant_punishments.json")

if __name__ == '__main__':
    generate_restaurant_punishments()