# Petpooja Captain Android App

This is the native Android Studio project for the **Petpooja Captain Mobile App**.

---

## 📱 Option 1: Instant 1-Tap PWA Install (No Android Studio required!)

Any waiter with an Android phone or iPhone can install the app directly:

1. Connect the phone to the restaurant Wi-Fi.
2. Open Chrome (or Safari on iOS) and navigate to `http://<YOUR_LAN_IP>:8000/captain` (or scan the QR code from the Billing Counter monitor).
3. Tap the **"📲 Install Petpooja Captain App"** banner at the top of the screen (or tap Chrome Menu ⋮ -> **"Install app"** / **"Add to Home screen"**).
4. The app installs as a native, full-screen mobile app with its own Petpooja icon on the Android launcher!

---

## 🛠️ Option 2: Build Native Android APK (`.apk`)

If you want an actual `.apk` file to install on Sunmi handheld POS terminals, Android tablets, or distribute directly:

1. Open **Android Studio**.
2. Select **Open an Existing Project** and choose the `petpooja-pos/android` directory.
3. Let Gradle sync.
4. Go to **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
5. Once built, copy the generated `.apk` file to your phone/terminal and install it.
6. When launched for the first time, it will prompt for the Billing Station IP (e.g. `192.168.1.5:8000`) and connect automatically!
