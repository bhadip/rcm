# RCM Reliability Dashboard

A secure, offline-capable Reliability-Centered Maintenance (RCM) dashboard designed for Subject Matter Experts (SMEs). It visualizes component failure modes, reliability curves, and failure rates directly from encrypted Excel data without requiring a database or internet connection.

## 🌟 Key Features
- **100% Offline**: Runs entirely in the browser using local files.
- **Military-Grade Security**: Data is encrypted using AES-256. The raw Excel file is never exposed to the end-user.
- **Interactive P&ID Diagram**: SVG overlay allows precise clicking of components (ESDV-101, V-101, GT-101, etc.).
- **Dynamic Time Slider**: Adjust the "Current Day" to see real-time color changes (Green/Yellow/Red) based on Weibull reliability thresholds.
- **Advanced Charting**: Logarithmic reliability charts with dynamic target intersection markers (Red crosshairs) and current day indicators (Yellow dashed lines).
- **Maintenance Date Tracking**: Record last maintenance dates per failure mode; the system automatically calculates effective days elapsed since maintenance.
- **Smart Log Import/Export**: Export/import maintenance logs at both system level (all components) and component level (single component).

## 📁 Project Structure
- `dashboard.html`: The main, self-contained application file (includes embedded encrypted data).
- `diagram.jpg`: The background P&ID image.
- `crypto-js.min.js`: Library for in-memory AES decryption.
- `chart.umd.js`: Chart.js library for rendering reliability graphs.
- `*.md`: Project documentation.

## ⚡ Quick Start
1. Ensure `crypto-js.min.js` and `chart.umd.js` are in the same folder as `dashboard.html`.
2. Double-click `dashboard.html` to open it in Chrome, Safari, or Edge.
3. The dashboard will automatically decrypt and load the embedded data.

## 📊 Version
Current version: **v0.5.2**

---
*© 2026 BCore · Brawijaya Center Of Reliability & Integrity Excellences*
*Powered by Prasanti Advisory*
