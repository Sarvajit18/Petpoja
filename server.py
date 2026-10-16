import os
import sys
import json
import socket
from datetime import datetime
from typing import List, Optional

import io
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
import qrcode
import qrcode.image.svg
from pydantic import BaseModel

from database import get_db, init_db

# Initialize database
init_db()

app = FastAPI(title="Petpooja-Style Restaurant POS & Captain App")

# Static directory setup
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

# ----------------- WebSocket Connection Manager -----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# ----------------- Utility Functions -----------------
def get_local_ip():
    """Detect LAN IP address so Captains can connect over WiFi/Ethernet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_escpos_raw(printer_ip: str, printer_port: int, raw_bytes: bytes):
    """Send ESC/POS raw bytes over network (Ethernet thermal printer)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3.0)
            sock.connect((printer_ip, printer_port))
            sock.sendall(raw_bytes)
            return True, "Printed successfully"
    except Exception as e:
        return False, str(e)

# ----------------- Request Models -----------------
class OrderItemIn(BaseModel):
    item_id: Optional[int] = None
    item_name: str
    price: float
    quantity: int
    notes: Optional[str] = ""

class PunchOrderIn(BaseModel):
    order_type: str = "dine_in" # dine_in, takeaway, delivery
    table_id: Optional[int] = None
    captain_name: str = "Counter"
    customer_name: Optional[str] = ""
    customer_phone: Optional[str] = ""
    items: List[OrderItemIn]

class SettleOrderIn(BaseModel):
    payment_mode: str = "cash" # cash, upi, card, split
    discount_percent: float = 0.0
    discount_amount: float = 0.0

class TransferTableIn(BaseModel):
    from_table_id: int
    to_table_id: int

class StaffLoginIn(BaseModel):
    pin: str

# ----------------- API Endpoints -----------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive & receive any client pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@app.get("/api/info")
def get_system_info():
    ip = get_local_ip()
    return {
        "local_ip": ip,
        "pos_url": f"http://{ip}:8000",
        "captain_url": f"http://{ip}:8000/captain",
        "kitchen_url": f"http://{ip}:8000/kitchen",
        "admin_url": f"http://{ip}:8000/admin"
    }

@app.get("/api/qr")
def get_qr_code(text: str):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(text, image_factory=factory)
    stream = io.BytesIO()
    img.save(stream)
    return Response(content=stream.getvalue(), media_type="image/svg+xml")

@app.get("/api/settings")
def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = dict(cursor.fetchall())
    conn.close()
    return settings

@app.post("/api/settings")
async def update_settings(payload: dict):
    conn = get_db()
    cursor = conn.cursor()
    for k, v in payload.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()
    conn.close()
    await manager.broadcast({"event": "SETTINGS_UPDATED"})
    return {"status": "ok"}

@app.get("/api/staff")
def get_staff():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role FROM staff ORDER BY id")
    staff = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return staff

@app.post("/api/staff/login")
def staff_login(payload: StaffLoginIn):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role FROM staff WHERE pin = ?", (payload.pin,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid PIN")
    return dict(row)

@app.get("/api/menu")
def get_menu():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, icon FROM categories ORDER BY id")
    categories = [dict(row) for row in cursor.fetchall()]

    for cat in categories:
        cursor.execute("SELECT * FROM menu_items WHERE category_id = ? ORDER BY name", (cat["id"],))
        cat["items"] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return categories

@app.get("/api/tables")
def get_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dining_tables ORDER BY section, id")
    tables = [dict(row) for row in cursor.fetchall()]

    for t in tables:
        if t["current_order_id"]:
            cursor.execute("""
                SELECT order_number, grand_total, subtotal, captain_name, created_at, status
                FROM orders WHERE id = ?
            """, (t["current_order_id"],))
            ord_row = cursor.fetchone()
            if ord_row:
                t["order"] = dict(ord_row)
                cursor.execute("SELECT SUM(quantity) FROM order_items WHERE order_id = ?", (t["current_order_id"],))
                t["item_count"] = cursor.fetchone()[0] or 0
        else:
            t["order"] = None
            t["item_count"] = 0

    conn.close()
    return tables

