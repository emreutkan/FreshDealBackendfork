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
    "purchase_reports.json": "purchase_reports"
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
    "purchase_reports.json"
]


def process_achievements(df):
    with engine.connect() as conn:
        result = conn.execute(text("SHOW COLUMNS FROM achievements LIKE 'achievement_type'"))
        enum_info = result.fetchone()
        if enum_info:
            enum_values = enum_info[1].split("'")[1::2]
            print(f"Valid achievement_type values: {enum_values}")
            mapping = {
                'FIRST_PURCHASE': 'FIRST_PURCHASE',
                'PURCHASE_COUNT': 'PURCHASE_COUNT',
                'WEEKLY_PURCHASE': 'WEEKLY_PURCHASE',
                'REGULAR_COMMENTER': 'COMMENTER',
                'CO2_SAVED': 'ENVIRONMENTAL',
                'FLASH_DEALS': 'PURCHASE_COUNT',
                'CUISINE_VARIETY': 'EXPLORER'
            }
            df['achievement_type'] = df['achievement_type'].map(
                lambda x: mapping.get(x, enum_values[0])
            )
    return df


def process_restaurant_punishments(df):
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE restaurant_punishments"))
        cols = {row[0]: row for row in result}
        print(f"Restaurant Punishments Table Columns: {list(cols.keys())}")
        if 'punishment_type' in cols and 'punishment_type' not in df:
            df['punishment_type'] = 'TEMPORARY'
        if 'duration_days' in cols and 'duration_days' not in df:
            if 'start_date' in df and 'end_date' in df:
                df['duration_days'] = (
                    pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])
                ).dt.total_seconds() / 86400
                df['duration_days'] = df['duration_days'].astype(int)
            else:
                df['duration_days'] = 7
        if 'created_by' in cols and 'created_by' not in df:
            df['created_by'] = 31
        if 'created_at' in cols and 'created_at' not in df:
            df['created_at'] = df.get('start_date', pd.Timestamp.now())
        if 'is_active' in cols and 'is_active' not in df:
            df['is_active'] = True
        if 'is_reverted' in cols and 'is_reverted' not in df:
            df['is_reverted'] = False
        if 'reverted_by' in cols and 'reverted_by' not in df:
            df['reverted_by'] = None
        if 'reverted_at' in cols and 'reverted_at' not in df:
            df['reverted_at'] = None
        if 'reversion_reason' in cols and 'reversion_reason' not in df:
            df['reversion_reason'] = None
    return df


def process_refund_records(df):
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE refund_records"))
        cols = {row[0]: row for row in result}
        if 'restaurant_id' in cols and 'restaurant_id' not in df:
            if 'purchase_id' in df:
                pids = df['purchase_id'].tolist()
                if pids:
                    purchases = pd.read_sql(
                        text(f"SELECT id, restaurant_id FROM purchases WHERE id IN ({','.join(map(str,pids))})"),
                        engine
                    )
                    mapping = dict(zip(purchases.id, purchases.restaurant_id))
                    df['restaurant_id'] = df['purchase_id'].map(mapping).fillna(1).astype(int)
                else:
                    df['restaurant_id'] = 1
            else:
                df['restaurant_id'] = 1
        if 'user_id' in cols and 'user_id' not in df:
            df['user_id'] = 11
        if 'order_id' in cols and 'order_id' not in df:
            df['order_id'] = df.get('purchase_id')
        if 'processed' in cols and 'processed' not in df:
            df['processed'] = True
        if 'created_by' in cols and 'created_by' not in df:
            df['created_by'] = 31
        if 'created_at' in cols and 'created_at' not in df:
            df['created_at'] = df.get('processed_at', pd.Timestamp.now())
    return df


