import os
import json
import pandas as pd
from sqlalchemy import create_engine, text, DateTime as SQLDateTime
from dotenv import load_dotenv

load_dotenv()
MYSQL_URI = os.getenv("MYSQL_URI")
if not MYSQL_URI:
    raise SystemExit("❌ Missing MYSQL_URI in .env")

engine = create_engine(MYSQL_URI)
json_dir = "exported_json"

# disable foreign key checks during import
txt_fk_off = text("SET FOREIGN_KEY_CHECKS=0;")
txt_fk_on = text("SET FOREIGN_KEY_CHECKS=1;")

# Get list of existing tables in the database
with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES;"))
    existing_tables = [row[0] for row in result]
    print(f"Existing tables: {existing_tables}")

# disable FK checks for import
with engine.begin() as conn:
    conn.execute(txt_fk_off)

# Map file names to table names if they differ
table_name_mapping = {
    "customeraddresses.json": "customeraddresses",
    "discountearned.json": "discountearned",
    "user_cart.json": "user_cart"
}

# Files to import, only including those matching existing tables
ordered_files = [
    "users.json",
    "customeraddresses.json",
    "restaurants.json",
    "restaurant_badge_points.json",
    "listings.json",
    "purchases.json",
    "restaurant_comments.json",
    "comment_badges.json",
    "achievements.json",
    "user_achievements.json",
    "environmental_contributions.json",
    "user_favorites.json",
    "user_devices.json",
    "restaurant_punishments.json",
    "refund_records.json",
    "user_cart.json",
    "discountearned.json"
]


# Table-specific processing functions
def process_achievements(df):
    # Get the actual enum values from the database
    with engine.connect() as conn:
        result = conn.execute(text("SHOW COLUMNS FROM achievements LIKE 'achievement_type'"))
        enum_info = result.fetchone()
        if enum_info:
            # Extract enum values from the column definition
            enum_def = enum_info[1]
            enum_values = enum_def.split("'")[1::2]  # Extract values between quotes
            print(f"Valid achievement_type values: {enum_values}")

            # Map our values to valid enum values
            mapping = {
                'FIRST_PURCHASE': 'FIRST_PURCHASE',
                'PURCHASE_COUNT': 'PURCHASE_COUNT',
                'WEEKLY_PURCHASE': 'WEEKLY_PURCHASE',
                'REGULAR_COMMENTER': 'COMMENTER',  # Map to the closest existing value
                'CO2_SAVED': 'ENVIRONMENTAL',  # Map to the closest existing value
                'FLASH_DEALS': 'PURCHASE_COUNT',  # Map to general purchase count
                'CUISINE_VARIETY': 'EXPLORER'  # Map to the closest existing value
            }

            # Apply mapping to achievement_type column
            df['achievement_type'] = df['achievement_type'].map(
                lambda x: mapping.get(x, enum_values[0] if enum_values else x)
            )
    return df


def process_restaurant_punishments(df):
    # Check required columns
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE restaurant_punishments"))
        columns = {row[0]: row for row in result}

        # Add missing required columns with default values
        if 'punishment_type' in columns and 'punishment_type' not in df.columns:
            df['punishment_type'] = 'OTHER'  # Default punishment type

        if 'duration_days' in columns and 'duration_days' not in df.columns:
            # Calculate duration from start and end dates
            if 'start_date' in df.columns and 'end_date' in df.columns:
                # Convert to datetime, calculate difference in days, and get integer value
                df['duration_days'] = pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])
                df['duration_days'] = df['duration_days'].dt.total_seconds() / (24 * 3600)
                df['duration_days'] = df['duration_days'].astype(int)
            else:
                df['duration_days'] = 1  # Default duration

        if 'created_by' in columns and 'created_by' not in df.columns:
            df['created_by'] = 1  # Default admin user

        if 'created_at' in columns and 'created_at' not in df.columns:
            df['created_at'] = pd.Timestamp.now()

    return df


