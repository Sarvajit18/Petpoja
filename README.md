# Shansara Restaurant POS & Captain App (Desktop & Mobile)

A complete, production-grade, offline-first Restaurant Billing and Management System named **Shansara POS**. Designed specifically for local network (LAN / Ethernet / Wi-Fi) operation without requiring any active internet connection or cloud subscriptions.

---

## 🌟 What's Included

### 1. 🖥️ Main Billing Software (Windows Desktop App)
* **Dedicated Windows App Window:** Runs in a standalone application window (no address bar, no tabs) powered by Edge/Chrome app mode or Python.
* **Table Management:** Visual multi-section floor plan (Family Hut, AC Hall, Garden/Rooftop).
* **Live Statuses:** 🟢 Vacant, 🔴 Occupied (with running amount, elapsed timer, captain name), 🟡 Billed.
* **Instant KOT & Bill Generation:** Supports 80mm & 58mm ESC/POS thermal receipts and network printers (TCP/IP port 9100).
* **GST & Settlement:** Automatic CGST/SGST, discounts, Cash, UPI QR, and Card payments.
* **QR Code Pairing:** Cashier can click **"📲 Connect Captain App"** to show a live QR code on screen for instant waiter phone connection.

### 2. 📱 Mobile Captain App (Android / iOS / Tablets)
* **Instant PWA Installation:** Waiters can scan the QR code from the billing counter and tap **"Install App"** to add it to their Android/iOS home screen.
* **Native Android Project (`/android`):** Full Android Studio project ready to compile into a `.apk` for Sunmi, iMin, or handheld POS devices.
* **Speedy Order Punching:** Category chips, dish search, Veg/Non-Veg indicators, custom cooking notes (e.g. *"Extra spicy"*, *"No onion"*).
* **Real-time Sync:** Orders punched by captains instantly appear on the kitchen display and billing screen via WebSockets.

### 3. 👨‍🍳 Kitchen Display System (`/kitchen`)
* Real-time incoming KOT board.
* Audio chime bell alert whenever a new order is punched.
* "Mark Ready / Served" button and Fullscreen mode.

### 4. ⚙️ Admin & Daily Reports (`/admin`)
* Real-time sales summary (Today's Revenue, Settled Bills, Tax Collected).
* Cash vs. UPI vs. Card breakdown.
* Top-selling dishes leaderboard.

---

## 🚀 How to Run

### Main Billing Station (Windows PC)
1. **Desktop App Mode (Recommended):**
   * Double-click **`Launch_Desktop_App.bat`** (or **`Petpooja_POS.vbs`** for silent background startup).
   * It will automatically launch the server and open the dedicated Desktop POS application window!
2. **Create Desktop Shortcut:**
   * Double-click **`create_desktop_shortcut.bat`** to create a **"Shansara POS"** shortcut directly on your Windows Desktop!

### Mobile Captain App (Waiter's Phone)
1. Ensure the phone is connected to the same Wi-Fi / Ethernet router.
2. Open Chrome/Safari and go to:
   ```
   http://<YOUR_LAN_IP>:8000/captain
   ```
   *(Or just scan the QR code from the top bar of the Main Billing Station!)*
3. Tap **"📲 Install Shansara Captain App"** to install it directly onto the phone's home screen.

---

## 📁 Repository Structure

```
shansara-pos/
├── server.py                   # FastAPI backend + WebSockets + ESC/POS driver + QR generator
├── database.py                 # SQLite schema + menu/tables seeder
├── pos.db                      # Local SQLite database
├── Launch_Desktop_App.bat      # Windows Desktop App launcher (Dedicated window mode)
├── Petpooja_POS.vbs            # Silent background Windows launcher
├── create_desktop_shortcut.bat # Places 1-click icon on Windows Desktop
├── start_pos.bat               # Console server launcher
├── static/
│   ├── logo.png                # Official 11 TO 11 Brand Logo
│   ├── pos.html                # Main Billing Station UI
│   ├── captain.html            # Captain Mobile Web App (PWA)
│   ├── kitchen.html            # Kitchen Display System (KDS)
│   ├── admin.html              # Reports & Settings Dashboard
│   ├── manifest.json           # Mobile PWA manifest
│   ├── sw.js                   # Service Worker for offline mobile app
│   └── icons/                  # 192x192 & 512x512 app icons
└── android/                    # Native Android Studio Project for APK compilation
    ├── app/
    │   ├── build.gradle
    │   └── src/main/java/com/petpooja/captain/MainActivity.java
    └── README.md
```