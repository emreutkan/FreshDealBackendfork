#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import datetime

# 0) Locate dirs
SCRIPT_DIR   = os.path.dirname(__file__)                    # .../src/scripts
SAMPLES_DIR  = os.path.join(SCRIPT_DIR, 'SampleData')        # .../src/scripts/SampleData
# ← now point one level up to src/exported_json
EXPORT_JSON  = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'exported_json'))

# 1) Exactly the generators you've written, in dependency order:
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
        print(f"WARN: Missing generator, skipping: {script}")
        continue

    # comments need purchases.json
    if script == "generate_restaurant_comments_and_badges.py":
        if not os.path.exists(os.path.join(EXPORT_JSON, 'purchases.json')):
            print("WARN: purchases.json not yet generated; skipping comments_and_badges")
            continue

    print(f">> Running {script}")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    rc = subprocess.call([sys.executable, path], env=env)
    if rc != 0:
        print(f"ERROR: {script} failed with exit code {rc}")
        sys.exit(rc)

# 2) Import into MSSQL
print("\n=== Importing JSON into MSSQL ===")
load_dotenv()

# Get connection details from .env
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

if not all([DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_DRIVER]):
    sys.exit("ERROR: Missing one or more MSSQL connection details in .env (DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_DRIVER)")

# Create a direct ODBC connection
connection_string = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Get existing tables
cursor.execute(f"SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = '{DB_NAME}'")
existing_tables = [row[0] for row in cursor.fetchall()]
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
    "user_achievements.json",
    "environmental_contributions.json",
    "user_favorites.json",
    "user_cart.json",
    "user_devices.json",
    "discountearned.json",
]

# Helper function to get column names for a table
def get_table_columns(table_name):
    cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{table_name}'")
    return [row[0] for row in cursor.fetchall()]

# Helper function to parse date strings
def parse_date(date_str):
    if not date_str or date_str == 'null' or date_str is None:
        return None
    try:
        # Try standard format first
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try with milliseconds
            return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Try with just date
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")

# Process each file
for fname in ordered_files:
    table = table_map.get(fname, fname.rsplit('.',1)[0])
    if table not in existing_tables:
        print(f"WARN: Skipping {fname} (no table {table})")
        continue

    fpath = os.path.join(EXPORT_JSON, fname)
    if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
        print(f"WARN: Skipping missing/empty {fname}")
        continue

    print(f"Importing {fname} -> {table}")

    # Load the JSON data
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print(f"WARN: No data found in {fname}")
        continue

    # Ensure data is a list
    if not isinstance(data, list):
        data = [data]

    # Get table columns
    table_columns = get_table_columns(table)

    # Filter data to only include existing columns
    filtered_data = []
    for item in data:
        filtered_item = {k: v for k, v in item.items() if k in table_columns}
        filtered_data.append(filtered_item)

    if not filtered_data:
        print(f"WARN: No valid columns found for {table}")
        continue

    # Check for existing IDs
    if "id" in table_columns and table != 'user_achievements':
        try:
            cursor.execute(f"SELECT id FROM {table}")
            existing_ids = {row[0] for row in cursor.fetchall()}
            filtered_data = [item for item in filtered_data if item.get('id') not in existing_ids]
            if not filtered_data:
                print(f"INFO: All entries in {fname} for table {table} already exist based on ID. Skipping.")
                continue
        except Exception as e:
            print(f"WARN: Could not check existing IDs for table {table}, proceeding with insert. Error: {e}")

    # Handle special case for user_achievements
    if table == 'user_achievements':
        # Check for existing IDs
        try:
            cursor.execute("SELECT id FROM user_achievements")
            existing_ids = {row[0] for row in cursor.fetchall()}
            original_count = len(filtered_data)
            filtered_data = [item for item in filtered_data if item.get('id') not in existing_ids]
            if len(filtered_data) < original_count:
                print(f"INFO: Filtered out {original_count - len(filtered_data)} rows from {fname} for user_achievements due to duplicate IDs.")
        except Exception as e:
            print(f"WARN: Could not check existing IDs for user_achievements, proceeding. Error: {e}")

        # Check for existing user_id/achievement_id pairs
        if filtered_data and all(col in filtered_data[0] for col in ['user_id', 'achievement_id']):
            try:
                cursor.execute("SELECT user_id, achievement_id FROM user_achievements")
                existing_pairs = {(row[0], row[1]) for row in cursor.fetchall()}
                original_count = len(filtered_data)
                filtered_data = [item for item in filtered_data if (item.get('user_id'), item.get('achievement_id')) not in existing_pairs]
                if len(filtered_data) < original_count:
                    print(f"INFO: Filtered out {original_count - len(filtered_data)} rows from {fname} for user_achievements due to duplicate (user_id, achievement_id) pairs.")
            except Exception as e:
                print(f"WARN: Could not check unique (user_id, achievement_id) for user_achievements, proceeding. Error: {e}")

    if not filtered_data:
        print(f"INFO: No new data to insert for {table} from {fname} after filtering. Skipping.")
        continue

    # Get column names for insert
    columns = list(filtered_data[0].keys())

    # Create placeholders for SQL statement
    placeholders = ','.join(['?' for _ in columns])

    # Create column string for SQL statement
    column_str = ','.join(columns)

    # Set IDENTITY_INSERT ON if necessary
    identity_insert_was_set = False
    if 'id' in columns:
        try:
            cursor.execute(f"SET IDENTITY_INSERT {table} ON")
            identity_insert_was_set = True
        except Exception as e:
            print(f"WARN: Could not set IDENTITY_INSERT ON for {table}. Error: {e}")

    # Insert data row by row
    successful_rows = 0
    for item in filtered_data:
        try:
            # Convert datetime strings to datetime objects
            values = []
            for col in columns:
                value = item.get(col)
                # Convert date strings to datetime objects if the column name suggests it's a date
                if value and isinstance(value, str) and ('date' in col.lower() or 'time' in col.lower() or col in ['expires_at', 'created_at', 'earned_at']):
                    value = parse_date(value)
                values.append(value)

            # Execute the insert
            cursor.execute(f"INSERT INTO {table} ({column_str}) VALUES ({placeholders})", values)
            successful_rows += 1
        except Exception as e:
            print(f"Error inserting row in {table}: {e}")
            # Continue with next row

    # Set IDENTITY_INSERT OFF if it was set ON
    if identity_insert_was_set:
        try:
            cursor.execute(f"SET IDENTITY_INSERT {table} OFF")
        except Exception as e:
            print(f"WARN: Could not set IDENTITY_INSERT OFF for {table}. Error: {e}")

    # Commit the transaction
    conn.commit()
    print(f"OK: {successful_rows} rows added to {table}")

# Close the connection
conn.close()

print("\nSUCCESS: All sample-data JSON generated and imported successfully.")
