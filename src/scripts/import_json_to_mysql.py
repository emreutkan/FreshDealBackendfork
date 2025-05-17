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
json_dir = "../../src/exported_json"  # Adjust the path as needed

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
    "user_cart.json": "user_cart",
    "purchase_reports.json": "purchase_reports"  # Add mapping for purchase reports
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
    "discountearned.json",
    "purchase_reports.json"  # Add purchase reports to files to import
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

        # Print columns to debug
        print(f"Restaurant Punishments Table Columns: {list(columns.keys())}")

        # Check if the new columns exist in the DB schema
        has_is_active = 'is_active' in columns
        has_is_reverted = 'is_reverted' in columns
        has_reverted_by = 'reverted_by' in columns
        has_reverted_at = 'reverted_at' in columns
        has_reversion_reason = 'reversion_reason' in columns

        print(f"is_active column exists: {has_is_active}")
        print(f"is_reverted column exists: {has_is_reverted}")

        # Add missing columns if they exist in the table but not in our data
        if 'punishment_type' in columns and 'punishment_type' not in df.columns:
            df['punishment_type'] = 'TEMPORARY'  # Default punishment type

        if 'duration_days' in columns and 'duration_days' not in df.columns:
            # Calculate duration from start and end dates
            if 'start_date' in df.columns and 'end_date' in df.columns:
                # Convert to datetime, calculate difference in days, and get integer value
                df['duration_days'] = pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])
                df['duration_days'] = df['duration_days'].dt.total_seconds() / (24 * 3600)
                df['duration_days'] = df['duration_days'].astype(int)
            else:
                df['duration_days'] = 7  # Default duration

        if 'created_by' in columns and 'created_by' not in df.columns:
            df['created_by'] = 31  # Default support team user

        if 'created_at' in columns and 'created_at' not in df.columns:
            df['created_at'] = df['start_date'] if 'start_date' in df.columns else pd.Timestamp.now()

        # Handle the new columns if they exist in the schema
        if has_is_active and 'is_active' not in df.columns:
            # Check if there's an 'active' column we can use
            if 'active' in df.columns:
                df['is_active'] = df['active']
            else:
                # Default to active if end_date is in the future
                df['is_active'] = True

        if has_is_reverted and 'is_reverted' not in df.columns:
            df['is_reverted'] = False  # Default to not reverted

        if has_reverted_by and 'reverted_by' not in df.columns:
            df['reverted_by'] = None  # No one reverted it

        if has_reverted_at and 'reverted_at' not in df.columns:
            df['reverted_at'] = None  # No reversion time

        if has_reversion_reason and 'reversion_reason' not in df.columns:
            df['reversion_reason'] = None  # No reversion reason

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
            df['created_by'] = 31  # Default support team user

        if 'created_at' in columns and 'created_at' not in df.columns:
            if 'processed_at' in df.columns:
                df['created_at'] = df['processed_at']
            else:
                df['created_at'] = pd.Timestamp.now()

    return df


def process_purchase_reports(df):
    # Add required columns with default values
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE purchase_reports"))
        columns = {row[0]: row for row in result}

        print(f"Purchase Reports Table Columns: {list(columns.keys())}")

        # Check if status column exists in the DB schema
        has_status = 'status' in columns
        print(f"status column exists: {has_status}")

        if has_status and 'status' in df.columns:
            # Check the type of the status column
            status_column_info = columns['status']
            column_type = status_column_info[1]

            print(f"Status column type: {column_type}")

            # If it's an ENUM, extract the allowed values
            if 'enum' in column_type.lower():
                enum_values = column_type.split("'")[1::2]  # Extract values between quotes
                print(f"Valid status values: {enum_values}")

                # Make sure our values match the enum values
                if set(df['status'].unique()) != set(enum_values):
                    # Map our values to the enum values if possible
                    if 'active' in enum_values and 'resolved' in enum_values and 'inactive' in enum_values:
                        df['status'] = df['status'].apply(lambda x: x.upper() if x in enum_values else 'ACTIVE')
                    else:
                        # If our values don't match and we can't find a mapping, set a default
                        df['status'] = enum_values[0] if enum_values else 'ACTIVE'

        # Add other required fields with defaults if missing
        if 'resolved_at' in columns and 'resolved_at' not in df.columns and 'status' in df.columns:
            # Set resolved_at based on status
            df['resolved_at'] = None
            if 'status' in df.columns:
                resolved_mask = df['status'].isin(['resolved', 'RESOLVED', 'inactive', 'INACTIVE'])
                if resolved_mask.any():
                    # For resolved reports, set a resolved time if missing
                    df.loc[resolved_mask, 'resolved_at'] = pd.Timestamp.now()

        if 'resolved_by' in columns and 'resolved_by' not in df.columns and 'status' in df.columns:
            # Set resolved_by based on status
            df['resolved_by'] = None
            if 'status' in df.columns:
                resolved_mask = df['status'].isin(['resolved', 'RESOLVED', 'inactive', 'INACTIVE'])
                if resolved_mask.any():
                    # For resolved reports, set a resolver if missing
                    df.loc[resolved_mask, 'resolved_by'] = 31  # Default support user

        if 'punishment_id' in columns and 'punishment_id' not in df.columns:
            df['punishment_id'] = None  # No punishment by default

    return df


# Table-specific processors
table_processors = {
    'achievements': process_achievements,
    'restaurant_punishments': process_restaurant_punishments,
    'refund_records': process_refund_records,
    'purchase_reports': process_purchase_reports
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