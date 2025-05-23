#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime, timedelta, timezone

def generate_discounts_earned():
    """
    Generates 2–5 discount‐earned records for each customer.
    Writes to ../exported_json/discountearned.json.
    """
    # Load users
    with open('../exported_json/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    records = []
    rec_id = 1

    # For each customer, generate 2–5 discount records
    for user in users:
        if user.get('role') != 'customer':
            continue

        # guarantee at least 2, up to 5 discounts per customer
        num = random.randint(2, 5)
        for _ in range(num):
            # pick a discount amount
            amount = random.choice([5.0, 10.0, 15.0, 20.0, 25.0])
            # random timestamp within last 60 days
            earned_at = datetime.now(timezone.utc) - timedelta(
                days=random.randint(0, 60),
                hours=random.randint(0,23),
                minutes=random.randint(0,59)
            )
            records.append({
                "id":        rec_id,
                "user_id":   user["id"],
                "discount":  round(amount, 2),
                "earned_at": earned_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            rec_id += 1

    # Ensure output dir exists
    os.makedirs('../exported_json', exist_ok=True)

    out_path = '../exported_json/discountearned.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(records)} discount‐earned records to {out_path}")

if __name__ == "__main__":
    # Seed for reproducibility (optional)
    random.seed(42)
    generate_discounts_earned()
