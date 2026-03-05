#!/usr/bin/env python3
"""
PAX Counter — Serial → WebSocket bridge + HTTP server
Usage: python3 server.py /dev/ttyUSB0
"""

import sys, json, time, serial, asyncio, threading
import http.server, socketserver
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
SERIAL_PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BAUD        = 115200
WS_PORT     = 8765
HTTP_PORT   = 8080
DEVICE_TTL  = 30   # seconds until a device is considered gone

# ── Shared state ────────────────────────────────────────────────────────────
devices      = {}          # mac → {rssi, ch, last_seen}
devices_lock = threading.Lock()
ws_clients   = set()

# ── Serial thread ───────────────────────────────────────────────────────────
def serial_thread():
    while True:
        try:
            with serial.Serial(SERIAL_PORT, BAUD, timeout=1) as ser:
                print(f"[serial] Connected → {SERIAL_PORT}")
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw:
                        continue
                    try:
                        d = json.loads(raw)
                        mac = d.get("mac", "")
                        if mac and mac != "FF:FF:FF:FF:FF:FF":
                            with devices_lock:
                                devices[mac] = {
                                    "rssi":      d.get("rssi", -100),
                                    "ch":        d.get("ch", 0),
                                    "last_seen": time.time(),
                                }
                    except json.JSONDecodeError:
                        pass
        except serial.SerialException as e:
            print(f"[serial] {e} — retrying in 2s")
            time.sleep(2)

# ── Helpers ─────────────────────────────────────────────────────────────────
def snapshot():
    """Return devices sorted by RSSI desc, pruning stale ones."""
    now = time.time()
    with devices_lock:
        stale = [m for m, v in devices.items() if now - v["last_seen"] > DEVICE_TTL]
        for m in stale:
            del devices[m]
        return sorted(
            [{"mac": k, "rssi": v["rssi"], "ch": v["ch"]} for k, v in devices.items()],
            key=lambda x: x["rssi"], reverse=True,
        )

# ── WebSocket handler ────────────────────────────────────────────────────────
async def ws_handler(ws):
    ws_clients.add(ws)
    print(f"[ws] client connected  ({len(ws_clients)} total)")
    try:
        await ws.wait_closed()
    finally:
        ws_clients.discard(ws)
        print(f"[ws] client left  ({len(ws_clients)} total)")

async def broadcaster():
    global ws_clients        # ← add this

    """Push the device list to all clients every 500ms."""
    while True:
        await asyncio.sleep(0.5)
        if not ws_clients:
            continue
        payload = json.dumps(snapshot())
        dead = set()
        for ws in ws_clients:
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        ws_clients -= dead

# ── HTTP server (serves index.html) ─────────────────────────────────────────
class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def http_thread():
    here = Path(__file__).parent
    class H(SilentHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(here), **kw)
    with socketserver.TCPServer(("", HTTP_PORT), H) as httpd:
        print(f"[http] http://localhost:{HTTP_PORT}")
        httpd.serve_forever()

# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    import websockets

    # Serial
    threading.Thread(target=serial_thread, daemon=True).start()

    # HTTP
    threading.Thread(target=http_thread, daemon=True).start()

    print(f"[ws]   ws://localhost:{WS_PORT}")
    async with websockets.serve(ws_handler, "localhost", WS_PORT):
        await broadcaster()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[bye]")