def process_refund_records(df):
    # Add required columns with default values
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE refund_records"))
        columns = {row[0]: row for row in result}

        if 'restaurant_id' in columns and 'restaurant_id' not in df.columns:
            # Get the restaurant_id from the purchase
            if 'purchase_id' in df.columns:
                # For each refund, look up the purchase and get its restaurant_id
                purchase_ids = df['purchase_id'].tolist()
                if purchase_ids:
                    purchases_data = pd.read_sql(
                        text(
                            f"SELECT id, restaurant_id FROM purchases WHERE id IN ({','.join(map(str, purchase_ids))})"),
                        engine
                    )
                    # Create a mapping of purchase_id to restaurant_id
                    purchase_to_restaurant = dict(zip(purchases_data['id'], purchases_data['restaurant_id']))
                    df['restaurant_id'] = df['purchase_id'].map(lambda x: purchase_to_restaurant.get(x, 1))
                else:
                    df['restaurant_id'] = 1  # Default restaurant
            else:
                df['restaurant_id'] = 1  # Default restaurant

        if 'user_id' in columns and 'user_id' not in df.columns:
            df['user_id'] = 11  # Default customer user

        if 'order_id' in columns and 'order_id' not in df.columns:
            # If purchase_id exists, use that, otherwise default
            if 'purchase_id' in df.columns:
                df['order_id'] = df['purchase_id']
            else:
                df['order_id'] = None

        if 'processed' in columns and 'processed' not in df.columns:
            df['processed'] = True

        if 'created_by' in columns and 'created_by' not in df.columns:
            df['created_by'] = 1

        if 'created_at' in columns and 'created_at' not in df.columns:
            if 'processed_at' in df.columns:
                df['created_at'] = df['processed_at']
            else:
                df['created_at'] = pd.Timestamp.now()

    return df


# Table-specific processors
table_processors = {
    'achievements': process_achievements,
    'restaurant_punishments': process_restaurant_punishments,
    'refund_records': process_refund_records
}

# Process each file in order, but only if the corresponding table exists
for file in ordered_files:
    # Determine the table name from the file name
    base_name = file.rsplit('.', 1)[0]
    table_name = table_name_mapping.get(file, base_name)

    # Skip if table doesn't exist
    if table_name not in existing_tables:
        print(f"\n⚠️ Skipping {file} - Table {table_name} does not exist.")
        continue

    path = os.path.join(json_dir, file)
    print(f"\n📥 Importing {file} → {table_name}")

    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        print(f"⚠️ Skipped {file} — missing or empty.")
        continue

    try:
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Handle both array of objects and single objects
        if isinstance(json_data, dict):
            df = pd.DataFrame([json_data])
        else:
            df = pd.DataFrame(json_data)

        if df.empty:
            print(f"⚠️ Skipped {file} — no data.")
            continue

        # Get column names of the table
        with engine.connect() as conn:
            result = conn.execute(text(f"DESCRIBE `{table_name}`;"))
            table_columns = [row[0] for row in result]
            required_columns = [row[0] for row in result if row[2] == 'NO' and row[5] != 'auto_increment']
            print(f"Table columns: {table_columns}")
            print(f"Required columns: {required_columns}")

        # Apply table-specific processing if defined
        if table_name in table_processors:
            df = table_processors[table_name](df)

        # Filter dataframe to include only columns that exist in the table
        df_columns = set(df.columns)
        valid_columns = [col for col in df.columns if col in table_columns]

        if len(valid_columns) < len(df_columns):
            missing_columns = df_columns - set(table_columns)
            print(f"⚠️ Skipping non-existent columns: {missing_columns}")

        df = df[valid_columns]

        # Ensure all required columns have values
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            print(f"⚠️ Missing required columns: {missing_required}")
            continue

        # Check for existing IDs to avoid duplicates
        if 'id' in df.columns:
            with engine.connect() as conn:
                # Get existing IDs
                existing_ids_result = conn.execute(text(f"SELECT id FROM `{table_name}`"))
                existing_ids = {row[0] for row in existing_ids_result}

                # Filter out rows with IDs that already exist
                new_rows = df[~df['id'].isin(existing_ids)]

                if len(new_rows) < len(df):
                    print(f"⚠️ Skipping {len(df) - len(new_rows)} rows with existing IDs")

                df = new_rows

                if df.empty:
                    print(f"⚠️ All rows already exist in table. Nothing to import.")
                    continue

        # Set up dtype overrides for timestamp columns
        datetime_columns = [col for col in df.columns if
                            'date' in col.lower() or 'time' in col.lower() or col == 'timestamp']
        dtype_overrides = {col: SQLDateTime() for col in datetime_columns if col in df.columns}

        # Import data
        df.to_sql(
            table_name,
            con=engine,
            index=False,
            if_exists="append",  # Append to existing data
            dtype=dtype_overrides
        )
        print(f"✅ Imported {table_name} ({len(df)} rows)")

    except json.JSONDecodeError:
        print(f"❌ Error: {file} is not valid JSON.")
    except Exception as e:
        print(f"❌ Error importing {file}: {str(e)}")

# re-enable foreign key checks
with engine.begin() as conn:
    conn.execute(txt_fk_on)

print("\n🎉 JSON data appended to existing tables successfully.")