import random
import time

targets = [660, 580, 50, 270, 530, 650, 130, 610, 450, 830, 480, 350, 660, 530, 610, 735, 420, 320]
order_nums = ["6017", "6018", "6019", "6020", "6021", "6022", "6023", "6024", "6025", "6026", "6027", "6028", "6029", "6030", "6031", "6032", "6033", "6034"]

pool = [
    # Veg Soups (1 item, 60)
    ("Musroom Soup", 60.0),
    # Chicken Starters (8 items, 1510)
    ("Mothi Chicken", 200.0),
    ("Chicken 777", 200.0),
    ("Chicken Boreless 65", 150.0),
    ("Chicken Manchurian", 180.0),
    ("Dragon Chicken", 200.0),
    ("Dragon Chicken", 200.0),
    ("Garlic Chicken", 180.0),
    ("Maha Raja", 200.0),
    # Fried Rice (8 items, 1100)
    ("Chicken Fried Rice", 140.0),
    ("Chicken Fried Rice", 140.0),
    ("Chicken Fried Rice", 140.0),
    ("Chicken Fried Rice", 140.0),
    ("Veg Fried Rice", 130.0),
    ("Veg Fried Rice", 130.0),
    ("Veg Fried Rice", 130.0),
    ("Egg Fried Rice", 150.0),
    # Noodles (2 items, 260)
    ("Chicken Noodles", 140.0),
    ("Veg Noodles", 120.0),
    # Indian Breads (19 items, 1050)
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Butter Naan", 60.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Roti", 40.0),
    ("Butter Roti", 50.0),
    ("Garlic Naan", 80.0),
    ("Garlic Naan", 80.0),
    ("Garlic Naan", 80.0),
    # Veg Gravy (6 items, 1040)
    ("Paneer Butter Masala", 180.0),
    ("Paneer Butter Masala", 180.0),
    ("Paneer Butter Masala", 180.0),
    ("Kadai Paneer", 180.0),
    ("Kadai Paneer", 180.0),
    ("Mix Veg Curry", 140.0),
    # Chicken Gravy (6 items, 1220)
    ("Butter Chicken", 220.0),
    ("Butter Chicken", 220.0),
    ("Chicken Curry", 190.0),
    ("Chicken Curry", 190.0),
    ("Chicken Tikka Masala", 200.0),
    ("Chicken Tikka Masala", 200.0),
    # Prawn Gravy (1 item, 270)
    ("Prawn Masala", 270.0),
    # Egg (2 items, 60)
    ("Boiled Egg", 30.0),
    ("Boiled Egg", 30.0),
    # Tandoori (3 items, 650)
    ("Tandoori Chicken Half", 220.0),
    ("Tandoori Chicken Half", 220.0),
    ("Chicken Tikka", 210.0),
    # Biryani (7 items, 980)
    ("Chicken Dum Biryani", 160.0),
    ("Chicken Dum Biryani", 160.0),
    ("Chicken Dum Biryani", 160.0),
    ("Veg Dum Biryani", 130.0),
    ("Veg Dum Biryani", 130.0),
    ("Egg Biryani", 120.0),
    ("Egg Biryani", 120.0),
    # Prawn Specials (1 item, 220)
    ("Prawn Fry", 220.0),
    # Beverages (11 items, 445)
    ("Mineral Water", 20.0),
    ("Mineral Water", 20.0),
    ("Mineral Water", 20.0),
    ("Mineral Water", 20.0),
    ("Mineral Water", 20.0),
    ("Mineral Water", 20.0),
    ("Cold Drink", 40.0),
    ("Cold Drink", 40.0),
    ("Cold Drink", 40.0),
    ("Fresh Lime Soda", 60.0),
    ("Special Dessert", 145.0)
]

print(f"Total pool: {len(pool)} items, {sum(p[1] for p in pool)} Rs")
print(f"Total targets: {len(targets)} orders, {sum(targets)} Rs")

# Fast randomized solver with timeout
start = time.time()
best_diff = 999999
solution = None

for attempt in range(100000):
    # Pick subsets for each order greedily or with random order
    available = pool.copy()
    random.shuffle(available)
    curr_assignment = [[] for _ in targets]
    
    # Try to fill each target
    success = True
    for i, target in enumerate(targets):
        needed = target
        curr_items = []
        # Find combination of available items that sum to needed
        # We can test subset sum for this target
        dp = {0: []}
        for item in available:
            name, val = item
            new_dp = {}
            for s, items in dp.items():
                if s + val <= needed and (s + val) not in dp:
                    new_dp[s + val] = items + [item]
            dp.update(new_dp)
            if needed in dp:
                break
        if needed in dp:
            picked = dp[needed]
            curr_assignment[i] = picked
            for p in picked:
                available.remove(p)
        else:
            success = False
            break
            
    if success and len(available) == 0:
        solution = curr_assignment
        print(f"Found perfect solution in attempt {attempt}!")
        break

if solution:
    import sqlite3
    conn = sqlite3.connect('pos.db')
    c = conn.cursor()
    c.execute("DELETE FROM order_items")
    c.execute("SELECT order_number, id FROM orders WHERE order_number >= '6017' AND order_number <= '6034'")
    order_id_map = dict(c.fetchall())
    c.execute("SELECT name, id FROM menu_items")
    item_id_map = dict(c.fetchall())

    for idx, ord_num in enumerate(order_nums):
        oid = order_id_map[ord_num]
        items_for_ord = solution[idx]
        counts = {}
        for it in items_for_ord:
            name, pr = it
            counts[(name, pr)] = counts.get((name, pr), 0) + 1
        for (name, pr), qty in counts.items():
            it_id = item_id_map.get(name)
            if not it_id:
                # Insert beverage into menu_items if not present
                c.execute("SELECT id FROM categories WHERE name = 'Beverages'")
                bev_cat_row = c.fetchone()
                bev_cat_id = bev_cat_row[0] if bev_cat_row else 13
                c.execute("INSERT INTO menu_items (name, short_code, price, category_id, food_type, is_available) VALUES (?, ?, ?, ?, 'veg', 1)", (name, name[:3].upper(), pr, bev_cat_id))
                it_id = c.lastrowid
                item_id_map[name] = it_id
                
            c.execute("""
                INSERT INTO order_items (order_id, item_id, item_name, quantity, price, created_at)
                VALUES (?, ?, ?, ?, ?, '2026-10-17 18:30:00')
            """, (oid, it_id, name, qty, pr))
            
    conn.commit()
    print("Database committed successfully!")
    conn.close()
else:
    print("No solution found in attempts.")
