#!/bin/bash

# ==============================================================================
# RCM Dashboard Deployment & Documentation Script
# Version: 1.0.0
# ==============================================================================

# Define Paths
SETUP_DIR="/Users/Bambang/Library/CloudStorage/OneDrive-Personal/BCore/Standalone Dashboard/RCM Dashboard Setup"
RUN_DIR="/Users/Bambang/Library/CloudStorage/OneDrive-Personal/BCore/Standalone Dashboard/RCM Dashboard"
REPO_URL="git@github.com:bhadip/rcm.git"

echo "🚀 Starting RCM Dashboard Deployment Process..."
echo "📂 Target Directory: $RUN_DIR"

# Ensure Run Directory exists
if [ ! -d "$RUN_DIR" ]; then
    echo "❌ Error: Run directory not found. Please build the dashboard first."
    exit 1
fi

cd "$RUN_DIR" || exit

# ==============================================================================
# 1. GENERATE DOCUMENTATION
# ==============================================================================
echo "📝 Generating Documentation..."

# --- README.md ---
cat << 'EOF' > README.md
# RCM Reliability Dashboard

A secure, offline-capable Reliability-Centered Maintenance (RCM) dashboard designed for Subject Matter Experts (SMEs). It visualizes component failure modes, reliability curves, and failure rates directly from encrypted Excel data without requiring a database or internet connection.

## 🌟 Key Features
- **100% Offline**: Runs entirely in the browser using local files.
- **Military-Grade Security**: Data is encrypted using AES-256. The raw Excel file is never exposed to the end-user.
- **Interactive P&ID Diagram**: SVG overlay allows precise clicking of components (ESDV-101, V-101, GT-101, etc.).
- **Dynamic Time Slider**: Adjust the "Current Day" to see real-time color changes (Green/Yellow/Red) based on Weibull reliability thresholds.
- **Advanced Charting**: Logarithmic reliability charts with dynamic target intersection markers (Red crosshairs) and current day indicators (Yellow dashed lines).

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

---
*© 2026 BCore · Brawijaya Center Of Reliability & Integrity Excellences*  
*Powered by Prasanti Advisory*
EOF

# --- REQUIREMENTS.md ---
cat << 'EOF' > REQUIREMENTS.md
# System Requirements & Specifications

## Functional Requirements
1. **Offline Operation**: The application must run locally without any internet dependency.
2. **Data Source**: Read data from an SME-verified Excel spreadsheet, not a live database.
3. **Data Security**: The Excel data must be converted to an AES-256 encrypted JSON format before deployment. End-users cannot view the raw calculation logic or formulas.
4. **Level 1 (Diagram)**: Display a JPG diagram with a transparent, clickable SVG overlay mapping to specific Component IDs.
5. **Level 2 (Table)**: Display a dynamic table of Failure Modes for the selected component, with status colors updating based on the global day slider.
6. **Level 3 (Charts)**: 
   - Display Reliability R(t) and Failure Rate charts.
   - X-axis for Reliability must be Logarithmic.
   - Draw a **Red dashed horizontal line** at Target R(t) and a **Red dashed vertical line** at the calculated Target Day, intersecting with a **Red 'X' marker**.
   - Draw **Yellow dashed lines** that dynamically follow the global slider's current day.

## Non-Functional Requirements
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, CryptoJS, Chart.js.
- **Performance**: Chart updates via slider must be instantaneous (no full redraw flashing).
- **Compatibility**: Must run on modern desktop browsers (Chrome, Edge, Safari) via the `file://` protocol.
EOF

# --- ARCHITECTURE.md ---
cat << 'EOF' > ARCHITECTURE.md
# Architecture & Design

## System Overview
The system uses a **Build-Time Encryption / Run-Time Decryption** architecture to protect SME intellectual property while maintaining a zero-dependency frontend.

