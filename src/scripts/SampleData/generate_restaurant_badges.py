import json
import os
import random


def generate_restaurant_badge_points():
    """
    Generates random badge point summaries for each of the 10 restaurants and writes to
    ../exported_json/restaurant_badge_points.json. Ensures:
      - Restaurants 1–3 have at least one negative badge (>0).
      - Restaurants 8–10 have full positive badges (100 each).
      - Net positive minus negative points ≥ 100 for all restaurants.
    """
    random.seed(42)

    # load restaurants
    with open('../exported_json/restaurants.json', 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    badge_points = []
    for r in restaurants:
        rid = r['id']
        # base random positive scores 60-100
        if rid >= 8:
            fresh = 100
            fast = 100
            friendly = 100
        else:
            fresh = random.randint(60, 100)
            fast = random.randint(60, 100)
            friendly = random.randint(60, 100)

        # negative badges: most zero, but restaurants 1-3 get at least one
        if rid <= 3:
            not_fresh = random.randint(1, 20)
            slow = 0 if random.random() < 0.5 else random.randint(1, 20)
            not_friendly = 0 if random.random() < 0.5 else random.randint(1, 20)
        else:
            not_fresh = random.choice([0, random.randint(1, 20)])
            slow = random.choice([0, random.randint(1, 20)])
            not_friendly = random.choice([0, random.randint(1, 20)])

        # ensure net positive ≥ 100
        positives = fresh + fast + friendly
        negatives = not_fresh + slow + not_friendly
        net = positives - negatives
        if net < 100:
            # bump fresh to cover deficit
            deficit = 100 - net
            fresh += deficit

        pts = {
            "id": rid,
            "restaurantID": rid,
            "freshPoint": fresh,
            "fastDeliveryPoint": fast,
            "customerFriendlyPoint": friendly,
            "notFreshPoint": not_fresh,
            "slowDeliveryPoint": slow,
            "notCustomerFriendlyPoint": not_friendly
        }
        badge_points.append(pts)

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/restaurant_badge_points.json', 'w', encoding='utf-8') as f:
        json.dump(badge_points, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(badge_points)} badge-point records to ../exported_json/restaurant_badge_points.json")


if __name__ == "__main__":
    generate_restaurant_badge_points()
