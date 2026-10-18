import os
import sys
import socket
import logging
import threading
from datetime import datetime
import ctypes
from ctypes import wintypes

logger = logging.getLogger("printer_service")

# Windows Spooler Structures
class DOC_INFO_1(ctypes.Structure):
    _fields_ = [
        ("pDocName", wintypes.LPCWSTR),
        ("pOutputFile", wintypes.LPCWSTR),
        ("pDataType", wintypes.LPCWSTR)
    ]

def get_installed_windows_printers():
    """Retrieve list of printer names installed on Windows."""
    printers = []
    if sys.platform != "win32":
        return printers

    try:
        import subprocess
        cmd = 'powershell -NoProfile -Command "Get-Printer | Select-Object -ExpandProperty Name"'
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=5)
        for line in out.splitlines():
            name = line.strip()
            if name:
                printers.append(name)
    except Exception as e:
        logger.warning(f"Failed to query Get-Printer: {e}")
        # Fallback to win32 EnumPrinters via winspool
        try:
            winspool = ctypes.WinDLL("winspool.drv")
            # EnumPrinters flags: PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS = 0x02 | 0x04 = 6
            needed = wintypes.DWORD()
            returned = wintypes.DWORD()
            winspool.EnumPrintersW(6, None, 1, None, 0, ctypes.byref(needed), ctypes.byref(returned))
            if needed.value > 0:
                buf = ctypes.create_string_buffer(needed.value)
                winspool.EnumPrintersW(6, None, 1, buf, needed.value, ctypes.byref(needed), ctypes.byref(returned))
        except Exception:
            pass

    return printers

def print_raw_to_windows_printer(printer_name: str, raw_bytes: bytes, doc_name: str = "Shansara KOT"):
    """Send raw ESC/POS bytes directly to a Windows USB/spooler printer using winspool.drv."""
    if sys.platform != "win32":
        return False, "Windows spooler printing only available on Windows"

    try:
        winspool = ctypes.WinDLL("winspool.drv")
        h_printer = wintypes.HANDLE()

        if not winspool.OpenPrinterW(printer_name, ctypes.byref(h_printer), None):
            return False, f"Could not open printer '{printer_name}'. Make sure it is plugged in and turned on."

        try:
            doc_info = DOC_INFO_1(doc_name, None, "RAW")
            job_id = winspool.StartDocPrinterW(h_printer, 1, ctypes.byref(doc_info))
            if job_id <= 0:
                return False, "Could not start print document on Windows spooler."

            try:
                winspool.StartPagePrinter(h_printer)
                written = wintypes.DWORD()
                winspool.WritePrinter(h_printer, raw_bytes, len(raw_bytes), ctypes.byref(written))
                winspool.EndPagePrinter(h_printer)
            finally:
                winspool.EndDocPrinter(h_printer)

            return True, f"Sent {written.value} bytes to printer '{printer_name}'"
        finally:
            winspool.ClosePrinter(h_printer)

    except Exception as e:
        return False, f"Windows printing error: {e}"

