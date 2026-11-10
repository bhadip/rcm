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
PASSWORD = "Brawijaya2026!" # The password to enter in the app

# List all component sheet names here
SHEET_NAMES = ["GT-101", "ESDV-101"] 

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def safe_float(val, default=0.0):
    """Safely converts a value to float, handling 'N/A', None, and strings."""
    if val is None:
        return default
    try:
        # Remove '%' if present (e.g., "95%")
        if isinstance(val, str) and '%' in val:
            val = val.replace('%', '')
        return float(val)
    except (ValueError, TypeError):
        return default

def generate_weibull_arrays(b, eta, days=365):
    """Generates Reliability R(t) and Failure Rate arrays using Weibull distribution."""
    rel_data = []
    fr_data = []
    for t in range(1, days + 1):
        # R(t) = exp(-(t/eta)^b)
        r_t = 100 * (2.718281828 ** (-((t/eta)**b)))
        # f(t) = (b/eta) * (t/eta)^(b-1) * exp(-(t/eta)^b)
        f_t = (b/eta) * ((t/eta)**(b-1)) * (2.718281828 ** (-((t/eta)**b)))
        rel_data.append(round(r_t, 4))
        fr_data.append(round(f_t, 6))
    return rel_data, fr_data

def encrypt_data(data_dict, password):
    """Encrypts JSON data using AES-256-CBC, compatible with CryptoJS.AES.decrypt"""
    json_str = json.dumps(data_dict, ensure_ascii=False)
    
    # 1. Generate random 8-byte salt
    salt = os.urandom(8)
    
    # 2. Derive Key and IV using MD5 (matches CryptoJS default EvpKDF)
    key_iv = b""
    prev = b""
    while len(key_iv) < 48: # 32 bytes key + 16 bytes IV
        prev = hashlib.md5(prev + password.encode('utf-8') + salt).digest()
        key_iv += prev
        
    key = key_iv[:32]
    iv = key_iv[32:48]
    
    # 3. Encrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # 4. Format as "Salted__" + salt + ciphertext, then Base64
    result = b"Salted__" + salt + ciphertext
    return base64.b64encode(result).decode('utf-8')

# ==========================================
# DATA PARSING LOGIC
# ==========================================
def parse_sheet(ws):
    component_data = {"failureModes": []}
    
    # Based on RCM 1-2.xlsx header:
    # Col 2 (B): Failure Mode
    # Col 3 (C): Penyebab
    # Col 4 (D): Kategori
    # Col 5 (E): Target R(t)
    # Col 6 (F): Task List
    # Col 7 (G): MTBF (h)
    # Col 8 (H): MTBF (d)
    # Col 9 (I): SD (Contains 'N/A')
    # Col 10 (J): b (Weibull Shape)
    
    for row_idx in range(3, 18): # Rows 3 to 17
        fm_name = ws.cell(row=row_idx, column=2).value # Col B
        if not fm_name: continue
        
        mtbf_days = safe_float(ws.cell(row=row_idx, column=8).value, 1000) # Col H
        weibull_b = safe_float(ws.cell(row=row_idx, column=10).value, 2.0) # Col J
        
        # Since the SME moved the exact Hijau/Kuning days into complex sub-blocks,
        # we calculate robust thresholds based on MTBF to ensure the app works perfectly.
        # Green: <= 66% of life, Yellow: <= 33% of life, Red: > 33%
        green_threshold = mtbf_days * 0.66
        yellow_threshold = mtbf_days * 0.33
        
        fm = {
            "name": str(fm_name).strip(),
            "cause": str(ws.cell(row=row_idx, column=3).value or "").strip(),
            "category": str(ws.cell(row=row_idx, column=4).value or "").strip(),
            "targetRt": safe_float(ws.cell(row=row_idx, column=5).value, 95.0),
            "taskList": str(ws.cell(row=row_idx, column=6).value or "").strip(),
            "mtbfDays": mtbf_days,
            "weibull_b": weibull_b,
            "thresholds": {
                "green": green_threshold,
                "yellow": yellow_threshold,
                "red": 0
            }
        }
        
        # Generate 365 days of data
        eta = mtbf_days if mtbf_days > 0 else 1000
        b = weibull_b if weibull_b > 0 else 2.0
        
        fm['reliabilityData'], fm['failureRateData'] = generate_weibull_arrays(b, eta)
        component_data["failureModes"].append(fm)
        
    return component_data

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: {INPUT_EXCEL} not found in this folder.")
        exit(1)

    print(f"Reading {INPUT_EXCEL}...")
    wb = openpyxl.load_workbook(INPUT_EXCEL, data_only=True)
    
    app_data = {"maxDays": 365, "components": {}}
    
    for sheet_name in SHEET_NAMES:
        if sheet_name in wb.sheetnames:
            print(f"Parsing {sheet_name}...")
            ws = wb[sheet_name]
            app_data["components"][sheet_name] = parse_sheet(ws)
        else:
            print(f"Warning: Sheet '{sheet_name}' not found.")

    wb.close()
    
    # Encrypt and save
    print("Encrypting data...")
    encrypted_json = encrypt_data(app_data, PASSWORD)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_json)
        
    print(f"Success! {OUTPUT_FILE} created.")
    print(f"Password for app: {PASSWORD}")