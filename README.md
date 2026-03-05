# PAX Counter 📡

A real-time crowd estimation tool using an ESP32 in promiscuous mode to passively detect WiFi probe requests from nearby devices. Displays a live radar on a local web dashboard.

```
Phone/Device  →  [Probe Request]  →  ESP32  →  [JSON/Serial]  →  Python Server  →  Browser Radar
```

---

## How It Works

When a phone scans for WiFi networks, it broadcasts **probe request frames** — even without connecting to anything. The ESP32 listens to all of these passively (promiscuous mode), extracts the source MAC and signal strength (RSSI), and streams them as JSON over serial. A Python server bridges that to a WebSocket, and a browser frontend renders a live radar sorted by signal strength.

> **Note on MAC Randomization:** iOS 14+ and Android 10+ send randomized MACs during probe bursts. The server clusters MACs by RSSI + time window to deduplicate these into a single device entry.

---

## Hardware

- ESP32 WROOM module (any ESP32 dev board works)
- USB cable (for flashing + serial data)
- No extra hardware needed for the basic scanner

---

## Project Structure

```
IoT-Paxcounter/
├── paxscanner/
│   └── paxscanner.ino   # ESP32 firmware
├── server.py            # Serial → WebSocket + HTTP server
├── index.html           # Radar frontend
└── README.md
```

---

## Setup & Installation

### Prerequisites

You need:
- [arduino-cli](https://arduino.github.io/arduino-cli/)
- Python 3.8+
- ESP32 core for arduino-cli

---

### Linux (Arch / Debian / Ubuntu)

#### 1. Install arduino-cli

**Arch:**
```bash
yay -S arduino-cli
# or use the official installer:
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

**Debian/Ubuntu:**
```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/
```

#### 2. Add ESP32 core

```bash
arduino-cli config init
arduino-cli config add board_manager.additional_urls \
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

#### 3. Serial port permissions

**Arch** (group is `uucp`):
```bash
sudo usermod -aG uucp $USER
newgrp uucp   # apply without relogging
```

**Debian/Ubuntu** (group is `dialout`):
```bash
sudo usermod -aG dialout $USER
newgrp dialout
```

#### 4. Flash the ESP32

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 paxscanner/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 paxscanner/
```

Verify it's working:
```bash
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200
# You should see JSON lines like: {"mac":"AA:BB:CC:DD:EE:FF","rssi":-67,"ch":6}
```

#### 5. Install Python dependencies

**Arch:**
```bash
sudo pacman -S python-pyserial python-websockets
```

**Debian/Ubuntu:**
```bash
pip3 install pyserial websockets
```

#### 6. Run the server

```bash
python3 server.py /dev/ttyUSB0
```

Open **http://localhost:8080** in your browser.

---

### macOS

#### 1. Install arduino-cli

```bash
brew install arduino-cli
```

#### 2. Add ESP32 core

```bash
arduino-cli config init
arduino-cli config add board_manager.additional_urls \
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

#### 3. Find your port

```bash
ls /dev/cu.*
# Usually something like /dev/cu.usbserial-0001 or /dev/cu.SLAB_USBtoUART
```

#### 4. Flash the ESP32

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 paxscanner/
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp32:esp32:esp32 paxscanner/
```

> If upload fails with a permissions error, you may need the CP210x or CH340 driver depending on your ESP32 board:
> - CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
> - CH340: https://www.wch-ic.com/downloads/CH341SER_MAC_ZIP.html

#### 5. Install Python dependencies

```bash
pip3 install pyserial websockets
```

#### 6. Run the server

```bash
python3 server.py /dev/cu.usbserial-0001
```

Open **http://localhost:8080** in your browser.

---

### Windows

#### 1. Install arduino-cli

Download the Windows binary from the [releases page](https://github.com/arduino/arduino-cli/releases) and add it to your PATH, or use winget:

```powershell
winget install ArduinoSA.CLI
```

#### 2. Add ESP32 core

```powershell
arduino-cli config init
arduino-cli config add board_manager.additional_urls https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

#### 3. Find your COM port

Open **Device Manager** → **Ports (COM & LPT)** — your ESP32 will show as `USB-SERIAL CH340 (COM3)` or similar. Note the COM number.

> If the device doesn't appear, install the driver:
> - CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
> - CH340: https://www.wch-ic.com/downloads/CH341SER_EXE.html

#### 4. Flash the ESP32

```powershell
arduino-cli compile --fqbn esp32:esp32:esp32 paxscanner/
arduino-cli upload -p COM3 --fqbn esp32:esp32:esp32 paxscanner/
```

Replace `COM3` with your actual port.

#### 5. Install Python dependencies

```powershell
pip install pyserial websockets
```

#### 6. Run the server

```powershell
python server.py COM3
```

Open **http://localhost:8080** in your browser.

---

## Radar Dashboard

The frontend shows:
- **Radar sweep** — devices blip when the sweep line passes over them
- **Distance from center** = signal strength (closer = stronger RSSI)
- **Color** — blush-pink for strong signals, pale-slate for weak
- **Sidebar** — live list of devices sorted by RSSI with a signal bar

Devices automatically expire after **30 seconds** of inactivity.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Path '/dev/ttyUSB0' is not readable` | Add user to `uucp`/`dialout` group, run `newgrp` |
| `No module named 'serial'` | Install `python-pyserial` via pacman/apt/pip |
| ESP32 not detected on Windows | Install CH340 or CP210x USB driver |
| Upload stuck at "Connecting..." | Hold the **BOOT** button on the ESP32 while uploading |
| No packets in monitor | Make sure there are WiFi devices nearby with WiFi enabled |
| Tons of duplicate MACs | This is iOS/Android MAC randomization — the server clusters them by RSSI |

---

## Limitations & Notes

- **MAC randomization** (iOS 14+, Android 10+) means one device can appear as multiple MACs. The server uses a time + RSSI clustering heuristic to deduplicate.
- Pax count is an **estimate**, not an exact count.
- Range depends on your environment — typically 10–30 meters indoors.
- This tool is passive and does not associate with or modify any network traffic.

---

## License

MIT
