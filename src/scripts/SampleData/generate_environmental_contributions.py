import json
import os
import random
from datetime import datetime

def generate_environmental_contributions():
    """
    Reads purchases.json and writes environmental_contributions.json:
    - One record per COMPLETED purchase
    - Fields: id, user_id, purchase_id, co2_avoided, created_at
    - If purchase has zero or missing saved_co2, assigns a random fallback (0.2–2.0 kg)
    """
    random.seed(42)
    # load purchases
    with open('../exported_json/purchases.json', 'r', encoding='utf-8') as f:
        purchases = json.load(f)

    contributions = []
    cid = 1
    for p in purchases:
        if p.get('status') != 'COMPLETED':
            continue

        # attempt to read saved_co2, fallback to random
        co2 = float(p.get('saved_co2', 0) or 0)
        if co2 <= 0:
            co2 = round(random.uniform(0.2, 2.0), 2)

        created_at = p.get('purchase_date')
        contributions.append({
            'id': cid,
            'user_id': p['user_id'],
            'purchase_id': p['id'],
            'co2_avoided': co2,
            'created_at': created_at
        })
        cid += 1

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/environmental_contributions.json', 'w', encoding='utf-8') as f:
        json.dump(contributions, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(contributions)} environmental contributions to ../exported_json/environmental_contributions.json")

if __name__ == '__main__':
    generate_environmental_contributions()