@app.post("/api/orders/punch")
async def punch_order(payload: PunchOrderIn):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cannot punch empty order")

    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_id = None
    table_name = "Counter / Takeaway"

    # Fetch settings for GST
    cursor.execute("SELECT value FROM settings WHERE key = 'gst_percent'")
    gst_val = cursor.fetchone()
    gst_percent = float(gst_val[0]) if gst_val else 5.0

    if payload.order_type == "dine_in":
        if not payload.table_id:
            raise HTTPException(status_code=400, detail="Table ID required for Dine-in")
        
        cursor.execute("SELECT * FROM dining_tables WHERE id = ?", (payload.table_id,))
        table = cursor.fetchone()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        table_name = table["name"]
        order_id = table["current_order_id"]

    # If no existing active order, create one
    if not order_id:
        today_date = datetime.now().strftime("%Y%m%d")
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number LIKE ?", (f"ORD-{today_date}-%",))
        daily_count = cursor.fetchone()[0] + 1
        order_num = f"ORD-{today_date}-{daily_count:04d}"

        cursor.execute("""
            INSERT INTO orders (order_number, order_type, table_id, table_name, captain_name, 
                                customer_name, customer_phone, status, created_at, gst_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """, (order_num, payload.order_type, payload.table_id, table_name, payload.captain_name,
              payload.customer_name, payload.customer_phone, now_str, gst_percent))
        order_id = cursor.lastrowid

        if payload.order_type == "dine_in" and payload.table_id:
            cursor.execute("""
                UPDATE dining_tables 
                SET status = 'occupied', current_order_id = ?, captain_name = ?
                WHERE id = ?
            """, (order_id, payload.captain_name, payload.table_id))

    # Generate KOT for newly punched items
    cursor.execute("SELECT COUNT(*) FROM kots WHERE order_id = ?", (order_id,))
    kot_num = cursor.fetchone()[0] + 1

    cursor.execute("""
        INSERT INTO kots (kot_number, order_id, table_name, captain_name, created_at, status)
        VALUES (?, ?, ?, ?, ?, 'active')
    """, (kot_num, order_id, table_name, payload.captain_name, now_str))
    kot_id = cursor.lastrowid

    # Insert items
    for item in payload.items:
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, item_name, price, quantity, notes, kot_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, item.item_id, item.item_name, item.price, item.quantity, item.notes or '', kot_id, now_str))

    # Recalculate totals
    cursor.execute("SELECT SUM(price * quantity) FROM order_items WHERE order_id = ?", (order_id,))
    subtotal = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT discount_percent, discount_amount, gst_percent FROM orders WHERE id = ?", (order_id,))
    disc_row = cursor.fetchone()
    disc_pct = disc_row["discount_percent"]
    disc_amt = disc_row["discount_amount"]
    if disc_pct > 0:
        disc_amt = (subtotal * disc_pct) / 100.0

    taxable = max(0.0, subtotal - disc_amt)
    gst_amount = round((taxable * gst_percent) / 100.0, 2)
    grand_total = round(taxable + gst_amount)

    cursor.execute("""
        UPDATE orders 
        SET subtotal = ?, discount_amount = ?, gst_amount = ?, grand_total = ?
        WHERE id = ?
    """, (subtotal, disc_amt, gst_amount, grand_total, order_id))

    conn.commit()

    # Fetch created KOT details for real-time broadcast
    cursor.execute("SELECT * FROM kots WHERE id = ?", (kot_id,))
    kot_dict = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM order_items WHERE kot_id = ?", (kot_id,))
    kot_dict["items"] = [dict(r) for r in cursor.fetchall()]

    conn.close()

    # Broadcast to all Captains, POS counters, and Kitchen screens
    await manager.broadcast({
        "event": "KOT_CREATED",
        "kot": kot_dict,
        "table_id": payload.table_id,
        "order_id": order_id
    })

    return {
        "status": "success",
        "order_id": order_id,
        "kot_id": kot_id,
        "kot_number": kot_num,
        "grand_total": grand_total
    }

