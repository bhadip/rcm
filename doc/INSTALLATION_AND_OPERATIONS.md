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
