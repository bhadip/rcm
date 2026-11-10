# Version: v0.4.5
import openpyxl
import json
import os
import hashlib
import base64
import sys
import re

print("build_data.py Version: v0.4.5")

# ==========================================
# COMMAND LINE ARGUMENT PARSING
# ==========================================
if len(sys.argv) < 2:
    print("Usage: python3 build_data.py <excel_filename>")
    print("Example: python3 build_data.py 'RCM 2.xlsx'")
    sys.exit(1)

INPUT_EXCEL = sys.argv[1]
OUTPUT_FILE = "data.enc"
PASSWORD = "Brawijaya2026!"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(SCRIPT_DIR, 'index.html')

def safe_float(val, default=0.0):
    if val is None: return default
    try:
        if isinstance(val, str) and '%' in val: 
            val = val.replace('%', '')
            result = float(val)
            if 0 < result <= 1: return result * 100
            return result
        return float(val)
    except (ValueError, TypeError): return default

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
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    result = b"Salted__" + salt + ciphertext
    return base64.b64encode(result).decode('utf-8')

def get_html_components():
    if not os.path.exists(HTML_PATH):
        print(f"⚠️ Warning: {HTML_PATH} not found. Skipping HTML consistency check.")
        return None
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    svg_match = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.DOTALL)
    if not svg_match: return set()
    pattern = r'<rect\s+id="([^"]+)"\s+class="clickable-area"'
    return set(re.findall(pattern, svg_match.group(1)))

def parse_sheet(ws, sheet_name):
    component_data = {"failureModes": []}
    
    # 1. DYNAMICALLY FIND HEADER ROW
    start_row = 2
    for r in range(1, 10):
        val = ws.cell(row=r, column=2).value
        if val and str(val).strip() == "Failure Mode":
            start_row = r + 1
            print(f"  -> Found header at Row {r}. Data starts at Row {start_row}.")
            break

    # 2. Read Failure Modes dynamically (Column B)
    fm_list = []
    row_idx = start_row
    while True:
        fm_name = ws.cell(row=row_idx, column=2).value
        if not fm_name:
            break
            
        # FIX 1: Do not strip "Failure Mode: ", leave it exactly as is
        raw_name = str(fm_name).strip()
        
        fm_list.append({
            "row": row_idx,
            "name": raw_name
        })
        row_idx += 1
        
    if not fm_list:
        print(f"⚠️ Warning: No Failure Modes found in sheet '{sheet_name}'. Skipping sheet.")
        return None

    # 3. Read Target Rows dynamically (Column E)
    target_list = []
    for r in range(1, ws.max_row + 1):
        cell_e = ws.cell(row=r, column=5).value
        if isinstance(cell_e, str) and cell_e.strip().lower() == "target":
            rt = safe_float(ws.cell(row=r, column=6).value, 0)
            days = safe_float(ws.cell(row=r, column=7).value, 0)
            yellow = safe_float(ws.cell(row=r, column=9).value, 0)
            red = safe_float(ws.cell(row=r, column=10).value, 0)
            
            if rt > 0 and days > 0:
                if 0 < rt <= 1: rt *= 100
                target_list.append({
                    "row": r,
                    "targetDay": round(days, 2),
                    "yellow": round(yellow, 2),
                    "red": round(red, 2),
                    "targetRt": round(rt, 2)
                })

    # 4. CONSISTENCY CHECK: FM count vs Target count
    if len(fm_list) != len(target_list):
        print(f"❌ ERROR: Data inconsistency in sheet '{sheet_name}'!")
        print(f"   - Found {len(fm_list)} Failure Modes.")
        print(f"   - Found {len(target_list)} 'Target' rows.")
        sys.exit(1)

    # FIX 2: STRICT CHECK for 3-Column Data Sets starting from Column L (12)
    # We check Row 4 (where time-series data usually starts) to count valid blocks
    data_block_count = 0
    max_possible_blocks = (ws.max_column - 11) // 3
    
    for i in range(max_possible_blocks):
        col_idx = 12 + (i * 3) # Column L is 12
        # Check if the first column of the block (the 'Day' column) has numeric data in Row 4
        val = ws.cell(row=4, column=col_idx).value
        if isinstance(val, (int, float)):
            data_block_count += 1
        else:
            break # Stop counting at the first empty block

    print(f"  -> Found {len(fm_list)} Failure Modes and {data_block_count} valid 3-column Data Blocks (starting Col L).")

    if len(fm_list) != data_block_count:
        print(f"❌ ERROR: Data Block Mismatch in sheet '{sheet_name}'!")
        print(f"   - Number of Failure Modes: {len(fm_list)}")
        print(f"   - Number of 3-Column Data Sets: {data_block_count}")
        print(f"   - Every Failure Mode MUST have its own corresponding (t, Reliability, Failure Rate) block.")
        print(f"   - Please check the Excel sheet for missing or extra data columns starting at Column L.")
        sys.exit(1)

    print(f"  ✅ Consistency check passed for '{sheet_name}'.")

    # 5. Process Data
    for i, fm in enumerate(fm_list):
        t_data = target_list[i] 
        
        mtbf_days = safe_float(ws.cell(row=fm['row'], column=8).value, 1000)
        
        day_col = 12 + (i * 3)
        rel_col = 13 + (i * 3)
        fr_col = 14 + (i * 3)
        
        days_data, rel_data, fr_data = [], [], []
        for r in range(4, 1000): 
            day_val = ws.cell(row=r, column=day_col).value
            if isinstance(day_val, (int, float)):
                days_data.append(float(day_val))
                rel_data.append(safe_float(ws.cell(row=r, column=rel_col).value, 100.0))
                fr_data.append(safe_float(ws.cell(row=r, column=fr_col).value, 0.0))
            elif day_val is None and r > 10: 
                break
                
        fm_obj = {
            "name": fm['name'],
            "cause": str(ws.cell(row=fm['row'], column=3).value or "").strip(),
            "category": str(ws.cell(row=fm['row'], column=4).value or "").strip(),
            "targetRt": t_data['targetRt'],
            "taskList": str(ws.cell(row=fm['row'], column=6).value or "").strip(),
            "mtbfDays": mtbf_days,
            "thresholds": {"yellow": t_data['yellow'], "red": t_data['red']},
            "days": days_data,
            "reliabilityData": rel_data,
            "failureRateData": fr_data,
            "targetDay": t_data['targetDay']
        }
        component_data["failureModes"].append(fm_obj)
        print(f"  -> [MATCH] {fm['name']}: Rt={t_data['targetRt']}%, TargetDay={t_data['targetDay']}")

    return component_data

