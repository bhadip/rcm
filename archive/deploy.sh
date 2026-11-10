#!/bin/bash

# ==============================================================================
# RCM Dashboard Deployment & Documentation Script
# Version: 2.0.0
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
EOF

# --- REQUIREMENTS.md ---
cat << 'EOF' > REQUIREMENTS.md
# System Requirements & Specifications

## Functional Requirements
1. **Offline Operation**: The application must run locally without any internet dependency.
2. **Data Source**: Read data from an SME-verified Excel spreadsheet, not a live database.
3. **Data Security**: The Excel data must be converted to an AES-256 encrypted JSON format before deployment. End-users cannot view the raw calculation logic or formulas.
4. **Level 1 (Diagram)**: Display a JPG diagram with a transparent, clickable SVG overlay mapping to specific Component IDs.
5. **Level 2 (Table)**: Display a dynamic table of Failure Modes for the selected component, with status colors updating based on the global day slider. Include a "Last Maintenance Date" column.
6. **Level 3 (Charts)**:
   - Display Reliability R(t) and Failure Rate charts.
   - X-axis for Reliability must be Logarithmic.
   - Draw a **Red dashed horizontal line** at Target R(t) and a **Red dashed vertical line** at the calculated Target Day, intersecting with a **Red 'X' marker**.
   - Draw **Yellow dashed lines** that dynamically follow the global slider's current day.
7. **Maintenance Date Logic**: When a maintenance date is entered, the effective day = slider day + (today - maintenance date). If no date is entered, assume 0 offset.
8. **Smart Log Import**: Component-level import must accept both system logs (extracting only the relevant component) and component logs.

## Non-Functional Requirements
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, CryptoJS, Chart.js, Python 3.x (build-time only).
- **Performance**: Chart updates via slider must be instantaneous (no full redraw flashing).
- **Compatibility**: Must run on modern desktop browsers (Chrome, Edge, Safari) via the `file://` protocol.
- **Data Validation**: Build script must verify consistency between Failure Mode count, Target row count, and data column blocks.

## Excel File Structure Requirements
- Header row must contain "Failure Mode" in Column B.
- Data starts immediately after the header row.
- Each Failure Mode must have a corresponding "Target" row in Column E.
- Time-series data blocks (Day, Reliability, Failure Rate) must start at Column L, with 3 columns per Failure Mode.
EOF

# --- ARCHITECTURE.md ---
cat << 'EOF' > ARCHITECTURE.md
# Architecture & Design

## System Overview
The system uses a **Build-Time Encryption / Run-Time Decryption** architecture to protect SME intellectual property while maintaining a zero-dependency frontend.

## Data Flow
1. **Source**: SME updates `RCM 1-2.xlsx` (or similar) with Failure Modes, Weibull parameters (b, η), and Target thresholds.
2. **Build Phase (`build_data.py`)**:
   - Dynamically detects all sheets (components) in the workbook.
   - Performs consistency checks:
     - Component count in Excel vs HTML SVG overlay IDs.
     - Failure Mode count vs Target row count per sheet.
     - Failure Mode count vs 3-column data block count.
   - Extracts metadata and time-series arrays from each sheet.
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
- **In Memory**: Decrypted only in the browser's JavaScript runtime. The password is Base64 obfuscated in the source code to prevent casual viewing.
- **Maintenance Logs**: Stored in browser localStorage with optional export/import as JSON files.

## Component Mapping
- Each Excel sheet name must match an SVG component ID in `index.html`.
- SVG overlay uses `preserveAspectRatio="none"` to scale with the background JPG.
- Clickable areas are defined as `<rect>` elements with `class="clickable-area"`.
EOF

# --- INSTALLATION_AND_OPERATIONS.md ---
cat << 'EOF' > INSTALLATION_AND_OPERATIONS.md
# Installation, Operations & Troubleshooting

## 🛠️ For Developers (Build Environment)

### Prerequisites
- Python 3.x
- `openpyxl`, `pycryptodome`

`pip3 install openpyxl pycryptodome`

### Build Process
1. Place `build_data.py`, `embed_data.py`, and the Excel file (e.g., `RCM 2.xlsx`) in the **Setup** folder.
2. Run the build script: `python3 build_data.py "RCM 2.xlsx"` (Generates `data.enc`).
3. Run the embed script: `python3 embed_data.py` (Generates `dashboard.html` in the Run folder).

### Version Display
Both scripts print their version numbers at the top of execution:
- `build_data.py Version: v0.3.14`
- `embed_data.py Version: v0.1.4`

## 🚀 For End-Users (Operations)
1. Ensure the **Run** folder contains: `dashboard.html`, `diagram.jpg`, `crypto-js.min.js`, and `chart.umd.js`.
2. Double-click `dashboard.html`.
3. *Note*: If using Chrome, local file restrictions might block JS execution. If so, right-click the file -> "Open With" -> Safari, or use a local server like `python3 -m http.server`.

### Maintenance Log Workflow
- **System Log** (Level 1): Exports/imports ALL components' maintenance dates. Use this for full backups.
- **Component Log** (Level 2): Exports/imports only the current component's dates. Smart import accepts both formats.
- Logs are auto-saved to browser localStorage on every date change.

