#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import pandas as pd
from sqlalchemy import create_engine, text, DateTime as SQLDateTime
from dotenv import load_dotenv

# 0) Locate dirs
SCRIPT_DIR   = os.path.dirname(__file__)                    # .../src/scripts
SAMPLES_DIR  = os.path.join(SCRIPT_DIR, 'SampleData')        # .../src/scripts/SampleData
# ← now point one level up to src/exported_json
EXPORT_JSON  = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'exported_json'))

# 1) Exactly the generators you’ve written, in dependency order:
generators = [
    "generate_users.py",
    "generate_user_address.py",
    "generate_restaurants.py",
    "generate_restaurant_badges.py",
    "generate_listings.py",
    "generate_purchases.py",
    "generate_refund_records.py",
    "generate_restaurant_comments_and_badges.py",
    "generate_restaurant_punishments.py",
    "generate_achievements.py",
    "generate_environmental_contributions.py",
    "generate_user_favorites_cart_and_devices.py",
    "generate_discounts_earned.py"

]

print("\n=== Generating JSON data ===")
for script in generators:
    path = os.path.join(SAMPLES_DIR, script)
    if not os.path.isfile(path):
        print(f"⚠️  Missing generator, skipping: {script}")
        continue

    # comments need purchases.json
    if script == "generate_restaurant_comments_and_badges.py":
        if not os.path.exists(os.path.join(EXPORT_JSON, 'purchases.json')):
            print("⚠️  purchases.json not yet generated; skipping comments_and_badges")
            continue

    print(f"▶️ Running {script}")
    rc = subprocess.call([sys.executable, path])
    if rc != 0:
        print(f"❌ {script} failed with exit code {rc}")
        sys.exit(rc)

# 2) Import into MySQL
print("\n=== Importing JSON into MySQL ===")
load_dotenv()
MYSQL_URI = os.getenv("MYSQL_URI")
if not MYSQL_URI:
    sys.exit("❌ Missing MYSQL_URI in .env")
engine = create_engine(MYSQL_URI)

# disable FK checks
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

# existing tables
with engine.connect() as conn:
    existing_tables = [r[0] for r in conn.execute(text("SHOW TABLES;"))]
    print(f"Existing tables: {existing_tables}")

# JSON filename → table name overrides
table_map = {
    "customeraddresses.json": "customeraddresses",
    "user_cart.json":         "user_cart",
    "purchase_reports.json":  "purchase_reports"
}

# import order
ordered_files = [
    "users.json",
    "customeraddresses.json",
    "restaurants.json",
    "restaurant_badge_points.json",
    "listings.json",
    "purchases.json",
    "refund_records.json",
    "restaurant_comments.json",
    "comment_badges.json",
    "restaurant_punishments.json",
    "achievements.json",
    "environmental_contributions.json",
    "user_favorites.json",
    "user_cart.json",
    "user_achievements.json",
    "user_devices.json",
    "discountearned.json",

]

for fname in ordered_files:
    table = table_map.get(fname, fname.rsplit('.',1)[0])
    if table not in existing_tables:
        print(f"⚠️  Skipping {fname} (no table {table})")
        continue

    fpath = os.path.join(EXPORT_JSON, fname)
    if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
        print(f"⚠️  Skipping missing/empty {fname}")
        continue

    print(f"Importing {fname} → {table}")
    data = json.load(open(fpath, encoding='utf-8'))
    df   = pd.DataFrame(data if isinstance(data, list) else [data])
    if df.empty:
        continue

    # keep only real columns
    cols = [c[0] for c in engine.connect().execute(text(f"DESCRIBE `{table}`;"))]
    df   = df[[c for c in df.columns if c in cols]]

    # drop already-present IDs
    if 'id' in df.columns:
        existing_ids = {r[0] for r in engine.connect().execute(text(f"SELECT id FROM `{table}`;"))}
        df = df[~df['id'].isin(existing_ids)]
        if df.empty:
            continue

    df.to_sql(
        table,
        engine,
        index=False,
        if_exists='append',
        dtype={c: SQLDateTime() for c in df.columns if 'date' in c.lower() or 'time' in c.lower()}
    )
    print(f"✅  {len(df)} rows added to {table}")

# re-enable FK checks
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

print("\n🎉 All sample-data JSON generated and imported successfully.")
