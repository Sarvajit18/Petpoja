import sqlite3
import os
import json
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pos.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tables table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dining_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        section TEXT DEFAULT 'Main Dining',
        capacity INTEGER DEFAULT 4,
        status TEXT DEFAULT 'available', -- 'available', 'occupied', 'billed'
        current_order_id INTEGER,
        captain_name TEXT
    )
    ''')

    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        icon TEXT DEFAULT '🍽️'
    )
    ''')

    # Menu items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        food_type TEXT DEFAULT 'veg', -- 'veg', 'non-veg', 'egg'
        is_available INTEGER DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')

    # Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        order_type TEXT DEFAULT 'dine_in', -- 'dine_in', 'takeaway', 'delivery'
        table_id INTEGER,
        table_name TEXT,
        captain_name TEXT DEFAULT 'Counter',
        customer_name TEXT,
        customer_phone TEXT,
        status TEXT DEFAULT 'active', -- 'active', 'billed', 'settled', 'cancelled'
        created_at TEXT NOT NULL,
        subtotal REAL DEFAULT 0.0,
        discount_percent REAL DEFAULT 0.0,
        discount_amount REAL DEFAULT 0.0,
        gst_percent REAL DEFAULT 5.0,
        gst_amount REAL DEFAULT 0.0,
        grand_total REAL DEFAULT 0.0,
        payment_mode TEXT, -- 'cash', 'upi', 'card', 'split'
        settled_at TEXT
    )
    ''')

    # Order items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        item_id INTEGER,
        item_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        notes TEXT DEFAULT '',
        kot_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    ''')

    # Kitchen Order Tickets (KOT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kot_number INTEGER NOT NULL,
        order_id INTEGER NOT NULL,
        table_name TEXT NOT NULL,
        captain_name TEXT DEFAULT 'Counter',
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'active', -- 'active', 'completed'
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    ''')

    # Staff / Captains
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'captain', -- 'admin', 'cashier', 'captain', 'kitchen'
        pin TEXT DEFAULT '1234'
    )
    ''')

    # Restaurant Settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    conn.commit()

    # Seed Default Settings if empty
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        default_settings = {
            "restaurant_name": "Royal Feast Multi-Cuisine",
            "tagline": "Taste That Lingers",
            "address": "12, Commercial Hub, Main Road",
            "phone": "+91 98765 43210",
            "gstin": "27AABCR1234F1Z1",
            "fssai": "11521000000000",
            "gst_percent": "5.0",
            "service_charge_percent": "0.0",
            "currency_symbol": "₹"
        }
        for k, v in default_settings.items():
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))
        conn.commit()

    # Seed Staff if empty
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        default_staff = [
            ("Counter / Cashier", "cashier", "1111"),
            ("Captain Ramesh", "captain", "1234"),
            ("Captain Priya", "captain", "1234"),
            ("Captain Amit", "captain", "1234"),
            ("Kitchen Display", "kitchen", "0000"),
            ("Admin Manager", "admin", "9999")
        ]
        cursor.executemany("INSERT INTO staff (name, role, pin) VALUES (?, ?, ?)", default_staff)
        conn.commit()

    # Seed Dining Tables if empty
    cursor.execute("SELECT COUNT(*) FROM dining_tables")
    if cursor.fetchone()[0] == 0:
        tables = [
            # Dining Area
            ("T-1", "Dining Area", 2),
            ("T-2", "Dining Area", 4),
            ("T-3", "Dining Area", 4),
            ("T-4", "Dining Area", 6),
            # First Floor Family Section
            ("FF-1", "Family Floor", 4),
            ("FF-2", "Family Floor", 4),
            ("FF-3", "Family Floor", 6),
            ("FF-4", "Family Floor", 8),
            # Garden / Outdoor
            ("G-1", "Garden / Rooftop", 2),
            ("G-2", "Garden / Rooftop", 4),
            ("G-3", "Garden / Rooftop", 4),
            ("G-4", "Garden / Rooftop", 6)
        ]
        cursor.executemany("INSERT INTO dining_tables (name, section, capacity) VALUES (?, ?, ?)", tables)
        conn.commit()

    # Seed Menu Categories & Items if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ("Starters", "🍢"),
            ("Main Course", "🍛"),
            ("Breads & Rice", "🍚"),
            ("Beverages", "🥤"),
            ("Desserts", "🍨")
        ]
        cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", categories)
        conn.commit()

        # Map category names to IDs
        cursor.execute("SELECT id, name FROM categories")
        cat_map = {name: cid for cid, name in cursor.fetchall()}

        menu_items = [
            # Starters
            (cat_map["Starters"], "Paneer Tikka", 260, "veg"),
            (cat_map["Starters"], "Crispy Corn Salt & Pepper", 210, "veg"),
            (cat_map["Starters"], "Hara Bhara Kabab", 220, "veg"),
            (cat_map["Starters"], "Chicken Tikka (6 Pcs)", 320, "non-veg"),
            (cat_map["Starters"], "Murgh Malai Tikka", 350, "non-veg"),
            (cat_map["Starters"], "Chilli Chicken Dry", 290, "non-veg"),
            (cat_map["Starters"], "Fish Amritsari", 380, "non-veg"),
            # Main Course
            (cat_map["Main Course"], "Paneer Butter Masala", 280, "veg"),
            (cat_map["Main Course"], "Dal Makhani", 240, "veg"),
            (cat_map["Main Course"], "Kadai Paneer", 270, "veg"),
            (cat_map["Main Course"], "Butter Chicken (Boneless)", 360, "non-veg"),
            (cat_map["Main Course"], "Chicken Tikka Masala", 340, "non-veg"),
            (cat_map["Main Course"], "Mutton Rogan Josh", 440, "non-veg"),
            (cat_map["Main Course"], "Egg Curry (2 Eggs)", 220, "egg"),
            # Breads & Rice
            (cat_map["Breads & Rice"], "Tandoori Butter Roti", 35, "veg"),
            (cat_map["Breads & Rice"], "Butter Naan", 60, "veg"),
            (cat_map["Breads & Rice"], "Garlic Naan", 75, "veg"),
            (cat_map["Breads & Rice"], "Jeera Rice", 160, "veg"),
            (cat_map["Breads & Rice"], "Dum Biryani (Veg)", 260, "veg"),
            (cat_map["Breads & Rice"], "Chicken Dum Biryani", 340, "non-veg"),
            (cat_map["Breads & Rice"], "Mutton Dum Biryani", 420, "non-veg"),
            # Beverages
            (cat_map["Beverages"], "Fresh Lime Soda", 80, "veg"),
            (cat_map["Beverages"], "Sweet / Salted Lassi", 110, "veg"),
            (cat_map["Beverages"], "Virgin Mojito", 140, "veg"),
            (cat_map["Beverages"], "Cold Drink 600ml", 50, "veg"),
            (cat_map["Beverages"], "Packaged Water 1L", 30, "veg"),
            # Desserts
            (cat_map["Desserts"], "Gulab Jamun with Rabdi", 120, "veg"),
            (cat_map["Desserts"], "Sizzling Brownie with Ice Cream", 180, "veg"),
            (cat_map["Desserts"], "Kesar Pista Kulfi", 90, "veg")
        ]
        cursor.executemany("INSERT INTO menu_items (category_id, name, price, food_type) VALUES (?, ?, ?, ?)", menu_items)
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
