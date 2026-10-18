import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess

# Safe console reconfigure
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure base directory is in sys.path
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import app, get_local_ip
import uvicorn

def is_port_in_use(port=8000, host='127.0.0.1'):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def open_desktop_window(url="http://localhost:8000"):
    # Wait until server responds on port 8000 (up to 8 seconds)
    for _ in range(32):
        if is_port_in_use(8000):
            break
        time.sleep(0.25)
    
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
    print(" [*] Main Cashier POS Station : http://localhost:8000")
    print(f" [*] Same Wi-Fi LAN Address   : http://{local_ip}:8000")
    print(f" [*] Captain Mobile App       : http://{local_ip}:8000/captain")
    print(f" [*] Kitchen Display (KDS)    : http://{local_ip}:8000/kitchen")
    print(f" [*] Admin & Daily Reports    : http://{local_ip}:8000/admin")
    print("=" * 68)
    print(" [OK] Connect any waiter's phone to the SAME WI-FI and open:")
    print(f"      http://{local_ip}:8000/captain")
    print("=" * 68)

    # Check if port 8000 is already active
    if is_port_in_use(8000):
        print(" [i] Shansara POS server is already running on port 8000.")
        print(" [i] Launching Desktop App Window...")
        open_desktop_window("http://localhost:8000")
        print(" [i] Window opened. You can minimize this launcher.")
        time.sleep(2)
        sys.exit(0)

    # Launch desktop window in background thread
    threading.Thread(target=open_desktop_window, daemon=True).start()

    # Run uvicorn on 0.0.0.0 so all Wi-Fi clients can connect
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    except Exception as e:
        print(f"Server encounter: {e}")
        time.sleep(4)