@app.get("/api/orders/active")
def get_active_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders 
        WHERE status IN ('active', 'billed') 
        ORDER BY id DESC
    """)
    orders = [dict(row) for row in cursor.fetchall()]
    for ord_obj in orders:
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (ord_obj["id"],))
        ord_obj["items"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return orders

@app.get("/api/orders/{order_id}")
def get_order_details(order_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = dict(order_row)
    cursor.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,))
    order["items"] = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM kots WHERE order_id = ? ORDER BY id", (order_id,))
    order["kots"] = [dict(r) for r in cursor.fetchall()]
    for k in order["kots"]:
        cursor.execute("SELECT * FROM order_items WHERE kot_id = ?", (k["id"],))
        k["items"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return order

@app.post("/api/orders/{order_id}/mark_billed")
async def mark_order_billed(order_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT table_id FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute("UPDATE orders SET status = 'billed' WHERE id = ?", (order_id,))
    if row["table_id"]:
        cursor.execute("UPDATE dining_tables SET status = 'billed' WHERE id = ?", (row["table_id"],))

    conn.commit()
    conn.close()

    await manager.broadcast({"event": "ORDER_BILLED", "order_id": order_id})
    return {"status": "ok"}

@app.post("/api/orders/{order_id}/settle")
async def settle_order(order_id: int, payload: SettleOrderIn):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    subtotal = order_row["subtotal"]
    gst_percent = order_row["gst_percent"]
    disc_amt = payload.discount_amount
    if payload.discount_percent > 0:
        disc_amt = (subtotal * payload.discount_percent) / 100.0

    taxable = max(0.0, subtotal - disc_amt)
    gst_amt = round((taxable * gst_percent) / 100.0, 2)
    grand_total = round(taxable + gst_amt)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE orders 
        SET status = 'settled', payment_mode = ?, discount_percent = ?, 
            discount_amount = ?, gst_amount = ?, grand_total = ?, settled_at = ?
        WHERE id = ?
    """, (payload.payment_mode, payload.discount_percent, disc_amt, gst_amt, grand_total, now_str, order_id))

    if order_row["table_id"]:
        cursor.execute("""
            UPDATE dining_tables 
            SET status = 'available', current_order_id = NULL, captain_name = NULL
            WHERE id = ?
        """, (order_row["table_id"],))

    conn.commit()
    conn.close()

    await manager.broadcast({"event": "ORDER_SETTLED", "order_id": order_id})
    return {"status": "settled", "grand_total": grand_total}

@app.post("/api/orders/transfer")
async def transfer_table(payload: TransferTableIn):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dining_tables WHERE id = ?", (payload.from_table_id,))
    from_tbl = cursor.fetchone()
    cursor.execute("SELECT * FROM dining_tables WHERE id = ?", (payload.to_table_id,))
    to_tbl = cursor.fetchone()

    if not from_tbl or not to_tbl:
        conn.close()
        raise HTTPException(status_code=404, detail="One or both tables not found")

    if not from_tbl["current_order_id"]:
        conn.close()
        raise HTTPException(status_code=400, detail="From table has no active order")

    if to_tbl["status"] != "available":
        conn.close()
        raise HTTPException(status_code=400, detail="Destination table is not available")

    order_id = from_tbl["current_order_id"]
    cursor.execute("UPDATE orders SET table_id = ?, table_name = ? WHERE id = ?", 
                   (to_tbl["id"], to_tbl["name"], order_id))
    cursor.execute("UPDATE dining_tables SET status = 'available', current_order_id = NULL, captain_name = NULL WHERE id = ?", 
                   (from_tbl["id"],))
    cursor.execute("UPDATE dining_tables SET status = 'occupied', current_order_id = ?, captain_name = ? WHERE id = ?", 
                   (order_id, from_tbl["captain_name"], to_tbl["id"]))

    conn.commit()
    conn.close()

    await manager.broadcast({"event": "TABLE_TRANSFERRED"})
    return {"status": "transferred"}