def print_raw_to_network_printer(ip: str, port: int, raw_bytes: bytes, timeout: float = 3.0):
    """Send raw ESC/POS bytes over TCP network (Ethernet / Wi-Fi thermal printer)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, int(port)))
            s.sendall(raw_bytes)
        return True, f"Printed successfully to {ip}:{port}"
    except socket.timeout:
        return False, f"Connection to thermal printer at {ip}:{port} timed out."
    except Exception as e:
        return False, f"Network printer error ({ip}:{port}): {e}"

def build_escpos_kot(kot_number: int, table_name: str, captain_name: str, items: list, 
                     paper_width: str = "80mm", restaurant_name: str = "11-11 RESTAURANT"):
    """
    Format a clean, professional thermal receipt Kitchen Order Ticket (KOT) in ESC/POS.
    Supports standard 80mm (48 chars) and compact 58mm (32 chars).
    """
    is_58mm = (paper_width == "58mm")
    col_width = 32 if is_58mm else 48
    div = "-" * col_width

    buf = bytearray()

    # 1. Initialize Printer: ESC @
    buf.extend(b"\x1b\x40")

    # 2. Buzzer Chime on print: ESC B 2 2
    buf.extend(b"\x1b\x42\x02\x02")

    # 3. Header: Restaurant Name centered
    buf.extend(b"\x1b\x61\x01") # Center
    buf.extend(b"\x1b\x21\x08") # Emphasized / Bold
    buf.extend(f"{restaurant_name.upper()}\n".encode("ascii", errors="replace"))

    # 4. Large Bold KOT Ticket Title (Double Width/Height)
    buf.extend(b"\x1b\x21\x30") # Double width & height
    buf.extend(f"KOT #{kot_number}\n".encode("ascii", errors="replace"))

    # 5. Table Information
    buf.extend(b"\x1b\x21\x20") # Double width
    buf.extend(f"TABLE: {table_name}\n".encode("ascii", errors="replace"))

    # 6. Metadata: Date, Time, Captain
    buf.extend(b"\x1b\x21\x00") # Normal
    buf.extend(b"\x1b\x61\x00") # Left align
    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    buf.extend(f"{div}\n".encode("ascii"))
    buf.extend(f"Date   : {now_str}\n".encode("ascii", errors="replace"))
    buf.extend(f"Captain: {captain_name}\n".encode("ascii", errors="replace"))
    buf.extend(f"{div}\n".encode("ascii"))

    # 7. Column Headers
    if is_58mm:
        buf.extend(b"QTY  ITEM\n")
    else:
        buf.extend(b"QTY   ITEM NAME\n")
    buf.extend(f"{div}\n".encode("ascii"))

    # 8. Items
    total_qty = 0
    buf.extend(b"\x1b\x21\x08") # Bold for food names
    for it in items:
        qty = int(it.get("quantity", 1))
        name = str(it.get("item_name", "Dish"))
        notes = str(it.get("notes", "")).strip()
        total_qty += qty

        # Format line
        if is_58mm:
            line = f"{qty:2d}  {name}\n"
        else:
            line = f"{qty:2d}   {name}\n"
        buf.extend(line.encode("ascii", errors="replace"))

        # Kitchen Notes (Indented & distinct)
        if notes:
            note_line = f"     >> Note: {notes}\n"
            buf.extend(b"\x1b\x21\x00") # normal for note
            buf.extend(note_line.encode("ascii", errors="replace"))
            buf.extend(b"\x1b\x21\x08") # back to bold

    buf.extend(b"\x1b\x21\x00") # Normal
    buf.extend(f"{div}\n".encode("ascii"))
    buf.extend(f"TOTAL ITEMS ORDERED: {total_qty}\n".encode("ascii"))
    buf.extend(f"{div}\n".encode("ascii"))

    # 9. Footer: Feed and Full/Partial Cut
    buf.extend(b"\n\n\n\n")
    buf.extend(b"\x1d\x56\x00") # GS V 0 = Full cut
    buf.extend(b"\x1d\x56\x01") # GS V 1 = Partial cut fallback

    return bytes(buf)

def print_kot_ticket(kot_data: dict, printers: list):
    """
    Print KOT ticket to all active KOT printers in background thread.
    kot_data: {kot_number, table_name, captain_name, items}
    printers: list of printer dicts from database
    """
    def _worker():
        kot_num = kot_data.get("kot_number", 1)
        tbl = kot_data.get("table_name", "Counter")
        captain = kot_data.get("captain_name", "Staff")
        items = kot_data.get("items", [])

        # Filter printers assigned for KOT
        target_printers = [
            p for p in printers 
            if "kot" in p.get("assigned_for", "").lower() or "all" in p.get("assigned_for", "").lower()
        ]

        if not target_printers:
            logger.info("No printer assigned for KOT. Skipping physical print.")
            return

        for p in target_printers:
            paper = p.get("paper_width", "80mm") or "80mm"
            raw_bytes = build_escpos_kot(kot_num, tbl, captain, items, paper)

            conn_type = (p.get("connection_type") or "network").lower()
            if conn_type == "windows":
                win_name = p.get("windows_printer_name") or p.get("name")
                ok, msg = print_raw_to_windows_printer(win_name, raw_bytes, f"KOT #{kot_num} - {tbl}")
                logger.info(f"Windows KOT Print ({win_name}): ok={ok}, msg={msg}")
            else:
                ip = p.get("ip_address", "127.0.0.1")
                port = int(p.get("port", 9100) or 9100)
                ok, msg = print_raw_to_network_printer(ip, port, raw_bytes)
                logger.info(f"Network KOT Print ({ip}:{port}): ok={ok}, msg={msg}")

    # Launch asynchronous printing without blocking HTTP requests
    threading.Thread(target=_worker, daemon=True).start()

def execute_test_print(printer_config: dict):
    """Run an immediate synchronous test print on a specific printer configuration."""
    test_kot = {
        "kot_number": 99,
        "table_name": "Test Table 1",
        "captain_name": "Admin / Test",
        "items": [
            {"item_name": "Chicken Biryani", "quantity": 2, "notes": "Less spicy"},
            {"item_name": "Hyderabad Chicken Gravy", "quantity": 1, "notes": "Extra gravy"}
        ]
    }
    paper = printer_config.get("paper_width", "80mm") or "80mm"
    raw_bytes = build_escpos_kot(99, "TEST 1", "Admin", test_kot["items"], paper)

    conn_type = (printer_config.get("connection_type") or "network").lower()
    if conn_type == "windows":
        win_name = printer_config.get("windows_printer_name") or printer_config.get("name")
        return print_raw_to_windows_printer(win_name, raw_bytes, "Shansara Test KOT")
    else:
        ip = printer_config.get("ip_address", "127.0.0.1")
        port = int(printer_config.get("port", 9100) or 9100)
        return print_raw_to_network_printer(ip, port, raw_bytes)
