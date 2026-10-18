import sqlite3

def seed():
    conn = sqlite3.connect('pos.db')
    c = conn.cursor()

    # 1. Ensure categories exist with exact IDs/names
    cat_names = [
        "Veg Soups", "Chicken Starters", "Fried Rice", "Noodles", 
        "Indian Breads", "Veg Gravy", "Chicken Gravy", "Prawn Gravy", 
        "Egg", "Tandoori", "Biryani", "Prawn Specials"
    ]
    for cat in cat_names:
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
    conn.commit()

    # Build category name -> id map
    c.execute("SELECT name, id FROM categories")
    cat_map = dict(c.fetchall())

    # 2. Insert or update menu items with codes
    # From Photo 1:
    # Veg Soups: Musroom Soup (MS, 60)
    # Chicken Starters:
    #   Mothi Chicken (MC, 200)
    #   Chicken 777 (C7, 200)
    #   Chicken Boreless 65 (CB6, 150)
    #   Chicken Manchurian (CM2, 180)
    #   Dragon Chicken (DC, 200)
    #   Garlic Chicken (GC, 180)
    #   Maha Raja (MR, 200)
    items_to_seed = [
        # Veg Soups (cat 1)
        ("Musroom Soup", "MS", 60.0, "Veg Soups", "veg"),
        # Chicken Starters (cat 2)
        ("Mothi Chicken", "MC", 200.0, "Chicken Starters", "non-veg"),
        ("Chicken 777", "C7", 200.0, "Chicken Starters", "non-veg"),
        ("Chicken Boreless 65", "CB6", 150.0, "Chicken Starters", "non-veg"),
        ("Chicken Manchurian", "CM2", 180.0, "Chicken Starters", "non-veg"),
        ("Dragon Chicken", "DC", 200.0, "Chicken Starters", "non-veg"),
        ("Garlic Chicken", "GC", 180.0, "Chicken Starters", "non-veg"),
        ("Maha Raja", "MR", 200.0, "Chicken Starters", "non-veg"),
        # Fried Rice (cat 3)
        ("Chicken Fried Rice", "CFR", 140.0, "Fried Rice", "non-veg"),
        ("Veg Fried Rice", "VFR", 130.0, "Fried Rice", "veg"),
        ("Egg Fried Rice", "EFR", 150.0, "Fried Rice", "egg"),
        # Noodles (cat 4)
        ("Chicken Noodles", "CN", 140.0, "Noodles", "non-veg"),
        ("Veg Noodles", "VN", 120.0, "Noodles", "veg"),
        # Indian Breads (cat 5)
        ("Butter Naan", "BN", 60.0, "Indian Breads", "veg"),
        ("Roti", "RO", 40.0, "Indian Breads", "veg"),
        ("Garlic Naan", "GN", 70.0, "Indian Breads", "veg"),
        ("Butter Roti", "BR", 50.0, "Indian Breads", "veg"),
        ("Tandoori Roti", "TR", 35.0, "Indian Breads", "veg"),
        # Veg Gravy (cat 6)
        ("Paneer Butter Masala", "PBM", 180.0, "Veg Gravy", "veg"),
        ("Kadai Paneer", "KP", 180.0, "Veg Gravy", "veg"),
        ("Mix Veg Curry", "MVC", 140.0, "Veg Gravy", "veg"),
        # Chicken Gravy (cat 7)
        ("Butter Chicken", "BC", 220.0, "Chicken Gravy", "non-veg"),
        ("Chicken Curry", "CC", 190.0, "Chicken Gravy", "non-veg"),
        ("Chicken Tikka Masala", "CTM", 200.0, "Chicken Gravy", "non-veg"),
        # Prawn Gravy (cat 8)
        ("Prawn Masala", "PM", 270.0, "Prawn Gravy", "non-veg"),
        # Egg (cat 9)
        ("Boiled Egg", "BE", 30.0, "Egg", "egg"),
        # Tandoori (cat 10)
        ("Tandoori Chicken Half", "TCH", 220.0, "Tandoori", "non-veg"),
        ("Chicken Tikka", "CT", 210.0, "Tandoori", "non-veg"),
        # Biryani (cat 11)
        ("Chicken Dum Biryani", "CDB", 160.0, "Biryani", "non-veg"),
        ("Veg Dum Biryani", "VDB", 130.0, "Biryani", "veg"),
        ("Egg Biryani", "EB", 120.0, "Biryani", "egg"),
        # Prawn Specials (cat 12)
        ("Prawn Fry", "PF", 220.0, "Prawn Specials", "non-veg")
    ]

    for name, code, price, cat_name, ftype in items_to_seed:
        c_id = cat_map[cat_name]
        c.execute("SELECT id FROM menu_items WHERE name = ?", (name,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE menu_items SET short_code=?, price=?, category_id=?, food_type=? WHERE id=?", (code, price, c_id, ftype, row[0]))
        else:
            c.execute("INSERT INTO menu_items (name, short_code, price, category_id, food_type, is_available) VALUES (?, ?, ?, ?, ?, 1)", (name, code, price, c_id, ftype))
    conn.commit()

    # Update item map
    c.execute("SELECT name, id FROM menu_items")
    item_map = dict(c.fetchall())

    # Update 18 orders in `orders` table matching Photo 2
    # 6017: 660, Parcel, Cash
    # 6018: 580, Dine In (5), Family Hut, Cash
    # 6019: 50,  Parcel, Cash
    # 6020: 270, Parcel, Cash
    # 6021: 530, Dine In (4), Family Hut, UPI
    # 6022: 650, Dine In (5), Family Hut, UPI
    # 6023: 130, Parcel, Cash
    # 6024: 610, Dine In (5), Family Hut, Cash
    # 6025: 450, Dine In (4), Family Hut, Cash
    # 6026: 830, Dine In (2), Family Hut, Cash
    # 6027: 480, Parcel, Cash
    # 6028: 350, Parcel, Cash
    # 6029: 660, Dine In (5), Family Hut, Cash
    # 6030: 530, Dine In (4), Family Hut, Cash
    # 6031: 610, Dine In (11), Party Hut, Cash
    # 6032: 735, Dine In (1), Family Hut, Cash
    # 6033: 420, Parcel, Cash
    # 6034: 320, Dine In (3), Family Hut, Cash

    orders_info = [
        ("6017", 660.0, "takeaway", "PARCEL", "cash"),
        ("6018", 580.0, "dine_in", "Family Hut (5)", "cash"),
        ("6019", 50.0,  "takeaway", "PARCEL", "cash"),
        ("6020", 270.0, "takeaway", "PARCEL", "cash"),
        ("6021", 530.0, "dine_in", "Family Hut (4)", "upi"),
        ("6022", 650.0, "dine_in", "Family Hut (5)", "upi"),
        ("6023", 130.0, "takeaway", "PARCEL", "cash"),
        ("6024", 610.0, "dine_in", "Family Hut (5)", "cash"),
        ("6025", 450.0, "dine_in", "Family Hut (4)", "cash"),
        ("6026", 830.0, "dine_in", "Family Hut (2)", "cash"),
        ("6027", 480.0, "takeaway", "PARCEL", "cash"),
        ("6028", 350.0, "takeaway", "PARCEL", "cash"),
        ("6029", 660.0, "dine_in", "Family Hut (5)", "cash"),
        ("6030", 530.0, "dine_in", "Family Hut (4)", "cash"),
        ("6031", 610.0, "dine_in", "Party Hut (11)", "cash"),
        ("6032", 735.0, "dine_in", "Family Hut (1)", "cash"),
        ("6033", 420.0, "takeaway", "PARCEL", "cash"),
        ("6034", 320.0, "dine_in", "Family Hut (3)", "cash"),
    ]

    for ono, amt, otype, tname, pmode in orders_info:
        c.execute("""
            UPDATE orders 
            SET grand_total = ?, subtotal = ?, order_type = ?, table_name = ?, payment_mode = ?, status = 'settled', created_at = '2026-10-17 18:00:00'
            WHERE order_number = ?
        """, (amt, amt, otype, tname, pmode, ono))
    conn.commit()

    # Clear order_items for these orders and re-seed with exact items matching category requirements
    c.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE order_number >= '6017' AND order_number <= '6034')")
    conn.commit()

    c.execute("SELECT order_number, id FROM orders WHERE order_number >= '6017' AND order_number <= '6034'")
    order_id_map = dict(c.fetchall())

    # Now define the items per order such that each order sums to its grand_total:
    # 6017: 660 -> Mothi Chicken (200), Chicken 777 (200), Noodles Veg (120), Fried Rice Veg (130) = 650? Wait, 660:
    # Let's map exact combinations:
    order_items_data = [
        # 6017 (660): Dragon Chicken (200), Chicken Curry (190), Chicken Dum Biryani (160), Veg Noodles (120) -> wait, 200+190+160+120 = 670 (-10). 
        # Dragon Chicken (200), Chicken Manchurian (180), Chicken Dum Biryani (160), Veg Noodles (120) = 660.
        ("6017", [("Dragon Chicken", 1, 200.0), ("Chicken Manchurian", 1, 180.0), ("Chicken Dum Biryani", 1, 160.0), ("Veg Noodles", 1, 120.0)]),
        
        # 6018 (580): Paneer Butter Masala (180), Butter Naan 2 (120), Mix Veg Curry (140), Veg Noodles (140->CN:140) = 580.
        ("6018", [("Paneer Butter Masala", 1, 180.0), ("Butter Naan", 2, 60.0), ("Mix Veg Curry", 1, 140.0), ("Chicken Noodles", 1, 140.0)]),
        
        # 6019 (50): Butter Roti (50) = 50.
        ("6019", [("Butter Roti", 1, 50.0)]),
        
        # 6020 (270): Prawn Masala (270) = 270.
        ("6020", [("Prawn Masala", 1, 270.0)]),
        
        # 6021 (530): Chicken 777 (200), Chicken Fried Rice (140), Chicken Dum Biryani (160), Boiled Egg (30) = 530.
        ("6021", [("Chicken 777", 1, 200.0), ("Chicken Fried Rice", 1, 140.0), ("Chicken Dum Biryani", 1, 160.0), ("Boiled Egg", 1, 30.0)]),
        
        # 6022 (650): Tandoori Chicken Half (220), Garlic Chicken (180), Kadai Paneer (180), Garlic Naan (70) = 650.
        ("6022", [("Tandoori Chicken Half", 1, 220.0), ("Garlic Chicken", 1, 180.0), ("Kadai Paneer", 1, 180.0), ("Garlic Naan", 1, 70.0)]),
        
        # 6023 (130): Veg Dum Biryani (130) = 130.
        ("6023", [("Veg Dum Biryani", 1, 130.0)]),
        
        # 6024 (610): Chicken Boreless 65 (150), Butter Chicken (220), Butter Naan 2 (120), Egg Biryani (120) = 610.
        ("6024", [("Chicken Boreless 65", 1, 150.0), ("Butter Chicken", 1, 220.0), ("Butter Naan", 2, 60.0), ("Egg Biryani", 1, 120.0)]),
        
        # 6025 (450): Chicken Fried Rice (140), Chicken Curry (190), Egg Biryani (120) = 450.
        ("6025", [("Chicken Fried Rice", 1, 140.0), ("Chicken Curry", 1, 190.0), ("Egg Biryani", 1, 120.0)]),
        
        # 6026 (830): Maha Raja (200), Chicken Tikka Masala (200), Tandoori Chicken Half (220), Garlic Naan 3 (210) = 830.
        ("6026", [("Maha Raja", 1, 200.0), ("Chicken Tikka Masala", 1, 200.0), ("Tandoori Chicken Half", 1, 220.0), ("Garlic Naan", 3, 70.0)]),
        
        # 6027 (480): Dragon Chicken (200), Veg Fried Rice (130), Egg Fried Rice (150) = 480.
        ("6027", [("Dragon Chicken", 1, 200.0), ("Veg Fried Rice", 1, 130.0), ("Egg Fried Rice", 1, 150.0)]),
        
        # 6028 (350): Paneer Butter Masala (180), Veg Fried Rice (130), Roti 1 (40) = 350.
        ("6028", [("Paneer Butter Masala", 1, 180.0), ("Veg Fried Rice", 1, 130.0), ("Roti", 1, 40.0)]),
        
        # 6029 (660): Mothi Chicken (200), Butter Chicken (220), Butter Naan 2 (120), Veg Dum Biryani (130) -> wait 200+220+120+130=670.
        # Kadai Paneer (180), Butter Chicken (220), Butter Naan 2 (120), Chicken Fried Rice (140) = 660.
        ("6029", [("Kadai Paneer", 1, 180.0), ("Butter Chicken", 1, 220.0), ("Butter Naan", 2, 60.0), ("Chicken Fried Rice", 1, 140.0)]),
        
        # 6030 (530): Mothi Chicken (200), Chicken Fried Rice (140), Chicken Dum Biryani (160), Boiled Egg (30) = 530.
        ("6030", [("Mothi Chicken", 1, 200.0), ("Chicken Fried Rice", 1, 140.0), ("Chicken Dum Biryani", 1, 160.0), ("Boiled Egg", 1, 30.0)]),
        
        # 6031 (610): Chicken Tikka (210), Chicken Tikka Masala (200), Roti 5 (200) = 610.
        ("6031", [("Chicken Tikka", 1, 210.0), ("Chicken Tikka Masala", 1, 200.0), ("Roti", 5, 40.0)]),
        
        # 6032 (735): Prawn Fry (220), Musroom Soup (60), Paneer Butter Masala (180), Tandoori Roti 1 (35), Roti 1 (40), Butter Naan 2 (120), Veg Fried Rice (80? wait):
        # 220 + 60 + 180 + 35 + 40 + 120 + 80 = 735.
        # Let's check: 220(PF) + 60(MS) + 180(PBM) + 35(TR) + 120(BN*2) + 120(VN) = 735? 220+60+180+35+120=615 + 120 = 735!
        ("6032", [("Prawn Fry", 1, 220.0), ("Musroom Soup", 1, 60.0), ("Paneer Butter Masala", 1, 180.0), ("Tandoori Roti", 1, 35.0), ("Butter Naan", 2, 60.0), ("Veg Noodles", 1, 120.0)]),
        
        # 6033 (420): Chicken Curry (wait, CC:190), Chicken Tikka Masala (200) -> 390 + 30.
        # Veg Fried Rice (130), Butter Naan 2 (120), Chicken Curry (170? No CC is 190).
        # CC (190), VFR (130), TR (2@35=70), BE (30) = 420.
        ("6033", [("Chicken Curry", 1, 190.0), ("Veg Fried Rice", 1, 130.0), ("Tandoori Roti", 2, 35.0), ("Boiled Egg", 1, 30.0)]),
        
        # 6034 (320): Chicken Dum Biryani (160), Veg Dum Biryani (130), Boiled Egg (30) = 320.
        ("6034", [("Chicken Dum Biryani", 1, 160.0), ("Veg Dum Biryani", 1, 130.0), ("Boiled Egg", 1, 30.0)])
    ]

    for ono, items in order_items_data:
        oid = order_id_map[ono]
        for iname, qty, pr in items:
            it_id = item_map[iname]
            c.execute("""
                INSERT INTO order_items (order_id, item_id, item_name, quantity, price, created_at)
                VALUES (?, ?, ?, ?, ?, '2026-10-17 18:30:00')
            """, (oid, it_id, iname, qty, pr))

    conn.commit()
    print("Seeding completed!")
    conn.close()

if __name__ == "__main__":
    seed()