@app.get("/api/kots/active")
def get_active_kots():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kots WHERE status = 'active' ORDER BY id ASC")
    kots = [dict(row) for row in cursor.fetchall()]
    for kot in kots:
        cursor.execute("SELECT * FROM order_items WHERE kot_id = ?", (kot["id"],))
        kot["items"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return kots

@app.post("/api/kots/{kot_id}/complete")
async def complete_kot(kot_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE kots SET status = 'completed' WHERE id = ?", (kot_id,))
    conn.commit()
    conn.close()
    await manager.broadcast({"event": "KOT_COMPLETED", "kot_id": kot_id})
    return {"status": "ok"}

@app.get("/api/reports/today")
def get_today_report():
    conn = get_db()
    cursor = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*) as total_bills,
               COALESCE(SUM(grand_total), 0) as total_sales,
               COALESCE(SUM(gst_amount), 0) as total_gst,
               COALESCE(SUM(discount_amount), 0) as total_discounts
        FROM orders
        WHERE status = 'settled' AND settled_at LIKE ?
    """, (f"{today_date}%",))
    summary = dict(cursor.fetchone())

    # Payment mode breakdown
    cursor.execute("""
        SELECT payment_mode, COUNT(*) as count, SUM(grand_total) as amount
        FROM orders
        WHERE status = 'settled' AND settled_at LIKE ?
        GROUP BY payment_mode
    """, (f"{today_date}%",))
    summary["payments"] = [dict(r) for r in cursor.fetchall()]

    # Top selling items
    cursor.execute("""
        SELECT item_name, SUM(quantity) as total_qty, SUM(price * quantity) as total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'settled' AND o.settled_at LIKE ?
        GROUP BY item_name
        ORDER BY total_qty DESC LIMIT 7
    """, (f"{today_date}%",))
    summary["top_items"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return summary

# ----------------- ESC/POS Network Printing Test Endpoint -----------------
class EscPosPrintRequest(BaseModel):
    printer_ip: str
    printer_port: int = 9100
    order_id: int

@app.post("/api/print/escpos")
def print_via_escpos(req: EscPosPrintRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (req.order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (req.order_id,))
    items = cursor.fetchall()

    cursor.execute("SELECT key, value FROM settings")
    settings = dict(cursor.fetchall())
    conn.close()

    # Build standard ESC/POS byte sequence
    # ESC @ = Initialize printer
    # ESC a 1 = Center align
    # ESC ! 16 = Double height
    buf = bytearray()
    buf.extend(b"\x1b\x40") # Init
    buf.extend(b"\x1b\x61\x01") # Center
    buf.extend(f"{settings.get('restaurant_name', 'Restaurant')}\n".encode('latin-1', 'ignore'))
    buf.extend(f"{settings.get('address', '')}\n".encode('latin-1', 'ignore'))
    buf.extend(f"Ph: {settings.get('phone', '')} | GSTIN: {settings.get('gstin', '')}\n".encode('latin-1', 'ignore'))
    buf.extend(b"------------------------------------------\n")
    buf.extend(b"\x1b\x61\x00") # Left align
    buf.extend(f"Order: {order_row['order_number']}   Table: {order_row['table_name']}\n".encode('latin-1', 'ignore'))
    buf.extend(f"Date: {order_row['created_at']}   Cap: {order_row['captain_name']}\n".encode('latin-1', 'ignore'))
    buf.extend(b"------------------------------------------\n")
    buf.extend(b"Item                     Qty   Rate    Total\n")
    buf.extend(b"------------------------------------------\n")
    for it in items:
        name = it['item_name'][:20].ljust(20)
        line = f"{name} {str(it['quantity']).rjust(3)} {str(int(it['price'])).rjust(6)} {str(int(it['price']*it['quantity'])).rjust(8)}\n"
        buf.extend(line.encode('latin-1', 'ignore'))
    buf.extend(b"------------------------------------------\n")
    buf.extend(b"\x1b\x61\x02") # Right align
    buf.extend(f"Subtotal: {order_row['subtotal']:.2f}\n".encode('latin-1', 'ignore'))
    if order_row['discount_amount'] > 0:
        buf.extend(f"Discount: -{order_row['discount_amount']:.2f}\n".encode('latin-1', 'ignore'))
    buf.extend(f"GST ({order_row['gst_percent']}%): {order_row['gst_amount']:.2f}\n".encode('latin-1', 'ignore'))
    buf.extend(f"GRAND TOTAL: Rs {order_row['grand_total']:.2f}\n".encode('latin-1', 'ignore'))
    buf.extend(b"\x1b\x61\x01") # Center
    buf.extend(b"\nThank you for dining with us!\nVisit Again!\n\n\n\n\x1d\x56\x41\x03") # Cut paper

    success, msg = print_escpos_raw(req.printer_ip, req.printer_port, bytes(buf))
    if not success:
        raise HTTPException(status_code=500, detail=f"Printer error: {msg}")
    return {"status": "printed", "message": msg}

# ----------------- Web UI HTML Routes -----------------
@app.get("/", response_class=HTMLResponse)
def serve_pos():
    return FileResponse(os.path.join(STATIC_DIR, "pos.html"))

@app.get("/captain", response_class=HTMLResponse)
def serve_captain():
    return FileResponse(os.path.join(STATIC_DIR, "captain.html"))

@app.get("/kitchen", response_class=HTMLResponse)
def serve_kitchen():
    return FileResponse(os.path.join(STATIC_DIR, "kitchen.html"))

@app.get("/admin", response_class=HTMLResponse)
def serve_admin():
    return FileResponse(os.path.join(STATIC_DIR, "admin.html"))

# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    print("=================================================================")
    print(" >>> PETPOOJA-STYLE RESTAURANT POS SERVER RUNNING <<<")
    print("=================================================================")
    print(f" [*] Main Billing Station POS : http://localhost:8000")
    print(f" [*] LAN / Ethernet Billing   : http://{local_ip}:8000")
    print(f" [*] Captain App (Phone/Tab)  : http://{local_ip}:8000/captain")
    print(f" [*] Kitchen Display (KDS)   : http://{local_ip}:8000/kitchen")
    print(f" [*] Admin & Daily Reports    : http://{local_ip}:8000/admin")
    print("=================================================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)
