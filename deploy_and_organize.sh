#!/bin/bash

# ==============================================================================
# RCM Dashboard Deployment, Documentation & Organization Script
# Version: 3.0.0
# ==============================================================================

# Define Paths
SETUP_DIR="/Users/Bambang/Library/CloudStorage/OneDrive-Personal/BCore/Standalone Dashboard/RCM Dashboard Setup"
RUN_DIR="/Users/Bambang/Library/CloudStorage/OneDrive-Personal/BCore/Standalone Dashboard/RCM Dashboard"
REPO_URL="git@github.com:bhadip/rcm.git"

echo "🚀 Starting RCM Dashboard Organization & Deployment..."

# Ensure directories exist
if [ ! -d "$SETUP_DIR" ]; then
    echo "❌ Error: Setup directory not found."
    exit 1
fi
if [ ! -d "$RUN_DIR" ]; then
    echo "❌ Error: Run directory not found. Please build the dashboard first."
    exit 1
fi

# ==============================================================================
# 1. ORGANIZE FILES
# ==============================================================================
echo "📂 Organizing file structure..."

# Create doc folder in Setup directory
mkdir -p "$SETUP_DIR/doc"

# Clean up Run directory: Remove any markdown files so it only contains installation files
find "$RUN_DIR" -type f -name "*.md" -delete
echo "   🧹 Cleaned markdown files from RCM Dashboard folder."

# ==============================================================================
# 2. GENERATE DOCUMENTATION (into Setup/doc folder)
# ==============================================================================
echo "📝 Generating Documentation..."

# --- README.md ---
cat << 'EOF' > "$SETUP_DIR/doc/README.md"
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
EOF

# --- REQUIREMENTS.md ---
cat << 'EOF' > "$SETUP_DIR/doc/REQUIREMENTS.md"
# System Requirements & Specifications

## Functional Requirements
1. **Offline Operation**: The application must run locally without any internet dependency.
2. **Data Security**: The Excel data must be converted to an AES-256 encrypted JSON format before deployment.
3. **CADEN Governance**: Must enforce hardware binding, clock integrity, and remote revocation capabilities.
4. **Level 1 (Diagram)**: Display a JPG diagram with a transparent, clickable SVG overlay.
5. **Level 2 (Table)**: Display dynamic Failure Modes with a "Last Maintenance Date" column.
6. **Level 3 (Charts)**: Logarithmic reliability charts with dynamic target intersection markers (Red crosshairs) and current day indicators (Yellow dashed lines).

## Non-Functional Requirements
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, CryptoJS, Chart.js, Python 3.x.
- **Performance**: Chart updates via slider must be instantaneous.
- **Compatibility**: Must run on modern desktop browsers via the `file://` protocol.
EOF

# --- ARCHITECTURE.md ---
cat << 'EOF' > "$SETUP_DIR/doc/ARCHITECTURE.md"
# Architecture & Design

## System Overview
The system uses a **Build-Time Encryption / Run-Time Decryption** architecture combined with **CADEN Client-Side Governance**.

## Data Flow
1. **Source**: SME updates `RCM 2.xlsx` with Failure Modes, Weibull parameters, and Target thresholds.
2. **Build Phase**: `build_data.py` dynamically parses sheets, validates consistency (FM count == Target count == Data blocks), and encrypts the JSON payload using AES-256-CBC.
3. **Embed Phase**: `embed_data.py` injects the encrypted string into `index.html`.
4. **Run Phase**: `dashboard.html` decrypts the data in memory. CADEN script verifies hardware fingerprint and license status before revealing the UI (`opacity: 1`).

## Security Model
- **At Rest**: Data is AES-256 encrypted.
- **In Memory**: Decrypted only in the browser's JavaScript runtime.
- **CADEN Governance**: Uses persistent UUIDs, canvas fingerprinting, and stealth WebSocket agents for remote revocation.
EOF

# --- INSTALLATION_AND_OPERATIONS.md ---
cat << 'EOF' > "$SETUP_DIR/doc/INSTALLATION_AND_OPERATIONS.md"
# Installation, Operations & Troubleshooting

