---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Arial', sans-serif;
    padding: 40px;
  }
  h1 {
    color: #2c3e50;
  }
  h2 {
    color: #e67e22;
    border-bottom: 2px solid #e67e22;
    padding-bottom: 10px;
  }
  table {
    font-size: 16px;
    width: 100%;
  }
  th {
    background-color: #ecf0f1;
    color: #2c3e50;
  }
---

# CrowdSense
## Privacy-Preserving Crowd Density & Demographics Monitor
### Edge-Based WiFi Sensing with Web Serial Verification

**Team Members:**
[Your Name] (Reg: 23BCE1230)
[Teammate Name]

**Course:**
C1 DA1 – IoT Mini Project

---

## Overview

* **Core Concept:** A privacy-first IoT system that estimates crowd density in real-time by passively sniffing WiFi/BLE signals (Probe Requests).
* **Technology Stack:** Utilizes **ESP32** in promiscuous mode for packet capture and **Next.js** for visualization.
* **Key Innovation:** Uses **Web Serial API** for zero-latency, offline data transmission, eliminating cloud dependencies during demos.
* **Differentiation:** Unlike camera-based systems, CrowdSense is non-intrusive, anonymous (hashed data), and capable of sensing through walls.

---

## Objective

* **Design:** To create a low-cost (<$10), portable crowd monitoring system using off-the-shelf ESP32 hardware.
* **Privacy:** To implement **Edge-Based Hashing (SHA-256)**, ensuring raw MAC addresses never leave the microcontroller.
* **Verification:** To solve the common "Fake Data" issue in IoT projects by using a direct Serial stream to prove real-time responsiveness.
* **Analytics:** To differentiate between "Active Users" (High Bandwidth/Streaming) and "Passive Users" (Idle) via packet type analysis.
* **Utility:** Providing actionable insights for HVAC automation and smart building occupancy without facial recognition.

---

## Introduction

* **Context:** Efficient crowd management is critical for smart cities, emergency response, and retail analytics.
* **The Problem:** Current solutions have major flaws:
    * **Cameras:** High cost, Line-of-Sight constraints, and severe privacy violations.
    * **PIR Sensors:** Can detect motion but cannot count static people.
* **The Solution:** Leveraging the "Digital Footprint" of smartphones. Devices constantly broadcast probe requests to find networks.
* **The Challenge:** **MAC Randomization** in modern OSs (iOS/Android) hides identity.
* **Our Approach:** We focus on **Aggregate Signal Analysis (RSSI)** and **Packet Density** rather than tracking individual users.

---

## Architecture Diagram

The system follows a 3-stage linear data pipeline:

**1. Sensing Layer (Edge Node)**
* **Hardware:** ESP32 WROOM
* **Function:** Promiscuous Sniffing (2.4GHz) -> RSSI Filtering (-90dBm cutoff) -> SHA-256 Hashing.

**2. Transmission Layer (Wired)**
* **Medium:** USB Serial (UART)
* **Protocol:** JSON Stream @ 115200 baud.
* **Benefit:** 0ms Latency, Air-gapped from internet.

**3. Application Layer (Host)**
* **Hardware:** Dell Laptop (Arch Linux)
* **Software:** Next.js Dashboard.
* **Logic:** Receives JSON -> Applies "Device Decay" (60s Debounce) -> Visualizes via Recharts.

---

## Components Used

**Hardware Components:**
1.  **ESP32 Development Board (DOIT DevKit V1):** The primary microcontroller and WiFi radio.
2.  **Host Machine:** Laptop (Intel i3-4005U, 8GB RAM) running Arch Linux.
3.  **USB Data Cable:** Provides power and serial communication interface.

**Software Stack:**
1.  **Firmware:** C++ (Arduino Framework) using `esp_wifi.h` libraries.
2.  **Frontend:** React / Next.js (Localhost).
3.  **Visualization:** `recharts` for live plotting and `navigator.serial` for data fetching.
4.  **Validation Tool:** `airodump-ng` (Linux suite) for ground-truth comparison.

---

## Connectivity Diagram

* **Physical Setup:**
    * The **ESP32** is connected directly to the **Laptop USB Port**.
    * No external sensors (DHT/PIR) are required; the **WiFi Antenna** on the PCB acts as the sensor.
* **Signal Flow:**
    1.  Smartphones emit **WiFi Probe Packets**.
    2.  ESP32 Antenna captures packets (Air Interface).
    3.  ESP32 processes and sends JSON via **USB Serial**.
    4.  Browser (Next.js) reads Serial Port and renders graphs.

---

## Novelty (Innovation)

1.  **Web Serial Integration:** Removes "Cloud Lag." The dashboard updates instantly, allowing for "Geiger Counter" demos where graphs react to physical proximity immediately.
2.  **Edge-Based Privacy:** We perform **SHA-256 hashing** on the chip. Raw MAC addresses are never stored or transmitted.
3.  **Smart "Device Decay" Logic:** Implemented a software-based "Grace Period" (60s) to handle the oscillation caused by modern phones sleeping to save battery.
4.  **Packet Volume Analysis:** Instead of just counting people, we analyze "Packet Density" to distinguish between a room of idle people vs. active data users.

---

## Related Work (2024-2025)

| Title | Authors | Year | Methodology | Limitation / Gap |
| :--- | :--- | :--- | :--- | :--- |
| **CrowdWatch: Privacy-Preserving** | *IEEE IoT Journal* | 2025 | WiFi multi-modal fingerprints. | Requires complex server-side processing. |
| **Integrated Intelligent Crowd Control** | *IEEE Access* | 2025 | Computer Vision + IoT. | High cost; Privacy concerns with cameras. |
| **YOLO-CROWD: Smart Monitoring** | *Auto. & Comp. Sci* | 2024 | IP Cameras + YOLO-Ghost. | Requires Line-of-Sight; fails in dark. |
| **Streamline Intelligent Monitoring** | *MDPI Sensors* | 2024 | Raspberry Pi Clusters. | Hardware is expensive/bulky compared to ESP32. |
| **IoT-Based Crowd Monitoring** | *ResearchGate* | 2024 | PIR Sensors. | Cannot count static people; low accuracy. |

---

## Related Work (2021-2023)

| Title | Authors | Year | Methodology | Limitation / Gap |
| :--- | :--- | :--- | :--- | :--- |
| **Affordable Real-Time Surveillance** | *IJSSE* | 2023 | ESP32-CAM + Twilio. | Focuses on photos, not anonymous counting. |
| **Estimating Indoor Crowd Density** | *Frontiers IoT* | 2022 | Passive WiFi probing. | High data oscillation; no verification. |
| **Device-Free Crowd Counting** | *MDPI Electronics* | 2021 | CSI Doppler Spectrum. | High computational load for MCU. |
| **Passive WiFi Sensing** | *PMC* | 2023 | WiFi + Cellular Data. | High latency; dependent on Telco data. |
| **Review of Crowd Management** | *Springer* | 2021 | Survey of IoT methods. | General overview; no solution for randomization. |
