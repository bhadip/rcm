# Version: v0.6.5
import openpyxl, json, os, hashlib, base64, sys

print("build_data.py Version: v0.6.5")

if len(sys.argv) < 2:
    print("Usage: python3 build_data.py <excel_filename>")
    sys.exit(1)

INPUT_EXCEL = sys.argv[1]
OUTPUT_FILE = "data.enc"
PASSWORD = "Brawijaya2026!"

def safe_float(val, default=0.0):
    if val is None: return default
    try:
        if isinstance(val, str):
            # Remove commas and spaces before parsing (handles "10,000")
            val = val.replace(',', '').strip()
            if '%' in val:
                val = val.replace('%', '')
                r = float(val)
                return r * 100 if 0 < r <= 1 else r
        return float(val)
    except (ValueError, TypeError): return default

def encrypt_data(data_dict, password):
    json_str = json.dumps(data_dict, ensure_ascii=False)
    salt = os.urandom(8); key_iv = b""; prev = b""
    while len(key_iv) < 48:
        prev = hashlib.md5(prev + password.encode('utf-8') + salt).digest()
        key_iv += prev
    key, iv = key_iv[:32], key_iv[32:48]
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(json_str.encode('utf-8'), AES.block_size))
    return base64.b64encode(b"Salted__" + salt + ct).decode('utf-8')

