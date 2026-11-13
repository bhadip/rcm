# RCM Reliability Dashboard

A secure, offline-capable Reliability-Centered Maintenance (RCM) dashboard designed for Subject Matter Experts (SMEs). It visualizes component failure modes, reliability curves, and failure rates directly from encrypted Excel data, governed by CADEN licensing.

## 🌟 Key Features
- **Zero-Touch Startup:** No password prompts. Embedded data auto-decrypts and loads instantly.
- **CADEN License Governance:** Integrated hardware fingerprinting, smart offline recovery, and real-time User/License display in the footer.
- **Interactive P&ID Diagram:** SVG overlay allows precise clicking of components.
- **Dynamic Time Slider:** Adjust the "Current Day" to see real-time color changes (Green/Yellow/Red) across the entire system.
- **Maintenance Date Tracking:** Record last maintenance dates per failure mode; the system automatically calculates effective days elapsed.
- **Smart Log Import/Export:** Export/import maintenance logs at both system level and component level.
- **Anti-Flash Rendering:** Prevents UI flashing during CADEN license verification.

## 📁 Project Structure
- `doc/`: Project documentation and revision history.
- `build_data.py`: Python script to parse Excel and encrypt data (generates `build_info.json`).
- `embed_data.py`: Python script to inject encrypted data and dynamic metadata into HTML.
- `integrate_caden.py`: Python script to inject CADEN licensing script.
- `RCM 4-2.xlsx`: The latest SME-verified Excel data source.
- `RCM Dashboard/`: The final distribution folder (contains `dashboard.html`, `diagram.jpg`, `crypto-js.min.js`, `chart.umd.js`).

## ⚡ Quick Start
1. Ensure `crypto-js.min.js` and `chart.umd.js` are in the same folder as `dashboard.html`.
2. Double-click `dashboard.html` to open it in Chrome, Safari, or Edge.

## 🛠️ Developer Build Process
1. Place scripts and the Excel file in the **Setup** folder.
2. Run: `python3 build_data.py "RCM 4-2.xlsx"` (Generates `data.enc` and `build_info.json`)
3. Run: `python3 integrate_caden.py`
4. Run: `python3 embed_data.py "RCM 4-2.xlsx"` (Generates final `dashboard.html` with real metadata)

## ⌨️ Hidden Shortcuts
- **Calibration Mode:** Press `Ctrl + Shift + L` (Windows/Linux) or `Cmd + Shift + L` (Mac) to toggle the SVG overlay calibration panel.

---
&copy; 2026 BCore &middot; Brawijaya Center Of Reliability & Integrity Excellences
Powered by Prasanti Advisory, Singapore
