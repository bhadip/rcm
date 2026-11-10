# RCM Reliability Dashboard

A secure, offline-capable Reliability-Centered Maintenance (RCM) dashboard designed for Subject Matter Experts (SMEs). It visualizes component failure modes, reliability curves, and failure rates directly from encrypted Excel data.

## 🌟 Key Features
- **100% Offline**: Runs entirely in the browser using local files.
- **CADEN License Governance**: Integrated hardware fingerprinting, anti-clock-skew validation, secure admin resets, and smart offline recovery.
- **Interactive P&ID Diagram**: SVG overlay allows precise clicking of components.
- **Dynamic Time Slider**: Adjust the "Current Day" to see real-time color changes (Green/Yellow/Red).
- **Maintenance Date Tracking**: Record last maintenance dates per failure mode; the system automatically calculates effective days elapsed.
- **Smart Log Import/Export**: Export/import maintenance logs at both system level and component level.
- **Anti-Flash Rendering**: Prevents UI flashing during CADEN license verification.

## 📁 Project Structure
- `doc/`: Project documentation and revision history.
- `build_data.py`: Python script to parse Excel and encrypt data.
- `embed_data.py`: Python script to inject encrypted data into HTML.
- `integrate_caden.py`: Python script to inject CADEN licensing script.
- `caden_script.txt`: The CADEN governance script source.
- `RCM 2.xlsx`: The latest SME-verified Excel data source.
- `RCM Dashboard/`: The final distribution folder (contains `dashboard.html`, `diagram.jpg`, `crypto-js.min.js`, `chart.umd.js`).

## ⚡ Quick Start
1. Ensure `crypto-js.min.js` and `chart.umd.js` are in the same folder as `dashboard.html`.
2. Double-click `dashboard.html` to open it in Chrome, Safari, or Edge.

---
&copy; 2026 BCore &middot; Brawijaya Center Of Reliability & Integrity Excellences
Powered by Prasanti Advisory, Singapore
