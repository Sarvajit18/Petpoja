import sqlite3

def seed():
    conn = sqlite3.connect('pos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES ('11 -11 SPL CHICKEN GRAVY', '🍗')")
    cursor.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES ('BIRYANI', '🍚')")
    
    cursor.execute("SELECT id FROM categories WHERE name = '11 -11 SPL CHICKEN GRAVY'")
    c_gravy_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM categories WHERE name = 'BIRYANI'")
    c_biryani_id = cursor.fetchone()[0]

    items = [
        (c_gravy_id, 'Hyderabad Chicken Gravy', 220, 'non-veg'),
        (c_gravy_id, 'Jaipur Chicken Masala', 220, 'non-veg'),
        (c_gravy_id, 'Japan Chicken Gravy', 220, 'non-veg'),
        (c_gravy_id, 'Kadai Chicken Gravy', 220, 'non-veg'),
        (c_gravy_id, 'Kola Urundai Chicken Masala', 230, 'non-veg'),
        (c_biryani_id, 'Bucket Biryani (3 Kg)', 599, 'non-veg'),
        (c_biryani_id, 'Chicken 65 Biryani', 160, 'non-veg'),
        (c_biryani_id, 'Chicken Biryani', 130, 'non-veg'),
        (c_biryani_id, 'Egg Biryani', 100, 'egg'),
        (c_biryani_id, 'Mutton Biryani', 250, 'non-veg'),
        (c_biryani_id, 'Mutton Thokku Biryani', 230, 'non-veg'),
    ]

    for cid, name, price, ftype in items:
        cursor.execute("SELECT id FROM menu_items WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE menu_items SET price = ?, food_type = ?, category_id = ? WHERE id = ?", (price, ftype, cid, row[0]))
        else:
            cursor.execute("INSERT INTO menu_items (category_id, name, price, food_type) VALUES (?, ?, ?, ?)", (cid, name, price, ftype))

    # Also sync into dist/Shansara_POS/pos.db if it exists
    conn.commit()
    conn.close()
    print("Database seeded with exact menu items successfully!")

if __name__ == "__main__":
    seed()
