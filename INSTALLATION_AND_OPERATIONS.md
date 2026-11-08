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
