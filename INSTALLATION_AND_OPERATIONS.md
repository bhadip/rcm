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
