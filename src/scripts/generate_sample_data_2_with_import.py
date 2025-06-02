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

# Construct MSSQL URI from .env variables
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

if not all([DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_DRIVER]):
    sys.exit("ERROR: Missing one or more MSSQL connection details in .env (DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_DRIVER)")

MSSQL_URI = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"
engine = create_engine(MSSQL_URI)

# For MSSQL, foreign key checks are typically managed at the constraint level or per transaction.
# We will proceed assuming constraints are deferrable or will be handled by the order of operations.
# If specific FK handling is needed during bulk import, it's more complex than a simple session variable.

# existing tables (MSSQL version)
with engine.connect() as conn:
    # For MSSQL, information_schema.tables is standard
    result = conn.execute(text("SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = :db_name"), {'db_name': DB_NAME})
    existing_tables = [row[0] for row in result]
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
        print(f"WARN: Skipping {fname} (no table {table})")
        continue

    fpath = os.path.join(EXPORT_JSON, fname)
    if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
        print(f"WARN: Skipping missing/empty {fname}")
        continue

    print(f"Importing {fname} -> {table}")
    data = json.load(open(fpath, encoding='utf-8'))
    df   = pd.DataFrame(data if isinstance(data, list) else [data])
    if df.empty:
        continue

    # keep only real columns (MSSQL version)
    with engine.connect() as conn:
        # For MSSQL, information_schema.columns provides column info
        result = conn.execute(text(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{table}' AND TABLE_CATALOG = '{DB_NAME}'"))
        cols = [row[0] for row in result]
    df_cols_in_db = [c for c in df.columns if c in cols]
    if not df_cols_in_db:
        print(f"WARN: No matching columns found for table {table} in DataFrame from {fname}. Skipping.")
        continue
    df   = df[df_cols_in_db]

    # drop already-present IDs for general tables
    if table != 'user_achievements' and 'id' in df.columns and table in existing_tables:
        try:
            with engine.connect() as conn:
                existing_ids_result = conn.execute(text(f"SELECT id FROM [{table}]")) # Use square brackets for table names in MSSQL
                existing_ids = {r[0] for r in existing_ids_result}
            df = df[~df['id'].isin(existing_ids)]
            if df.empty:
                print(f"INFO: All entries in {fname} for table {table} already exist based on ID. Skipping.")
                continue
        except Exception as e:
            print(f"WARN: Could not check existing IDs for table {table}, proceeding with insert. Error: {e}")

    # Specifically handle unique constraints for user_achievements
    if table == 'user_achievements' and not df.empty and table in existing_tables:
        # 1. Handle Primary Key 'id' constraint
        if 'id' in df.columns:
            try:
                with engine.connect() as conn:
                    existing_ids_result = conn.execute(text("SELECT id FROM user_achievements"))
                    existing_ids = {row[0] for row in existing_ids_result}

                original_row_count = len(df)
                df = df[~df['id'].isin(existing_ids)]
                if len(df) < original_row_count:
                    print(f"INFO: Filtered out {original_row_count - len(df)} rows from {fname} for user_achievements due to duplicate IDs.")

                if df.empty:
                    print(f"INFO: All user_achievements entries in {fname} had duplicate IDs. Skipping.")
                    continue
            except Exception as e:
                print(f"WARN: Could not check existing IDs for user_achievements, proceeding. Error: {e}")

        # 2. Handle Unique Key (user_id, achievement_id) constraint
        if not df.empty and all(col in df.columns for col in ['user_id', 'achievement_id']):
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT user_id, achievement_id FROM user_achievements"))
                    existing_user_achievements = {tuple(row) for row in result}

                original_row_count = len(df)
                df_copy = df.copy()
                df_copy['user_id'] = df_copy['user_id'].astype(int)
                df_copy['achievement_id'] = df_copy['achievement_id'].astype(int)
                df_copy['_temp_tuple'] = df_copy.apply(lambda row: (row['user_id'], row['achievement_id']), axis=1)

                df = df[~df_copy['_temp_tuple'].isin(existing_user_achievements)]

                if len(df) < original_row_count:
                     print(f"INFO: Filtered out {original_row_count - len(df)} rows from {fname} for user_achievements due to duplicate (user_id, achievement_id) pairs.")

                if df.empty:
                    print(f"INFO: All remaining user_achievements entries in {fname} had duplicate (user_id, achievement_id) pairs. Skipping.")
                    continue
            except Exception as e:
                print(f"WARN: Could not check unique (user_id, achievement_id) for user_achievements, proceeding. Error: {e}")

    if df.empty: # Final check if DataFrame became empty after all filtering for any table
        print(f"INFO: No new data to insert for {table} from {fname} after filtering. Skipping.")
        continue

    # For MSSQL, ensure table names with spaces or special characters are quoted if necessary,
    # though pandas to_sql usually handles this. Using schema might be needed for some setups.
    # Example: df.to_sql(table, engine, schema='dbo', index=False, if_exists='append', ...)

    # Define tables that have an identity 'id' column and might receive explicit ID values from JSON
    # Add other table names to this list if they also have an identity 'id' column
    # and you intend to insert explicit values for it.
    tables_that_need_identity_insert = ['users', 'customeraddresses', 'restaurants',
                                        'listings', 'purchases', 'refund_records',
                                        'restaurant_comments', 'comment_badges',
                                        'restaurant_punishments', 'achievements',
                                        'environmental_contributions', 'user_favorites',
                                        'user_cart', 'user_devices', 'discountearned',
                                        'restaurant_badge_points'] # Added most tables that have 'id'
                                                                  # and are not 'user_achievements'
                                                                  # Review this list based on actual schema.

    identity_insert_was_set_on = False
    with engine.connect() as conn:  # Use a single connection for all operations for this table
        try:
            # Check if IDENTITY_INSERT needs to be managed for this table
            if table in tables_that_need_identity_insert and 'id' in df.columns:
                conn.execute(text(f"SET IDENTITY_INSERT [{table}] ON"))
                # No commit here, part of the larger transaction
                identity_insert_was_set_on = True

            # Perform the data insertion
            df.to_sql(
                name=table,
                con=conn,  # Pass the connection object, not the engine
                index=False,
                if_exists='append',
                dtype={c: SQLDateTime() for c in df.columns if 'date' in c.lower() or 'time' in c.lower()}
            )

            # If all successful so far, commit the transaction
            conn.commit()
            print(f"OK: {len(df)} rows added to {table}")

        except Exception as e:
            print(f"ERROR: During import for table {table} from {fname}: {e}")
            try:
                conn.rollback() # Rollback on any error during SET ON or to_sql
                print(f"INFO: Transaction rolled back for table {table}.")
            except Exception as er:
                print(f"ERROR: During rollback for table {table}: {er}")
        finally:
            # Always attempt to turn IDENTITY_INSERT OFF if it was turned ON for this connection
            if identity_insert_was_set_on:
                print(f"DEBUG: In finally, for table {table}, identity_insert_was_set_on is True. Attempting to set IDENTITY_INSERT OFF.") # ADDED DEBUG
                try:
                    # This command will execute on the same connection `conn`.
                    # If the previous transaction was committed or rolled back,
                    # this will execute in a new context on the same connection.
                    conn.execute(text(f"SET IDENTITY_INSERT [{table}] OFF"))
                    conn.commit() # Ensure this SET OFF is also committed.
                    print(f"INFO: IDENTITY_INSERT set to OFF for table {table}.")
                except Exception as e_off:
                    print(f"WARN: Failed to SET IDENTITY_INSERT OFF for table {table} in finally. Error: {e_off}")
        # Connection `conn` is automatically closed here when exiting the `with` block.

# Re-enabling FK checks is not a direct command in MSSQL like in MySQL.
# Constraints are either enabled or disabled. If they were disabled, they'd need to be re-enabled individually.
# Assuming they remained enabled throughout.

print("\nSUCCESS: All sample-data JSON generated and imported successfully.")