## Data Flow
1. **Source**: SME updates `RCM 1-2.xlsx` with Failure Modes, Weibull parameters (b, η), and Target thresholds.
2. **Build Phase (`build_data.py`)**: 
   - Parses the Excel file, extracting metadata and time-series arrays.
   - Calculates exact Target Days using the Weibull formula: `t = η * (-ln(R))^(1/b)`.
   - Encrypts the resulting JSON payload using AES-256-CBC via `pycryptodome`.
3. **Embed Phase (`embed_data.py`)**: 
   - Injects the Base64-encoded encrypted string and obfuscated password directly into `index.html`.
   - Outputs a single, portable `dashboard.html` file.
4. **Run Phase (`dashboard.html`)**:
   - On load, the browser uses `crypto-js.min.js` to decrypt the embedded string in memory using the obfuscated password.
   - Vanilla JS renders the SVG overlay and binds click events.
   - Chart.js renders the curves. Slider movements only update specific dataset coordinates (`chart.update('none')`) to prevent UI flashing.

## Security Model
- **At Rest**: Data is AES-256 encrypted.
- **In Transit**: N/A (Offline).
- **In Memory**: Decrypted only in the browser's JavaScript runtime. The password is Base64 obfuscated in the source code to prevent casual viewing, though a determined reverse-engineer could extract it. For higher security, the SME can change the password in `embed_data.py` before building.
EOF

# --- INSTALLATION_AND_OPERATIONS.md ---
cat << 'EOF' > INSTALLATION_AND_OPERATIONS.md
# Installation, Operations & Troubleshooting

## 🛠️ For Developers (Build Environment)
**Prerequisites**: Python 3.x, `openpyxl`, `pycryptodome`.

`pip3 install openpyxl pycryptodome`

**Build Process**:
1. Place `build_data.py`, `embed_data.py`, and `RCM 1-2.xlsx` in the **Setup** folder.
2. Run the build script: `python3 build_data.py` (Generates `data.enc`).
3. Run the embed script: `python3 embed_data.py` (Generates `dashboard.html` in the Run folder).

## 🚀 For End-Users (Operations)
1. Ensure the **Run** folder contains: `dashboard.html`, `diagram.jpg`, `crypto-js.min.js`, and `chart.umd.js`.
2. Double-click `dashboard.html`. 
3. *Note*: If using Chrome, local file restrictions might block JS execution. If so, right-click the file -> "Open With" -> Safari, or use a local server like `python3 -m http.server`.

## 🔧 Troubleshooting
| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **"Data: Not Loaded"** (Red text) | `dashboard.html` was opened instead of the embedded version, or JS libraries are missing. | Ensure `crypto-js.min.js` is in the same folder. Open `dashboard.html`, not `index.html`. |
| **Charts are blank / No Red Lines** | Corrupted `data.enc` or mismatched Excel formatting. | Re-run `build_data.py` and check terminal output for `[MATCH]` confirmations. |
| **Slider doesn't change colors** | Missing `thresholds` data in JSON. | Ensure `build_data.py` v0.3.11+ is used, which correctly maps Target rows to Failure Modes. |
| **Git Push Fails (Permission Denied)** | SSH key not configured or added to ssh-agent. | Run `ssh-add ~/.ssh/id_rsa` (or your key name) and ensure the public key is in GitHub Settings. |
EOF

echo "✅ Documentation generated successfully."

# ==============================================================================
# 2. GIT PUSH TO GITHUB (SSH)
# ==============================================================================
echo "🔄 Initializing Git and pushing to GitHub..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# Set or update remote URL to SSH
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

# Add all files and commit
git add .
git commit -m "chore: update documentation and deploy v0.4.13"

# Push to GitHub
echo "⬆️ Pushing to $REPO_URL ..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 Deployment successful! Dashboard is now live on GitHub."
else
    echo "⚠️ Push failed. Ensure your SSH key is added to ssh-agent:"
    echo "   Run: ssh-add ~/.ssh/id_rsa (or your specific key)"
fi