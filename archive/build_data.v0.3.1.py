# Version: v0.3.1
import openpyxl
import json
import os
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_EXCEL = "RCM 1-2.xlsx"
OUTPUT_FILE = "data.enc"
PASSWORD = "Brawijaya2026!"

SHEET_NAMES = ["ESDV-101", "GT-101"]

THRESHOLDS = {
    "ESDV-101": {
        "Fail to Close": {"yellow": 46.53, "red": 93.06},
        "Internal Leakage": {"yellow": 51.41, "red": 102.81},
        "Spurious Closure": {"yellow": 47.15, "red": 94.29},
        "Slow Closure": {"yellow": 72.00, "red": 144.01}
    },
    "GT-101": {
        "Air intake filter clogged": {"yellow": 47.14, "red": 94.29},
        "Compressor blade erosion": {"yellow": 72.00, "red": 144.01},
        "Compressor blade corrosion": {"yellow": 90.00, "red": 180.01},
        "Compressor blade fatigue cracking": {"yellow": 51.40, "red": 102.81},
        "Compressor rotor imbalance": {"yellow": 47.93, "red": 95.86},
        "Compressor rotor rubbing": {"yellow": 72.00, "red": 144.01},
        "Combustion liner thermal fatigue cracking": {"yellow": 90.00, "red": 180.01},
        "Combustion liner buckling/deformation": {"yellow": 72.00, "red": 144.01},
        "Fuel nozzle blockage": {"yellow": 90.00, "red": 180.01},
        "Fuel nozzle poor atomization": {"yellow": 90.00, "red": 180.01},
        "Ignition system fail to ignite": {"yellow": 90.00, "red": 180.01},
        "Door latch damaged": {"yellow": 333.33, "red": 666.67},
        "Indicator lamp fail": {"yellow": 333.33, "red": 666.67},
        "HVAC Insufficient cooling": {"yellow": 416.67, "red": 833.33},
        "Lighting failure": {"yellow": 416.67, "red": 833.33}
    }
}

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        if isinstance(val, str) and '%' in val:
            val = val.replace('%', '')
        return float(val)
    except (ValueError, TypeError):
        return default

def encrypt_data(data_dict, password):
    json_str = json.dumps(data_dict, ensure_ascii=False)
    salt = os.urandom(8)
    key_iv = b""
    prev = b""
    while len(key_iv) < 48:
        prev = hashlib.md5(prev + password.encode('utf-8') + salt).digest()
        key_iv += prev
    key = key_iv[:32]
    iv = key_iv[32:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    result = b"Salted__" + salt + ciphertext
    return base64.b64encode(result).decode('utf-8')

def parse_sheet(ws, sheet_name):
    component_data = {"failureModes": []}
    
    for row_idx in range(3, 18):
        fm_name = ws.cell(row=row_idx, column=2).value
        if not fm_name: continue
        
        fm_name_str = str(fm_name).strip()
        target_rt = safe_float(ws.cell(row=row_idx, column=5).value, 95.0)
        mtbf_days = safe_float(ws.cell(row=row_idx, column=8).value, 1000)
        
        fm_index = row_idx - 3
        day_col = 12 + (fm_index * 3)
        rel_col = 13 + (fm_index * 3)
        fr_col = 14 + (fm_index * 3)
        
        days = []
        rel_data = []
        fr_data = []
        
        for r in range(4, 400):
            day_val = ws.cell(row=r, column=day_col).value
            if isinstance(day_val, (int, float)):
                days.append(float(day_val))
                rel_data.append(safe_float(ws.cell(row=r, column=rel_col).value, 100.0))
                fr_data.append(safe_float(ws.cell(row=r, column=fr_col).value, 0.0))
        
        # Precise linear interpolation to find exact targetDay (e.g., 139.58 days)
        target_day = days[-1] if days else 365
        for i in range(len(rel_data) - 1):
            if rel_data[i] >= target_rt and rel_data[i+1] < target_rt:
                y1, y2 = rel_data[i], rel_data[i+1]
                x1, x2 = days[i], days[i+1]
                target_day = x1 + (target_rt - y1) * (x2 - x1) / (y2 - y1)
                break
        
        thresholds = {"yellow": mtbf_days * 0.33, "red": mtbf_days * 0.66}
        if sheet_name in THRESHOLDS and fm_name_str in THRESHOLDS[sheet_name]:
            thresholds = THRESHOLDS[sheet_name][fm_name_str]
        
        fm = {
            "name": fm_name_str,
            "cause": str(ws.cell(row=row_idx, column=3).value or "").strip(),
            "category": str(ws.cell(row=row_idx, column=4).value or "").strip(),
            "targetRt": target_rt,
            "taskList": str(ws.cell(row=row_idx, column=6).value or "").strip(),
            "mtbfDays": mtbf_days,
            "thresholds": thresholds,
            "days": days,
            "reliabilityData": rel_data,
            "failureRateData": fr_data,
            "targetDay": round(target_day, 2)
        }
        component_data["failureModes"].append(fm)
        
    return component_data

if __name__ == "__main__":
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: {INPUT_EXCEL} not found.")
        exit(1)

    print(f"Reading {INPUT_EXCEL}...")
    wb = openpyxl.load_workbook(INPUT_EXCEL, data_only=True)
    app_data = {"maxDays": 365, "components": {}}
    
    for sheet_name in SHEET_NAMES:
        if sheet_name in wb.sheetnames:
            print(f"Parsing {sheet_name}...")
            ws = wb[sheet_name]
            app_data["components"][sheet_name] = parse_sheet(ws, sheet_name)
        else:
            print(f"Warning: Sheet '{sheet_name}' not found.")

    wb.close()
    print("Encrypting data...")
    encrypted_json = encrypt_data(app_data, PASSWORD)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_json)
    print(f"Success! {OUTPUT_FILE} created.")
    print(f"Password: {PASSWORD}")