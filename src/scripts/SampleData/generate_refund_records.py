import json
import os
import random
from datetime import datetime, timedelta


def generate_refund_records():
    """
    Reads purchases.json and writes refund_records.json:
    - For each purchase with status in [COMPLETED, REJECTED, CANCELLED]
      there's an 8% chance of a refund record.
    - Fields include id, restaurant_id, user_id, order_id, amount, percentage,
      reason, detailed_reason, requested_by, processed, processing_time_days,
      created_by, created_at, processed_at, customer_notified, restaurant_charged, notes.
    """
    random.seed(42)
    # load purchases and users
    with open('../exported_json/purchases.json', 'r', encoding='utf-8') as f:
        purchases = json.load(f)
    with open('../exported_json/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    support_ids = [u['id'] for u in users if u['role'] == 'support'] or [u['id'] for u in users if u['role'] == 'owner']

    reasons = [
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
    notes_options = [
        "Customer was very upset, approved full refund",
        "Partial refund as compromise solution",
        "Restaurant agreed to cover full refund cost",
        "System issue, refund processed as goodwill",
        None
    ]

    refund_records = []
    rid = 1
    for p in purchases:
        if p['status'] not in ['COMPLETED', 'REJECTED', 'CANCELLED']:
            continue
        if random.random() >= 0.08:
            continue

        purchase_date = datetime.strptime(p['purchase_date'], "%Y-%m-%d %H:%M:%S")
        # refund timing
        created_at = purchase_date + timedelta(days=random.randint(1, 5))
        processing_time = random.randint(1, 5)
        processed_at = created_at + timedelta(days=processing_time)

        percent = random.choice([25, 50, 75, 100])
        amount = round(float(p['total_price']) * percent / 100, 2)

        reason = random.choice(reasons)
        detailed = f"{reason} - {random.choice(['Customer was unsatisfied', 'Service standards not met', 'Policy compliance', 'Goodwill gesture'])}"
        requested_by = random.choice(['CUSTOMER', 'RESTAURANT', 'SUPPORT'])
        processed = True
        customer_notified = random.choice([True, False])
        restaurant_charged = random.choice([True, False])
        notes = random.choice(notes_options)
        created_by = random.choice(support_ids)

        refund_records.append({
            'id': rid,
            'restaurant_id': p['restaurant_id'],
            'user_id': p['user_id'],
            'order_id': p['id'],
            'amount': amount,
            'percentage': percent,
            'reason': reason,
            'detailed_reason': detailed,
            'requested_by': requested_by,
            'processed': processed,
            'processing_time_days': processing_time,
            'created_by': created_by,
            'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'processed_at': processed_at.strftime("%Y-%m-%d %H:%M:%S"),
            'customer_notified': customer_notified,
            'restaurant_charged': restaurant_charged,
            'notes': notes
        })
        rid += 1

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/refund_records.json', 'w', encoding='utf-8') as f:
        json.dump(refund_records, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(refund_records)} refund records to ../exported_json/refund_records.json")


if __name__ == '__main__':
    generate_refund_records()