def process_purchase_reports(df):
    with engine.connect() as conn:
        result = conn.execute(text("DESCRIBE purchase_reports"))
        cols = {row[0]: row for row in result}
        print(f"Purchase Reports Table Columns: {list(cols.keys())}")
        if 'status' in cols and 'status' in df:
            column_type = cols['status'][1]
            if 'enum' in column_type.lower():
                enum_vals = column_type.split("'")[1::2]
                df['status'] = df['status'].str.upper().where(df['status'].str.upper().isin(enum_vals), enum_vals[0])
        if 'resolved_at' in cols and 'resolved_at' not in df:
            df['resolved_at'] = df['status'].isin(['RESOLVED','INACTIVE']).map(lambda v: pd.Timestamp.now() if v else None)
        if 'resolved_by' in cols and 'resolved_by' not in df:
            df['resolved_by'] = df['status'].isin(['RESOLVED','INACTIVE']).map(lambda v: 31 if v else None)
        if 'punishment_id' in cols and 'punishment_id' not in df:
            df['punishment_id'] = None
    return df


def process_purchases(df):
    with engine.connect() as conn:
        enum_def = conn.execute(text("SHOW COLUMNS FROM purchases LIKE 'status'")).fetchone()[1]
        valid = enum_def.split("'")[1::2]
        print(f"Valid purchase status values: {valid}")
    df['status'] = df['status'].where(df['status'].isin(valid), 'PENDING')
    return df


def process_user_achievements(df):
    before = len(df)
    df = df[df['earned_at'].notnull()]
    dropped = before - len(df)
    if dropped:
        print(f"⚠️ Dropped {dropped} rows with null earned_at")
    return df


table_processors = {
    'achievements': process_achievements,
    'restaurant_punishments': process_restaurant_punishments,
    'refund_records': process_refund_records,
    'purchase_reports': process_purchase_reports,
    'purchases': process_purchases,
    'user_achievements': process_user_achievements
}

for file in ordered_files:
    base = file.rsplit('.',1)[0]
    table = table_name_mapping.get(file, base)
    if table not in existing_tables:
        print(f"\n⚠️ Skipping {file} - Table {table} does not exist.")
        continue

    path = os.path.join(json_dir, file)
    print(f"\n📥 Importing {file} → {table}")
    if not os.path.isfile(path) or os.path.getsize(path)==0:
        print(f"⚠️ Skipped {file} — missing or empty.")
        continue

    try:
        data = json.load(open(path, encoding='utf-8'))
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
        if df.empty:
            print(f"⚠️ Skipped {file} — no data.")
            continue

        with engine.connect() as conn:
            desc = conn.execute(text(f"DESCRIBE `{table}`")).fetchall()
            cols = [r[0] for r in desc]
            req = [r[0] for r in desc if r[2]=='NO' and r[5]!='auto_increment']
            print(f"Table columns: {cols}")
            print(f"Required columns: {req}")

        if table in table_processors:
            df = table_processors[table](df)

        valid_cols = [c for c in df.columns if c in cols]
        missing = set(df.columns) - set(valid_cols)
        if missing:
            print(f"⚠️ Skipping non-existent columns: {missing}")
        df = df[valid_cols]

        miss_req = [c for c in req if c not in df.columns]
        if miss_req:
            print(f"⚠️ Missing required columns: {miss_req}")
            continue

        if 'id' in df:
            with engine.connect() as conn:
                existing = {r[0] for r in conn.execute(text(f"SELECT id FROM `{table}`"))}
            new = df[~df['id'].isin(existing)]
            skipped = len(df)-len(new)
            if skipped:
                print(f"⚠️ Skipping {skipped} rows with existing IDs")
            df = new
            if df.empty:
                print(f"⚠️ All rows already exist. Nothing to import.")
                continue

        dtypes = {c: SQLDateTime() for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or c=='timestamp'}
        df.to_sql(table, engine, index=False, if_exists="append", dtype=dtypes)
        print(f"✅ Imported {table} ({len(df)} rows)")

    except json.JSONDecodeError:
        print(f"❌ Error: {file} is not valid JSON.")
    except Exception as e:
        print(f"❌ Error importing {file}: {e}")

with engine.begin() as conn:
    conn.execute(txt_fk_on)

print("\n🎉 JSON data appended to existing tables successfully.")