def parse_sheet(ws, sheet_name):
    component_data = {"failureModes": []}
    fm_list = []
    
    # 1. Identify all Failure Modes
    for r in range(1, ws.max_row + 1):
        v = ws.cell(row=r, column=2).value
        if v and str(v).strip().startswith("Failure Mode:"):
            fm_list.append({"row": r, "name": str(v).strip(), "index": len(fm_list) + 1})

    if not fm_list:
        print(f"  WARNING: No Failure Modes found in '{sheet_name}'.")
        return None
    print(f"  -> Found {len(fm_list)} Failure Modes.")

    # 2. Global ordered search for "Y(min)" and "X(max)" in Columns E, F, G (5, 6, 7)
    # This handles layouts where Parameter Grafik blocks are at the bottom of the sheet
    y_min_values = []
    x_max_values = []
    
    for r in range(1, ws.max_row + 1):
        for c in range(5, 8):
            val = ws.cell(row=r, column=c).value
            if isinstance(val, str):
                s = val.strip().lower()
                if "y(min)" in s:
                    y_min_values.append(safe_float(ws.cell(row=r, column=c+1).value, None))
                elif "x(max)" in s:
                    x_max_values.append(safe_float(ws.cell(row=r, column=c+1).value, None))

    if len(y_min_values) != len(fm_list):
        print(f"  WARNING: Found {len(y_min_values)} 'Y(min)' entries, expected {len(fm_list)}.")
    if len(x_max_values) != len(fm_list):
        print(f"  WARNING: Found {len(x_max_values)} 'X(max)' entries, expected {len(fm_list)}.")

    start_search_col = 12 + (len(fm_list) * 3)
    has_error = False

    for i, fm in enumerate(fm_list):
        row = fm['row']
        fm_obj = {
            "name": fm['name'],
            "cause": str(ws.cell(row=row, column=3).value or "").strip(),
            "category": str(ws.cell(row=row, column=4).value or "").strip(),
            "targetRt": safe_float(ws.cell(row=row, column=5).value, 95.0),
            "taskList": str(ws.cell(row=row, column=6).value or "").strip(),
            "mtbfDays": safe_float(ws.cell(row=row, column=8).value, 1000),
            "chartYMin": y_min_values[i] if i < len(y_min_values) else None,
            "chartXMax": x_max_values[i] if i < len(x_max_values) else None,
            "actualData": [],
        }

        # Extract Time Series
        day_col, rel_col, fr_col = 12 + i*3, 13 + i*3, 14 + i*3
        days, rel, fr = [], [], []
        for r in range(4, 2000):
            dv = ws.cell(row=r, column=day_col).value
            if isinstance(dv, (int, float)):
                days.append(float(dv))
                rel.append(safe_float(ws.cell(row=r, column=rel_col).value, 100.0))
                fr.append(safe_float(ws.cell(row=r, column=fr_col).value, 0.0))
            elif dv is None and r > 10:
                break
        fm_obj["days"], fm_obj["reliabilityData"], fm_obj["failureRateData"] = days, rel, fr

        # Extract Actual Data Block
        for c in range(start_search_col, ws.max_column + 1):
            for r in range(1, ws.max_row + 1):
                if str(ws.cell(row=r, column=c).value or "").strip().lower() == "data:":
                    marker = safe_float(ws.cell(row=r, column=c-1).value, 0) or safe_float(ws.cell(row=r, column=c+1).value, 0)
                    if int(marker) != fm['index']:
                        continue
                    count = int(safe_float(ws.cell(row=r+1, column=c).value, 0))
                    t_col = fe_col = c
                    for hc in range(c, min(c+10, ws.max_column+1)):
                        hv = str(ws.cell(row=r+2, column=hc).value or "").strip()
                        if hv == "t": t_col = hc
                        if "failure event" in hv.lower(): fe_col = hc
                    pts = []
                    for k in range(count):
                        rr = r + 3 + k
                        tv = safe_float(ws.cell(row=rr, column=t_col).value, 0)
                        fv = safe_float(ws.cell(row=rr, column=fe_col).value, 0)
                        if tv > 0: pts.append({"x": tv, "y": fv})
                    fm_obj["actualData"] = pts
                    break

        component_data["failureModes"].append(fm_obj)

    # Consistency Report
    print(f"  --- Consistency Report: {sheet_name} ({len(component_data['failureModes'])} FMs processed) ---")
    for fm in component_data["failureModes"]:
        # Apply defaults only if truly missing (None)
        if fm["chartYMin"] is None: fm["chartYMin"] = 0.0
        if fm["chartXMax"] is None: fm["chartXMax"] = max(fm["days"]) if fm["days"] else 1000.0
        
        y_min_str = f"{fm['chartYMin']:,.0f}"
        x_max_str = f"{fm['chartXMax']:,.0f}"
        default_x_str = f"{max(fm['days']):,.0f}" if fm["days"] else "1,000"

        if not fm["days"]:
            print(f"    ERROR: '{fm['name']}' has NO time-series data.")
            has_error = True
        elif fm["chartYMin"] == 0.0 and x_max_str == default_x_str:
            print(f"    INFO : '{fm['name']}' using default/minimal values Ymin={y_min_str}, Xmax={x_max_str}")
        else:
            print(f"    OK   : '{fm['name']}' Ymin={y_min_str}, Xmax={x_max_str}")
            
        # NEW: Report actual data points if any exist
        if fm["actualData"] and len(fm["actualData"]) > 0:
            print(f"    DATA : '{fm['name']}' -> {len(fm['actualData'])} actual points.")
            
    print("  ------------------------------------------")
    
    if has_error:
        print(f"\n❌ BUILD ABORTED: Critical errors found in '{sheet_name}'. Please fix the Excel file.")
        sys.exit(1)
        
    return component_data

if __name__ == "__main__":
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: File '{INPUT_EXCEL}' not found."); sys.exit(1)
    print(f"Reading {INPUT_EXCEL}...")
    wb = openpyxl.load_workbook(INPUT_EXCEL, data_only=True)
    app_data = {"maxDays": 365, "components": {}}
    
    for sheet_name in wb.sheetnames:
        print(f"Parsing {sheet_name}...")
        res = parse_sheet(wb[sheet_name], sheet_name)
        if res: app_data["components"][sheet_name] = res
        
    wb.close()
    print("\nEncrypting data...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encrypt_data(app_data, PASSWORD))
    print(f"Success! {OUTPUT_FILE} created from {INPUT_EXCEL}.")