if __name__ == "__main__":
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: File '{INPUT_EXCEL}' not found in this directory.")
        exit(1)

    print(f"Reading {INPUT_EXCEL}...")
    
    html_components = get_html_components()
    wb = openpyxl.load_workbook(INPUT_EXCEL, data_only=True)
    excel_sheets = set(wb.sheetnames)
    
    if html_components is not None:
        missing_in_html = excel_sheets - html_components
        missing_in_excel = html_components - excel_sheets
        
        if missing_in_html or missing_in_excel:
            print("⚠️ WARNING: Component Mismatch detected between Excel and HTML!")
            if missing_in_html: print(f"   - Sheets in Excel but NOT in HTML: {missing_in_html}")
            if missing_in_excel: print(f"   - Components in HTML but NOT in Excel: {missing_in_excel}")
            print("   Continuing build process...\n")
        else:
            print("✅ Component consistency check passed.\n")
    else:
        print("⚠️ Skipping HTML consistency check.\n")

    app_data = {"maxDays": 365, "components": {}}
    
    for sheet_name in wb.sheetnames:
        print(f"Parsing {sheet_name}...")
        ws = wb[sheet_name]
        result = parse_sheet(ws, sheet_name)
        if result:
            app_data["components"][sheet_name] = result

    wb.close()
    
    print("\nEncrypting data...")
    encrypted_json = encrypt_data(app_data, PASSWORD)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_json)
    print(f"Success! {OUTPUT_FILE} created from {INPUT_EXCEL}.")