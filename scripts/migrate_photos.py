import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pos.db")

def migrate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Ensure areas table exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        area_type TEXT DEFAULT 'Offline',
        status TEXT DEFAULT 'Active'
    )
    ''')

    # Seed 3 areas matching Photo 5
    cursor.execute("DELETE FROM areas")
    areas_data = [
        ("Party Hut", "Offline", "Active"),
        ("Family Hut", "Offline", "Active"),
        ("Home Delivery", "Online", "Inactive")
    ]
    cursor.executemany("INSERT INTO areas (name, area_type, status) VALUES (?, ?, ?)", areas_data)

    # 2. Add extra columns to dining_tables if not exist
    table_cols = [r[1] for r in cursor.execute("PRAGMA table_info(dining_tables)").fetchall()]
    if "color_status" not in table_cols:
        cursor.execute("ALTER TABLE dining_tables ADD COLUMN color_status TEXT DEFAULT 'blank'")
    if "elapsed_minutes" not in table_cols:
        cursor.execute("ALTER TABLE dining_tables ADD COLUMN elapsed_minutes INTEGER DEFAULT 0")

    # 3. Seed exact tables matching Photo 2 and Photo 5
    # Family Hut: 1, 2, 3A, 3B, 3C, 3D, 4, 5
    # Party Hut: 11, 12A, 12B, 12C, 12D, 13, 14
    cursor.execute("DELETE FROM dining_tables")
    tables_data = [
        # Family Hut
        ("1", "Family Hut", 4, "occupied", "running_kot", 26),
        ("2", "Family Hut", 4, "available", "blank", 0),
        ("3A", "Family Hut", 4, "available", "blank", 0),
        ("3B", "Family Hut", 4, "available", "blank", 0),
        ("3C", "Family Hut", 4, "available", "blank", 0),
        ("3D", "Family Hut", 4, "available", "blank", 0),
        ("4", "Family Hut", 4, "billed", "printed", 73),
        ("5", "Family Hut", 4, "available", "blank", 0),
        # Party Hut
        ("11", "Party Hut", 6, "billed", "printed", 53),
        ("12A", "Party Hut", 4, "available", "blank", 0),
        ("12B", "Party Hut", 4, "available", "blank", 0),
        ("12C", "Party Hut", 4, "available", "blank", 0),
        ("12D", "Party Hut", 4, "available", "blank", 0),
        ("13", "Party Hut", 4, "available", "blank", 0),
        ("14", "Party Hut", 4, "available", "blank", 0),
    ]
    cursor.executemany("""
        INSERT INTO dining_tables (name, section, capacity, status, color_status, elapsed_minutes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tables_data)

    # 4. Update staff columns & seed exact 12 profiles from Photo 1
    staff_cols = [r[1] for r in cursor.execute("PRAGMA table_info(staff)").fetchall()]
    if "original_name" not in staff_cols:
        cursor.execute("ALTER TABLE staff ADD COLUMN original_name TEXT")
    if "user_type" not in staff_cols:
        cursor.execute("ALTER TABLE staff ADD COLUMN user_type TEXT DEFAULT 'Captain'")

    cursor.execute("DELETE FROM staff")
    staff_profiles = [
        ("biller", "biller", "Biller", "1111"),
        ("prabhu", "prabhu", "Captain", "1234"),
        ("shanmugapriya", "shanmugapriya", "Captain", "1234"),
        ("saravanan", "saravanan", "Captain", "1234"),
        ("sarathi", "sarathi", "Captain", "1234"),
        ("sab", "Sabarish", "Captain", "1234"),
        ("SARVAJIT", "SARVAJIT", "Captain", "1234"),
        ("saiswethan", "SAI", "Captain", "1234"),
        ("jeeva", "JEEVA", "Captain", "1234"),
        ("mukesh", "MUKESH", "Captain", "1234"),
        ("VIJAY", "VIJAY", "Captain", "1234"),
        ("KARTHI", "KARTHI", "Captain", "1234")
    ]
    cursor.executemany("""
        INSERT INTO staff (name, original_name, user_type, pin)
        VALUES (?, ?, ?, ?)
    """, staff_profiles)

    # 5. Add columns to menu_items if not present
    item_cols = [r[1] for r in cursor.execute("PRAGMA table_info(menu_items)").fetchall()]
    if "short_code" not in item_cols:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN short_code TEXT")
    if "is_favorite" not in item_cols:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN is_favorite INTEGER DEFAULT 0")
    if "stock_status" not in item_cols:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN stock_status TEXT DEFAULT 'Do Not Track'")

    # 6. Categories matching Photo 4:
    # other, Veg Rice & Noodles, Prawn Specials, Veg Gravy, rotti, Starters, Beverages, Desserts
    cursor.execute("DELETE FROM categories")
    cats = [
        ("other", "📦"),
        ("Veg Rice & Noodles", "🍜"),
        ("Prawn Specials", "🦐"),
        ("Veg Gravy", "🍲"),
        ("rotti", "🫓"),
        ("Starters", "🍢"),
        ("Main Course", "🍛"),
        ("Beverages", "🥤"),
        ("Desserts", "🍨")
    ]
    cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", cats)
    cat_map = {row[1]: row[0] for row in cursor.execute("SELECT id, name FROM categories").fetchall()}

    # 7. Seed items matching Photo 4
    cursor.execute("DELETE FROM menu_items")
    items_photo4 = [
        (cat_map["other"], "Curd", 35.00, "veg", "curd", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Schezwan Musroom Rice", 130.00, "veg", "SCH", 0, "Do Not Track"),
        (cat_map["Prawn Specials"], "Kerala Prawn", 280.00, "non-veg", "kp5", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Schezwan Veg Rice", 120.00, "veg", "SVR", 0, "Do Not Track"),
        (cat_map["Veg Gravy"], "Maharani Musroom", 200.00, "veg", "MAHA MUS", 0, "Do Not Track"),
        (cat_map["Veg Gravy"], "Maharani Gobi", 200.00, "veg", "MAHA GOBI", 0, "Do Not Track"),
        (cat_map["Veg Gravy"], "Maharani Paneer", 200.00, "veg", "MAHA PAN", 0, "Do Not Track"),
        (cat_map["rotti"], "Pulika Rotti", 25.00, "veg", "rotti 1", 0, "Do Not Track"),
        (cat_map["other"], "Connect", 30.00, "veg", "cig con", 0, "Do Not Track"),
        # Additional popular authentic items to populate the catalog
        (cat_map["Veg Gravy"], "Paneer Butter Masala", 240.00, "veg", "PBM", 1, "Do Not Track"),
        (cat_map["Veg Gravy"], "Kadai Paneer", 230.00, "veg", "KP", 0, "Do Not Track"),
        (cat_map["Veg Gravy"], "Dal Makhani", 190.00, "veg", "DM", 0, "Do Not Track"),
        (cat_map["Veg Gravy"], "Mushroom Masala", 210.00, "veg", "MM", 0, "Do Not Track"),
        (cat_map["rotti"], "Butter Naan", 55.00, "veg", "BN", 1, "Do Not Track"),
        (cat_map["rotti"], "Garlic Naan", 70.00, "veg", "GN", 0, "Do Not Track"),
        (cat_map["rotti"], "Tandoori Roti", 25.00, "veg", "TR", 0, "Do Not Track"),
        (cat_map["rotti"], "Kulcha", 45.00, "veg", "KC", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Veg Fried Rice", 110.00, "veg", "VFR", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Veg Hakka Noodles", 115.00, "veg", "VHN", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Jeera Rice", 120.00, "veg", "JR", 0, "Do Not Track"),
        (cat_map["Veg Rice & Noodles"], "Veg Biryani", 160.00, "veg", "VB", 0, "Do Not Track"),
        (cat_map["Starters"], "Paneer Tikka", 220.00, "veg", "PT", 1, "Do Not Track"),
        (cat_map["Starters"], "Gobi Manchurian", 140.00, "veg", "GM", 0, "Do Not Track"),
        (cat_map["Starters"], "Crispy Corn", 150.00, "veg", "CC", 0, "Do Not Track"),
        (cat_map["Starters"], "Mushroom Pepper Fry", 180.00, "veg", "MPF", 0, "Do Not Track"),
        (cat_map["Prawn Specials"], "Prawn Pepper Fry", 290.00, "non-veg", "PPF", 0, "Do Not Track"),
        (cat_map["Prawn Specials"], "Prawn Biryani", 320.00, "non-veg", "PB", 0, "Do Not Track"),
        (cat_map["Beverages"], "Fresh Lime Soda", 60.00, "veg", "FLS", 0, "Do Not Track"),
        (cat_map["Beverages"], "Sweet Lassi", 80.00, "veg", "SL", 0, "Do Not Track"),
        (cat_map["Beverages"], "Cold Drink 500ml", 40.00, "veg", "CD", 0, "Do Not Track"),
        (cat_map["Desserts"], "Gulab Jamun (2 Pcs)", 70.00, "veg", "GJ", 0, "Do Not Track"),
        (cat_map["Desserts"], "Vanilla Ice Cream", 60.00, "veg", "VIC", 0, "Do Not Track"),
        (cat_map["Desserts"], "Sizzling Brownie", 150.00, "veg", "SB", 0, "Do Not Track")
    ]
    cursor.executemany("""
        INSERT INTO menu_items (category_id, name, price, food_type, short_code, is_favorite, stock_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, items_photo4)

    # 8. Create sample orders for Table 1 (₹ 735), Table 4 (₹ 530), Table 11 (₹ 610) and Parcel 6028 (₹ 330)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t1_time = (datetime.now() - timedelta(minutes=26)).strftime("%Y-%m-%d %H:%M:%S")
    t4_time = (datetime.now() - timedelta(minutes=73)).strftime("%Y-%m-%d %H:%M:%S")
    t11_time = (datetime.now() - timedelta(minutes=53)).strftime("%Y-%m-%d %H:%M:%S")

    # Table 1: Family Hut 1 - ₹ 735.00
    cursor.execute("""
        INSERT INTO orders (order_number, order_type, table_name, captain_name, status, created_at, subtotal, grand_total)
        VALUES ('ORD-F1-001', 'dine_in', '1', 'prabhu', 'active', ?, 700.0, 735.0)
    """, (t1_time,))
    ord1_id = cursor.lastrowid
    cursor.execute("UPDATE dining_tables SET current_order_id = ? WHERE name = '1'", (ord1_id,))
    cursor.execute("INSERT INTO kots (kot_number, order_id, table_name, captain_name, created_at, status) VALUES (1, ?, '1', 'prabhu', ?, 'active')", (ord1_id, t1_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Paneer Butter Masala', 240, 2, ?)", (ord1_id, t1_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Butter Naan', 55, 4, ?)", (ord1_id, t1_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Fresh Lime Soda', 60, 1, ?)", (ord1_id, t1_time))

    # Table 4: Family Hut 4 - ₹ 530.00
    cursor.execute("""
        INSERT INTO orders (order_number, order_type, table_name, captain_name, status, created_at, subtotal, grand_total)
        VALUES ('ORD-F4-002', 'dine_in', '4', 'saravanan', 'billed', ?, 504.76, 530.0)
    """, (t4_time,))
    ord4_id = cursor.lastrowid
    cursor.execute("UPDATE dining_tables SET current_order_id = ? WHERE name = '4'", (ord4_id,))
    cursor.execute("INSERT INTO kots (kot_number, order_id, table_name, captain_name, created_at, status) VALUES (2, ?, '4', 'saravanan', ?, 'completed')", (ord4_id, t4_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Schezwan Musroom Rice', 130, 2, ?)", (ord4_id, t4_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Maharani Gobi', 200, 1, ?)", (ord4_id, t4_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Pulika Rotti', 25, 2, ?)", (ord4_id, t4_time))

    # Table 11: Party Hut 11 - ₹ 610.00
    cursor.execute("""
        INSERT INTO orders (order_number, order_type, table_name, captain_name, status, created_at, subtotal, grand_total)
        VALUES ('ORD-P11-003', 'dine_in', '11', 'SARVAJIT', 'billed', ?, 580.95, 610.0)
    """, (t11_time,))
    ord11_id = cursor.lastrowid
    cursor.execute("UPDATE dining_tables SET current_order_id = ? WHERE name = '11'", (ord11_id,))
    cursor.execute("INSERT INTO kots (kot_number, order_id, table_name, captain_name, created_at, status) VALUES (3, ?, '11', 'SARVAJIT', ?, 'completed')", (ord11_id, t11_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Kerala Prawn', 280, 1, ?)", (ord11_id, t11_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Schezwan Veg Rice', 120, 2, ?)", (ord11_id, t11_time))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Pulika Rotti', 25, 2, ?)", (ord11_id, t11_time))

    # Parcel Order 6028 matching Photo 1 & 2 - ₹ 330.00
    cursor.execute("DELETE FROM orders WHERE order_number = '6028'")
    cursor.execute("""
        INSERT INTO orders (order_number, order_type, table_name, captain_name, status, created_at, subtotal, grand_total)
        VALUES ('6028', 'takeaway', 'PARCEL', 'biller', 'billed', ?, 314.28, 330.0)
    """, (now_str,))
    ord_parc_id = cursor.lastrowid
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Schezwan Musroom Rice', 130, 1, ?)", (ord_parc_id, now_str))
    cursor.execute("INSERT INTO order_items (order_id, item_name, price, quantity, created_at) VALUES (?, 'Maharani Paneer', 200, 1, ?)", (ord_parc_id, now_str))

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
