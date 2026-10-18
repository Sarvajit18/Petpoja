import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess

# Ensure base directory is in sys.path
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import app, get_local_ip
import uvicorn

def open_desktop_window(url="http://localhost:8000"):
    time.sleep(1.8) # Wait for uvicorn to bind port
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    
    # 1. Try Edge App Mode (Standalone borderless app window)
    for p in edge_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={url}", "--window-size=1300,880"])
                return
            except Exception:
                pass

    # 2. Try Chrome App Mode
    for p in chrome_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={url}", "--window-size=1300,880"])
                return
            except Exception:
                pass

    # 3. Default browser fallback
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 68)
    print("         >>> SHANSARA RESTAURANT POS (WINDOWS STANDALONE) <<<")
    print("=" * 68)
    print(f" [*] Main Cashier POS Station : http://localhost:8000")
    print(f" [*] Same Wi-Fi LAN Address   : http://{local_ip}:8000")
    print(f" [*] Captain Mobile App       : http://{local_ip}:8000/captain")
    print(f" [*] Kitchen Display (KDS)    : http://{local_ip}:8000/kitchen")
    print(f" [*] Admin & Daily Reports    : http://{local_ip}:8000/admin")
    print("=" * 68)
    print(f" [✓] Connect any waiter's phone to the SAME WI-FI and open:")
    print(f"     http://{local_ip}:8000/captain")
    print("=" * 68)
    print(" Press Ctrl+C in this console to shut down the server safely.")
    print("=" * 68)

    # Launch desktop window
    threading.Thread(target=open_desktop_window, daemon=True).start()

    # Run uvicorn on 0.0.0.0 so all Wi-Fi clients can connect
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