## 🔧 Troubleshooting
| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **"Data: Not Loaded"** (Red text) | `dashboard.html` was opened instead of the embedded version, or JS libraries are missing. | Ensure `crypto-js.min.js` is in the same folder. Open `dashboard.html`, not `index.html`. |
| **Charts are blank / No Red Lines** | Corrupted `data.enc` or mismatched Excel formatting. | Re-run `build_data.py` and check terminal output for `[MATCH]` confirmations. |
| **Slider doesn't change colors** | Missing `thresholds` data in JSON. | Ensure `build_data.py` v0.3.11+ is used, which correctly maps Target rows to Failure Modes. |
| **Component count mismatch warning** | Excel sheet name doesn't match SVG ID in HTML. | Add the missing component to `index.html` SVG overlay or rename the Excel sheet. |
| **Data inconsistency error** | Failure Mode count != Target row count != Data block count. | Fix the Excel file so each Failure Mode has exactly one Target row and one 3-column data block. |
| **Git Push Fails (Permission Denied)** | SSH key not configured or added to ssh-agent. | Run `ssh-add ~/.ssh/id_rsa` (or your key name) and ensure the public key is in GitHub Settings. |
| **Maintenance dates not persisting** | Browser localStorage cleared. | Use Export Log to save dates to a JSON file, then Import Log to restore. |
EOF

# --- REVISION_HISTORY.md ---
cat << 'EOF' > REVISION_HISTORY.md
# Revision History

## Application Versions

### v0.5.2 (Current)
- Fixed smart import compatibility: Component-level import now correctly handles both System Logs and Component Logs.
- Added automatic detection of imported log format (nested vs flat structure).

### v0.5.1
- Added Export/Import Log buttons at Level 1 (System) and Level 2 (Component).
- System Log exports all components' maintenance dates.
- Component Log exports only the current component's dates.
- Smart merge logic: Importing a System Log at Component level extracts only the relevant component data.

### v0.5.0
- Added "Last Maintenance Date" column to Level 2 table.
- Implemented effective day calculation: `effectiveDay = sliderDay + (today - maintenanceDate)`.
- Yellow chart lines and status colors now reflect the effective day.
- Empty date assumed as today (0 offset) but not saved.
- Auto-save to browser localStorage on every date change.

### v0.4.13
- Fixed red lines stopping exactly at the blue curve intersection.
- Added red "X" marker (crossRot) at the target intersection point.
- Restored ESDV-101 hardcoded thresholds for slider color changes.

### v0.4.0
- Dynamic sheet processing: script now reads all sheets in the Excel file.
- Consistency Check A: Compares Excel sheet names vs HTML SVG component IDs.
- Consistency Check B: Verifies Failure Mode count == Target row count == Data block count.
- Detailed error reporting with row/column information on mismatch.

### v0.3.14
- Excel filename now passed as command-line argument to distinguish file versions.
- Usage: `python3 build_data.py "RCM 2.xlsx"`

### v0.3.13
- Fixed index-based mapping between Failure Modes and Target rows.
- Resolved 0.99 vs 99.0 percentage format mismatch.

### v0.3.11
- Restored hardcoded thresholds for ESDV-101 and GT-101.
- Fixed slider color changes for all components.

### v0.3.10
- Fixed Excel percentage parsing: values between 0 and 1 are now multiplied by 100.
- Resolved Target R(t) showing as 0.99% instead of 99%.

### v0.3.8
- Switched from chart-label scanning to Weibull formula calculation for Target Day.
- Formula: `t = η * (-ln(R))^(1/b)`.

### v0.2.0
- Initial Python build script (`build_data.py`).
- AES-256 encryption of Excel data to `data.enc`.
- Embed script (`embed_data.py`) to inject encrypted data into HTML.

### v0.1.0
- Initial HTML dashboard with SVG overlay.
- Basic Chart.js integration.
- Manual file upload with password decryption.

## Build Script Versions
- `build_data.py`: v0.3.14 (latest)
- `embed_data.py`: v0.1.4 (latest)

## Key Bug Fixes
1. **Log Scale Clipping (v0.4.6)**: Red lines now use `x: 1` instead of `x: 0` to prevent logarithmic scale errors.
2. **Typo Matching (v0.3.6)**: Fixed "Clossure" vs "Closure" spelling mismatch in thresholds dictionary.
3. **Header Row Detection (v0.4.4)**: Script now dynamically finds the header row instead of assuming Row 1.
4. **Read-Only Mode Crash (v0.4.2)**: Removed `read_only=True` to prevent hangs on complex Excel files.
5. **SVG Regex False Positive (v0.4.3)**: Restricted component ID search to inside `<svg>` tags only.
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
git commit -m "docs: update documentation with revision history and v0.5.2 features

- Added REVISION_HISTORY.md with complete version tracking
- Updated README.md with new features (maintenance dates, smart logs)
- Enhanced REQUIREMENTS.md with maintenance date logic and Excel structure
- Updated ARCHITECTURE.md with component mapping and security model
- Expanded INSTALLATION_AND_OPERATIONS.md with log workflow and troubleshooting
- Version bump to v0.5.2"

# Push to GitHub
echo "⬆️ Pushing to $REPO_URL ..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 Deployment successful! Dashboard is now live on GitHub."
else
    echo "⚠️ Push failed. Ensure your SSH key is added to ssh-agent:"
    echo "   Run: ssh-add ~/.ssh/id_rsa (or your specific key)"
fi