## 🛠️ For Developers (Build Environment)
**Prerequisites**: Python 3.x, `openpyxl`, `pycryptodome`.

`pip3 install openpyxl pycryptodome`

**Build Process**:
1. Place scripts and `RCM 2.xlsx` in the **Setup** folder.
2. Run: `python3 build_data.py "RCM 2.xlsx"`
3. Run: `python3 integrate_caden.py`
4. Run: `python3 embed_data.py`

## 🚀 For End-Users (Operations)
1. Ensure the **RCM Dashboard** folder contains: `dashboard.html`, `diagram.jpg`, `crypto-js.min.js`, and `chart.umd.js`.
2. Double-click `dashboard.html`.

## 🔧 Troubleshooting
| Issue | Solution |
| :--- | :--- |
| **"Data: Not Loaded"** | Ensure `crypto-js.min.js` is in the same folder. |
| **CADEN Lockdown** | Clear browser localStorage or contact admin for secure reset. |
| **"Â" in Footer** | Ensure `embed_data.py` v0.1.7+ is used (uses HTML entities). |
| **Git Push Fails** | Run `ssh-add ~/.ssh/id_rsa` to add key to agent. |
EOF

# --- REVISION_HISTORY.md ---
cat << 'EOF' > "$SETUP_DIR/doc/REVISION_HISTORY.md"
# Revision History

## Application Versions

### v0.5.8 (Current)
- Fixed "Â" garbage characters in footer by using HTML entities (`&copy;`, `&middot;`) and `innerHTML`.
- Ensured CADEN script has full control over UI visibility (no race conditions).

### v0.5.7
- Removed external fade-in trigger to prevent bypassing CADEN lockdown screens.

### v0.5.6
- Added anti-flash CSS (`body { opacity: 0; }`) to hide UI during license verification.

### v0.5.5
- Cleaned index.html to ensure proper CADEN script version detection and replacement.

### v0.5.4
- Integrated CADEN v0.4.0-proposal (Secure admin resets, smart fingerprint recovery, revocation awareness).

### v0.5.3
- Implemented Concept 1 "Reliability Shield" Gear Logo in header and favicon.

### v0.5.2
- Fixed smart import compatibility for System vs Component logs.

### v0.5.1
- Added Export/Import Log buttons at Level 1 (System) and Level 2 (Component).

### v0.5.0
- Added "Last Maintenance Date" column and effective day calculation logic.

### v0.4.x
- Dynamic sheet processing, consistency checks, and Excel filename arguments.

## Build Script Versions
- `build_data.py`: v0.4.5 (Strict 3-column data block validation)
- `embed_data.py`: v0.1.7 (HTML entity branding fix)
- `integrate_caden.py`: Latest (CADEN v0.3.0+ support)
EOF

echo "✅ Documentation generated in doc/ folder."

# ==============================================================================
# 3. GIT PUSH TO GITHUB (SSH)
# ==============================================================================
echo "🔄 Initializing Git and pushing to GitHub..."

cd "$SETUP_DIR" || exit

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# Set or update remote URL to SSH
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

# Add all files (scripts, excel, doc folder, and the RCM Dashboard distribution folder)
git add .

# Commit with a descriptive message
git commit -m "chore: reorganize repo structure, update docs to v0.5.8, and prepare for distribution

- Moved all documentation to 'doc/' subfolder
- Cleaned 'RCM Dashboard/' folder to contain ONLY installation files (dashboard.html, diagram.jpg, JS libs)
- Updated REVISION_HISTORY.md with v0.5.6 to v0.5.8 CADEN and branding fixes
- Ensured all source codes (build_data.py, embed_data.py, integrate_caden.py, caden_script.txt, RCM 2.xlsx) are tracked
- Fixed footer encoding issues using HTML entities in embed_data.py v0.1.7"

# Push to GitHub
echo "⬆️ Pushing to $REPO_URL ..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 Deployment successful! Repository is fully organized and live on GitHub."
    echo "📦 The 'RCM Dashboard' folder is now ready to be zipped and sent to users."
else
    echo "⚠️ Push failed. Ensure your SSH key is added to ssh-agent:"
    echo "   Run: ssh-add ~/.ssh/id_rsa (or your specific key)"
fi