# Shansara Captain Android App

This is the native Android Studio project for the **Shansara Captain Mobile App**.

---

## 📱 Option 1: Instant 1-Tap Direct Install (No Android Studio required!)

Any waiter or captain with an Android phone or iPhone can install the app directly on the same Wi-Fi:

1. Connect the phone to the restaurant Wi-Fi network.
2. Open Chrome (or Safari on iOS) and navigate to `http://<YOUR_LAN_IP>:8000/captain` (or scan the QR code from the Billing Counter screen).
3. Tap the **"📲 Install Shansara Captain App"** banner at the top of the screen (or tap Chrome Menu ⋮ -> **"Install app"** / **"Add to Home screen"**).
4. Android will automatically package and install it as a native, full-screen mobile app with the official **11 TO 11 Shansara** icon on the phone's home screen and app launcher!

---

## 🛠️ Option 2: Build Native Android APK (`.apk`)

If you want to compile an actual `.apk` file for Sunmi handheld POS terminals, Android tablets, or side-loading:

1. Open **Android Studio**.
2. Select **Open an Existing Project** and choose the `android` directory in this repository.
3. Let Gradle sync dependencies.
4. Go to **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
5. Once built, Android Studio will output `app-debug.apk` / `Shansara_Captain.apk`.
6. Copy the `.apk` file to any phone or terminal and install it.
7. On first launch, enter the Billing Station IP (e.g. `192.168.1.5:8000`) and it will connect and stay synced in real-time over the same Wi-Fi!
