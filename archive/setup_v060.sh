#!/bin/bash
# setup_v060.sh  — writes the corrected v0.6.0 build_data.py and index.html
# Run NON-interactively (history expansion off, quoted heredocs = literal):
#     bash setup_v060.sh
set -e
cd "$(dirname "$0")"

echo "[1/2] Writing build_data.py (v0.6.0) ..."
cat > build_data.py << '__BUILD_PY__'
# Version: v0.6.0
import openpyxl, json, os, hashlib, base64, sys, re

print("build_data.py Version: v0.6.0")

if len(sys.argv) < 2:
    print("Usage: python3 build_data.py <excel_filename>")
    sys.exit(1)

INPUT_EXCEL = sys.argv[1]
OUTPUT_FILE = "data.enc"
PASSWORD = "Brawijaya2026!"

def safe_float(val, default=0.0):
    if val is None: return default
    try:
        if isinstance(val, str) and '%' in val:
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
    for r in range(1, ws.max_row + 1):
        v = ws.cell(row=r, column=2).value
        if v and str(v).strip().startswith("Failure Mode"):
            fm_list.append({"row": r, "name": str(v).strip(), "index": len(fm_list) + 1})
    if not fm_list:
        print(f"  WARNING: No Failure Modes in '{sheet_name}'.")
        return None
    print(f"  -> Found {len(fm_list)} Failure Modes.")

    start_search_col = 12 + (len(fm_list) * 3)   # first column AFTER all FM time-series blocks
    for i, fm in enumerate(fm_list):
        row = fm['row']
        fm_obj = {
            "name": fm['name'],
            "cause": str(ws.cell(row=row, column=3).value or "").strip(),
            "category": str(ws.cell(row=row, column=4).value or "").strip(),
            "targetRt": safe_float(ws.cell(row=row, column=5).value, 95.0),
            "taskList": str(ws.cell(row=row, column=6).value or "").strip(),
            "mtbfDays": safe_float(ws.cell(row=row, column=8).value, 1000),
            "chartYMin": None, "chartXMax": None, "actualData": [],
        }

        # --- A. Parameter Grafik (Y(min)/X(max)) in cols E-J near the FM row ---
        for c in range(5, 11):
            for ro in range(0, 12):
                lab = ws.cell(row=row + ro, column=c).value
                if isinstance(lab, str):
                    s = lab.strip().lower()
                    if s.startswith("y(min)"):
                        fm_obj["chartYMin"] = safe_float(ws.cell(row=row + ro, column=c + 1).value, 0)
                    elif s.startswith("x(max)"):
                        fm_obj["chartXMax"] = safe_float(ws.cell(row=row + ro, column=c + 1).value, 0)

        # --- B. Time series: 3-col block from column L (12) ---
        day_col, rel_col, fr_col = 12 + i*3, 13 + i*3, 14 + i*3
        days, rel, fr = [], [], []
        for r in range(4, 1000):
            dv = ws.cell(row=r, column=day_col).value
            if isinstance(dv, (int, float)):
                days.append(float(dv))
                rel.append(safe_float(ws.cell(row=r, column=rel_col).value, 100.0))
                fr.append(safe_float(ws.cell(row=r, column=fr_col).value, 0.0))
            elif dv is None and r > 10:
                break
        fm_obj["days"], fm_obj["reliabilityData"], fm_obj["failureRateData"] = days, rel, fr

        # --- C. Actual data block (after last FM column), matched by FM index marker ---
        for c in range(start_search_col, ws.max_column + 1):
            for r in range(1, ws.max_row + 1):
                if str(ws.cell(row=r, column=c).value or "").strip().lower() == "data:":
                    marker = safe_float(ws.cell(row=r, column=c-1).value, 0) or \
                             safe_float(ws.cell(row=r, column=c+1).value, 0)
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

    # --- CONSISTENCY REPORT ---
    print(f"  --- Consistency Report: {sheet_name} ---")
    for fm in component_data["failureModes"]:
        if fm["chartYMin"] is None: fm["chartYMin"] = 0
        if fm["chartXMax"] is None: fm["chartXMax"] = max(fm["days"]) if fm["days"] else 1000
        if not fm["days"]:
            print(f"    ERROR: '{fm['name']}' has NO time-series data.")
        if fm["chartYMin"] == 0 and fm["chartXMax"] in (1000, max(fm["days"]) if fm["days"] else 1000):
            print(f"    WARN : '{fm['name']}' Parameter Grafik missing -> defaults used.")
        if fm["actualData"]:
            print(f"    INFO : '{fm['name']}' -> {len(fm['actualData'])} actual points.")
    print("  ------------------------------------------")
    return component_data

if __name__ == "__main__":
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: File '{INPUT_EXCEL}' not found."); exit(1)
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
__BUILD_PY__

echo "[2/2] Writing index.html (v0.6.0) ..."
cat > index.html << '__INDEX_HTML__'
<!-- Version: v0.6.0 -->
<!DOCTYPE html>
<html lang="en">
<head>
    <style> body { opacity: 0; transition: opacity 0.2s ease-in; } </style>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCM Reliability Dashboard v0.6.0</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%230F172A'/%3E%3Cpath d='M50 15 L80 25 L80 50 C80 70 50 85 50 85 C50 85 20 70 20 50 L20 25 Z' fill='%231E293B' stroke='%233B82F6' stroke-width='3' stroke-linejoin='round'/%3E%3Ccircle cx='50' cy='50' r='12' fill='none' stroke='%2310B981' stroke-width='4'/%3E%3Cpath d='M50 32 L50 28 M50 72 L50 68 M32 50 L28 50 M72 50 L68 50 M37 37 L34 34 M63 63 L66 66 M37 63 L34 66 M63 37 L66 34' stroke='%2310B981' stroke-width='4' stroke-linecap='round'/%3E%3C/svg%3E">
    <script src="crypto-js.min.js"></script>
    <script src="chart.umd.js"></script>
    <style>
        :root { --primary:#2c3e50; --secondary:#34495e; --accent:#3498db; --bg:#f4f6f9; --card-bg:#fff; --green:#2ecc71; --yellow:#f1c40f; --red:#e74c3c; --text:#333; }
        body { font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; margin:0; padding:0; background:var(--bg); color:var(--text); display:flex; flex-direction:column; min-height:100vh; }
        header { background:var(--primary); color:#fff; padding:15px 20px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 5px rgba(0,0,0,.1); padding-right:170px; }
        header h1 { margin:0; font-size:1.2rem; }
        .version-badge { background:var(--accent); padding:4px 8px; border-radius:4px; font-size:.8rem; font-weight:bold; margin-left:10px; }
        .status-indicator { font-size:.9rem; margin-right:15px; font-weight:bold; }
        .status-loaded{color:#2ecc71;} .status-unloaded{color:#e74c3c;}
        footer { margin-top:auto; background:var(--secondary); color:#bdc3c7; text-align:center; padding:10px; font-size:.85rem; }
        #app-container { flex:1; padding:20px; max-width:1400px; margin:0 auto; width:100%; box-sizing:border-box; }
        .view{display:none;} .view.active{display:block;}
        .card { background:var(--card-bg); border-radius:8px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,.05); margin-bottom:20px; }
        .btn { background:var(--accent); color:#fff; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-size:1rem; margin-right:5px; }
        .btn:hover{background:#2980b9;} .btn-secondary{background:#95a5a6;} .btn-success{background:#27ae60;}
        #login-modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; justify-content:center; align-items:center; z-index:1000; }
        .login-box { background:#fff; padding:30px; border-radius:10px; width:300px; text-align:center; }
        .login-box input { width:100%; padding:10px; margin:10px 0; border:1px solid #ddd; border-radius:5px; box-sizing:border-box; }
        #diagram-wrapper { position:relative; width:100%; max-width:1300px; margin:0 auto; }
        #diagram-wrapper img { width:100%; display:block; }
        #diagram-overlay { position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }
        .clickable-area { fill:transparent; stroke:transparent; stroke-width:2px; cursor:pointer; pointer-events:auto; transition:all .2s ease; }
        .clickable-area:hover { fill:rgba(0,123,255,.15); stroke:#007bff; stroke-dasharray:5,5; }
        .comp-green{fill:rgba(46,204,113,.4)!important;stroke:#2ecc71!important;}
        .comp-yellow{fill:rgba(241,196,15,.4)!important;stroke:#f1c40f!important;}
        .comp-red{fill:rgba(231,76,60,.4)!important;stroke:#e74c3c!important;}
        table { width:100%; border-collapse:collapse; margin-top:10px; }
        th,td { padding:12px; text-align:left; border-bottom:1px solid #eee; }
        th { background:#f8f9fa; font-weight:600; }
        tr:hover { background:#f1f1f1; }
        .status-cell { font-weight:bold; text-align:center; }
        .status-green{color:var(--green);} .status-yellow{color:#d4ac0d;} .status-red{color:var(--red);}
        .slider-container { background:#fff; padding:15px; border-radius:8px; display:flex; align-items:center; gap:15px; box-shadow:0 2px 5px rgba(0,0,0,.05); position:sticky; bottom:20px; z-index:100; flex-wrap:wrap; }
        .slider-container input[type=range] { flex:1; min-width:200px; }
        .day-display { font-weight:bold; min-width:120px; text-align:right; }
        .slider-note { font-size:.85rem; color:#7f8c8d; font-style:italic; width:100%; margin-top:5px; }
        .charts-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
        @media (max-width:768px){ .charts-grid{grid-template-columns:1fr;} }
        .chart-box { background:#fff; padding:15px; border-radius:8px; height:400px; }
        .calibration-mode #diagram-overlay{pointer-events:auto;}
        .calibration-mode .clickable-area{fill:rgba(255,0,0,.2);stroke:red;cursor:move;}
        #calibration-controls{display:none;position:fixed;top:70px;right:20px;background:#fff;padding:15px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);z-index:500;max-width:300px;}
        .calibration-mode #calibration-controls{display:block;}
        #calibration-controls label{display:block;margin:5px 0;font-size:.9rem;}
        #calibration-controls select,#calibration-controls input{width:100%;padding:5px;margin:5px 0;}
        .maint-date-input{padding:5px;border:1px solid #ddd;border-radius:4px;width:100%;box-sizing:border-box;}
        .log-controls{margin-bottom:15px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
        .log-controls-group{display:flex;gap:10px;align-items:center;border-right:1px solid #ddd;padding-right:15px;}
        .log-controls-group:last-child{border-right:none;}
    </style>
</head>
<body>
    <header>
        <div style="display:flex;align-items:center;gap:12px;">
            <svg width="32" height="32" viewBox="0 0 100 100" style="flex-shrink:0;">
                <rect width="100" height="100" rx="20" fill="#0F172A"/>
                <path d="M50 15 L80 25 L80 50 C80 70 50 85 50 85 C50 85 20 70 20 50 L20 25 Z" fill="#1E293B" stroke="#3B82F6" stroke-width="3" stroke-linejoin="round"/>
                <circle cx="50" cy="50" r="12" fill="none" stroke="#10B981" stroke-width="4"/>
                <path d="M50 32 L50 28 M50 72 L50 68 M32 50 L28 50 M72 50 L68 50 M37 37 L34 34 M63 63 L66 66 M37 63 L34 66 M63 37 L66 34" stroke="#10B981" stroke-width="4" stroke-linecap="round"/>
            </svg>
            <h1>RCM Reliability Dashboard</h1>
            <span class="version-badge">v0.6.0</span>
        </div>
        <div>
            <span id="data-status" class="status-indicator status-unloaded">Data: Not Loaded</span>
            <span id="user-info" style="font-size:.9rem;margin-right:15px;">Offline Mode</span>
            <button class="btn btn-secondary" onclick="toggleCalibration()" style="font-size:.8rem;padding:5px 10px;">Calibrate SVG</button>
        </div>
    </header>

    <div id="app-container">
        <div id="view-diagram" class="view active">
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                    <h2 style="margin:0;">System Overview</h2>
                    <div class="log-controls"><div class="log-controls-group">
                        <button class="btn btn-success" onclick="exportSystemLog()" style="font-size:.9rem;">Export System Log</button>
                        <button class="btn" onclick="document.getElementById('import-system-log-input').click()" style="font-size:.9rem;">Import System Log</button>
                        <input type="file" id="import-system-log-input" accept=".json" style="display:none;" onchange="importSystemLog(event)">
                    </div></div>
                </div>
                <p>Click on a component (ESDV-101, V-101, etc.) to view its failure modes.</p>
                <div id="diagram-wrapper">
                    <img src="diagram.jpg" alt="System Diagram" id="diagram-image">
                    <svg id="diagram-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 600" preserveAspectRatio="none">
                      <rect id="ESDV-101" class="clickable-area" x="200" y="250" width="110" height="80"/>
                      <rect id="V-101" class="clickable-area" x="340" y="230" width="130" height="110"/>
                      <rect id="PSV-101" class="clickable-area" x="520" y="10" width="100" height="80"/>
                      <rect id="PT-101" class="clickable-area" x="680" y="130" width="100" height="70"/>
                      <rect id="PIC-101" class="clickable-area" x="850" y="130" width="100" height="70"/>
                      <rect id="PCV-101" class="clickable-area" x="990" y="130" width="110" height="80"/>
                      <rect id="PI-101" class="clickable-area" x="680" y="370" width="90" height="80"/>
                      <rect id="P-101" class="clickable-area" x="840" y="370" width="120" height="80"/>
                      <rect id="NRV-101" class="clickable-area" x="990" y="370" width="110" height="80"/>
                      <rect id="GT-101" class="clickable-area" x="340" y="500" width="130" height="90"/>
                      <rect id="K-101" class="clickable-area" x="650" y="490" width="160" height="80"/>
                    </svg>
                </div>
            </div>
        </div>

        <div id="view-table" class="view">
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                    <button class="btn btn-secondary" onclick="switchView('diagram')">Back to Diagram</button>
                    <div class="log-controls"><div class="log-controls-group">
                        <button class="btn btn-success" onclick="exportComponentLog()" style="font-size:.9rem;">Export Component Log</button>
                        <button class="btn" onclick="document.getElementById('import-comp-log-input').click()" style="font-size:.9rem;">Import Component Log</button>
                        <input type="file" id="import-comp-log-input" accept=".json" style="display:none;" onchange="importComponentLog(event)">
                    </div></div>
                </div>
                <h2 id="table-title">Component Failure Modes</h2>
                <div style="overflow-x:auto;">
                    <table id="fm-table"><thead><tr>
                        <th>No</th><th>Failure Mode</th><th>Cause</th><th>Category</th>
                        <th>Target R(t)</th><th>Task List</th><th>MTBF (Days)</th>
                        <th>Last Maintenance Date</th><th>Status</th>
                    </tr></thead><tbody></tbody></table>
                </div>
            </div>
        </div>

        <div id="view-charts" class="view">
            <div class="card">
                <button class="btn btn-secondary" onclick="switchView('table')">Back to Table</button>
                <h2 id="chart-title">Reliability & Failure Rate</h2>
                <div class="charts-grid">
                    <div class="chart-box"><canvas id="chart-reliability"></canvas></div>
                    <div class="chart-box"><canvas id="chart-failurerate"></canvas></div>
                </div>
            </div>
        </div>

        <div class="slider-container" id="global-slider" style="display:none;">
            <label for="day-slider">Current Day:</label>
            <input type="range" id="day-slider" min="1" max="365" value="1">
            <div class="day-display">Day: <span id="day-value">1</span></div>
            <div class="slider-note">Move the slider to view the equipment status.</div>
        </div>
    </div>

    <footer><div id="branding-copyright"></div><div id="branding-powered"></div></footer>

    <div id="login-modal"><div class="login-box">
        <h3>Secure Data Access</h3>
        <p style="font-size:.9rem;color:#666;">Select the encrypted data file and enter password.</p>
        <input type="file" id="file-input" accept=".enc,.json">
        <input type="password" id="password-input" placeholder="Enter Password">
        <button class="btn" onclick="decryptAndLoad()">Unlock Dashboard</button>
        <p id="login-error" style="color:red;font-size:.8rem;margin-top:10px;"></p>
    </div></div>

    <div id="calibration-controls">
        <h3>SVG Calibration</h3>
        <label>Select Component:</label><select id="calib-select"></select>
        <label>X: <input type="number" id="calib-x" step="10"></label>
        <label>Y: <input type="number" id="calib-y" step="10"></label>
        <label>Width: <input type="number" id="calib-w" step="10"></label>
        <label>Height: <input type="number" id="calib-h" step="10"></label>
        <button class="btn" onclick="exportCalibration()" style="margin-top:10px;width:100%;">Export SVG Code</button>
        <textarea id="calib-output" style="width:100%;height:100px;margin-top:10px;font-size:.8rem;"></textarea>
    </div>

    <script>
        const EMBEDDED_DATA = null;
        const EMBEDDED_PWD_B64 = "";
        const EMBEDDED_BRAND_C_B64 = "";
        const EMBEDDED_BRAND_P_B64 = "";
        let appData=null, currentDay=1, currentComponentId=null, currentFailureModeIndex=null;
        let chartRel=null, chartFR=null, maintenanceLog={};

        function setDataStatus(l){const e=document.getElementById('data-status');e.innerText=l?"Data: Loaded":"Data: Not Loaded";e.className="status-indicator "+(l?"status-loaded":"status-unloaded");}
        function loadMaintenanceLog(){const s=localStorage.getItem('rcm_maintenance_log');if(s){try{maintenanceLog=JSON.parse(s);}catch(e){}}}
        function saveMaintenanceLog(){localStorage.setItem('rcm_maintenance_log',JSON.stringify(maintenanceLog));}
        function download(name,obj){const u="data:text/json;charset=utf-8,"+encodeURIComponent(JSON.stringify(obj,null,2));const a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();}
        function exportSystemLog(){download("system_maintenance_log.json",maintenanceLog);alert("System Log exported!");}
        function importSystemLog(ev){const f=ev.target.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{try{maintenanceLog=JSON.parse(e.target.result);saveMaintenanceLog();alert("System Log imported!");updateDiagramColors();}catch(x){alert("Error: "+x.message);}};r.readAsText(f);ev.target.value='';}
        function exportComponentLog(){download("component_log_"+currentComponentId+".json",maintenanceLog[currentComponentId]||{});alert("Component Log exported!");}
        function importComponentLog(ev){const f=ev.target.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{try{let d=JSON.parse(e.target.result);if(d[currentComponentId]&&typeof d[currentComponentId]==='object')d=d[currentComponentId];if(!maintenanceLog[currentComponentId])maintenanceLog[currentComponentId]={};for(const[k,v]of Object.entries(d)){if(typeof v==='string')maintenanceLog[currentComponentId][k]=v;}saveMaintenanceLog();alert("Component Log imported!");renderTable(currentComponentId);updateDiagramColors();}catch(x){alert("Error: "+x.message);}};r.readAsText(f);ev.target.value='';}
        function getDaysOffset(ds){if(!ds)return 0;const a=new Date(ds),t=new Date();a.setHours(0,0,0,0);t.setHours(0,0,0,0);const d=Math.ceil((t-a)/86400000);return d>0?d:0;}
        function getEffectiveDay(s,c,i){const n=appData.components[c].failureModes[i].name;const d=maintenanceLog[c]?maintenanceLog[c][n]:null;return s+getDaysOffset(d);}

        document.addEventListener('DOMContentLoaded',()=>{
            loadMaintenanceLog();
            if(EMBEDDED_BRAND_C_B64)document.getElementById('branding-copyright').innerHTML=atob(EMBEDDED_BRAND_C_B64);
            if(EMBEDDED_BRAND_P_B64)document.getElementById('branding-powered').innerHTML=atob(EMBEDDED_BRAND_P_B64);
            if(EMBEDDED_DATA){try{const p=atob(EMBEDDED_PWD_B64);const s=CryptoJS.AES.decrypt(EMBEDDED_DATA,p).toString(CryptoJS.enc.Utf8);if(s){appData=JSON.parse(s);document.getElementById('day-slider').max=appData.maxDays||365;document.getElementById('login-modal').style.display='none';document.getElementById('global-slider').style.display='flex';setDataStatus(true);updateDiagramColors();}}catch(e){console.error("Auto-load failed:",e);}}
            document.querySelectorAll('.clickable-area').forEach(el=>el.addEventListener('click',e=>{if(document.body.classList.contains('calibration-mode'))return;const id=e.target.id;if(appData&&appData.components[id]){currentComponentId=id;renderTable(id);switchView('table');}else if(!appData)alert("Data is not loaded.");else alert("No data for "+id);}));
            document.getElementById('day-slider').addEventListener('input',e=>{currentDay=parseInt(e.target.value);document.getElementById('day-value').innerText=currentDay;updateCurrentDayLines();updateUI();});
            const cs=document.getElementById('calib-select');document.querySelectorAll('.clickable-area').forEach(el=>{const o=document.createElement('option');o.value=el.id;o.text=el.id;cs.appendChild(o);});
            cs.addEventListener('change',updateCalibrationInputs);['calib-x','calib-y','calib-w','calib-h'].forEach(id=>document.getElementById(id).addEventListener('change',applyCalibration));updateCalibrationInputs();
        });

        function toggleCalibration(){document.body.classList.toggle('calibration-mode');}
        function updateCalibrationInputs(){const id=document.getElementById('calib-select').value,el=document.getElementById(id);document.getElementById('calib-x').value=el.getAttribute('x');document.getElementById('calib-y').value=el.getAttribute('y');document.getElementById('calib-w').value=el.getAttribute('width');document.getElementById('calib-h').value=el.getAttribute('height');}
        function applyCalibration(){const id=document.getElementById('calib-select').value,el=document.getElementById(id);el.setAttribute('x',document.getElementById('calib-x').value);el.setAttribute('y',document.getElementById('calib-y').value);el.setAttribute('width',document.getElementById('calib-w').value);el.setAttribute('height',document.getElementById('calib-h').value);}
        function exportCalibration(){let s='<svg id="diagram-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 600" preserveAspectRatio="none">\n';document.querySelectorAll('.clickable-area').forEach(el=>{s+='  <rect id="'+el.id+'" class="clickable-area" x="'+el.getAttribute('x')+'" y="'+el.getAttribute('y')+'" width="'+el.getAttribute('width')+'" height="'+el.getAttribute('height')+'" />\n';});s+='</svg>';document.getElementById('calib-output').value=s;}
        function decryptAndLoad(){const fi=document.getElementById('file-input'),pw=document.getElementById('password-input').value,em=document.getElementById('login-error');if(!fi.files[0]){em.innerText="Select a data file.";return;}if(!pw){em.innerText="Enter a password.";return;}const r=new FileReader();r.onload=e=>{try{const s=CryptoJS.AES.decrypt(e.target.result,pw).toString(CryptoJS.enc.Utf8);if(!s)throw new Error("Wrong password");appData=JSON.parse(s);document.getElementById('day-slider').max=appData.maxDays||365;document.getElementById('login-modal').style.display='none';document.getElementById('global-slider').style.display='flex';setDataStatus(true);updateDiagramColors();}catch(x){em.innerText="Error: "+x.message;}};r.readAsText(fi.files[0]);}
        function switchView(v){document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));document.getElementById('view-'+v).classList.add('active');if(v==='diagram'){currentComponentId=null;updateDiagramColors();}else if(v==='table')renderTable(currentComponentId);else if(v==='charts')renderCharts();}
        function getStatusColor(d,t){if(!t)return'green';if(d<=t.yellow)return'green';if(d<=t.red)return'yellow';return'red';}
        function getComponentStatus(c){const comp=appData.components[c];let w='green';const p={green:1,yellow:2,red:3};comp.failureModes.forEach((fm,i)=>{const s=getStatusColor(getEffectiveDay(currentDay,c,i),fm.thresholds);if(p[s]>p[w])w=s;});return w;}
        function updateDiagramColors(){if(!appData)return;Object.keys(appData.components).forEach(c=>{const el=document.getElementById(c);if(el){el.classList.remove('comp-green','comp-yellow','comp-red');el.classList.add('comp-'+getComponentStatus(c));}});}
        function handleDateChange(c,i,ds){const n=appData.components[c].failureModes[i].name;if(!maintenanceLog[c])maintenanceLog[c]={};if(ds)maintenanceLog[c][n]=ds;else delete maintenanceLog[c][n];saveMaintenanceLog();updateDiagramColors();if(document.getElementById('view-table').classList.contains('active')){const row=document.querySelector('tr[data-fm-index="'+i+'"]');if(row){const s=getStatusColor(getEffectiveDay(currentDay,c,i),appData.components[c].failureModes[i].thresholds);const sc=row.querySelector('.status-cell');sc.className='status-cell status-'+s;sc.innerText=s.toUpperCase();}}if(document.getElementById('view-charts').classList.contains('active'))updateCurrentDayLines();}
        function renderTable(c){const comp=appData.components[c];document.getElementById('table-title').innerText='Failure Modes: '+c;const tb=document.querySelector('#fm-table tbody');tb.innerHTML='';comp.failureModes.forEach((fm,i)=>{const ed=getEffectiveDay(currentDay,c,i),st=getStatusColor(ed,fm.thresholds),sd=maintenanceLog[c]?maintenanceLog[c][fm.name]:'';const tr=document.createElement('tr');tr.setAttribute('data-fm-index',i);tr.innerHTML='<td>'+(i+1)+'</td><td>'+fm.name+'</td><td>'+fm.cause+'</td><td>'+fm.category+'</td><td>'+fm.targetRt+'%</td><td>'+fm.taskList+'</td><td>'+fm.mtbfDays.toFixed(1)+'</td><td><input type="date" class="maint-date-input" value="'+sd+'"></td><td class="status-cell status-'+st+'">'+st.toUpperCase()+'</td>';tr.querySelector('.maint-date-input').addEventListener('change',e=>handleDateChange(c,i,e.target.value));tr.addEventListener('click',e=>{if(e.target.tagName!=='INPUT'){currentFailureModeIndex=i;switchView('charts');}});tb.appendChild(tr);});}
        function getValueAtDay(days,vals,t){for(let i=0;i<days.length-1;i++){if(days[i]<=t&&days[i+1]>=t){const f=(t-days[i])/(days[i+1]-days[i]);return vals[i]+f*(vals[i+1]-vals[i]);}}return vals[vals.length-1];}
        function renderCharts(){
            const comp=appData.components[currentComponentId], fm=comp.failureModes[currentFailureModeIndex];
            document.getElementById('chart-title').innerText=currentComponentId+' - '+fm.name;
            let targetRt=parseFloat(fm.targetRt)||99.0, targetDay=parseFloat(fm.targetDay);
            const maxDays=Math.max(...fm.days);
            const yMin=(fm.chartYMin!=null)?fm.chartYMin:0;
            const xMax=(fm.chartXMax!=null)?fm.chartXMax:maxDays;
            if(!targetDay||isNaN(targetDay)||targetDay>=maxDays*0.99){for(let i=0;i<fm.reliabilityData.length-1;i++){if(fm.reliabilityData[i]>=targetRt&&fm.reliabilityData[i+1]<targetRt){const f=(targetRt-fm.reliabilityData[i])/(fm.reliabilityData[i+1]-fm.reliabilityData[i]);targetDay=fm.days[i]+f*(fm.days[i+1]-fm.days[i]);break;}}}
            const ed=getEffectiveDay(currentDay,currentComponentId,currentFailureModeIndex);
            const cRel=getValueAtDay(fm.days,fm.reliabilityData,ed);
            const cFR=getValueAtDay(fm.days,fm.failureRateData,ed);
            if(chartRel)chartRel.destroy(); if(chartFR)chartFR.destroy();
            const actual=(fm.actualData&&fm.actualData.length)?{label:'Actual Failure Events',data:fm.actualData,backgroundColor:'#ffffff',borderColor:'#333333',borderWidth:1.5,pointRadius:6,pointHoverRadius:8,showLine:false}:null;
            const relDS=[
                {label:'Reliability',data:fm.days.map((d,i)=>({x:d,y:fm.reliabilityData[i]})),borderColor:'#3498db',borderWidth:2,tension:0.4,pointRadius:0,fill:false},
                {label:'Current Day',data:[{x:ed,y:0},{x:ed,y:cRel}],borderColor:'#f1c40f',borderDash:[5,5],borderWidth:2,pointRadius:0,fill:false,tension:0,showLine:true},
                {label:'Current Rel',data:[{x:1,y:cRel},{x:ed,y:cRel}],borderColor:'#f1c40f',borderDash:[5,5],borderWidth:2,pointRadius:0,fill:false,tension:0,showLine:true},
                {label:'Current Intersection',data:[{x:ed,y:cRel}],backgroundColor:'#f1c40f',pointRadius:6,showLine:false},
                {label:'Target R(t)',data:[{x:1,y:targetRt},{x:targetDay,y:targetRt}],borderColor:'#e74c3c',borderDash:[5,5],borderWidth:3,pointRadius:0,fill:false,tension:0,showLine:true},
                {label:'Target Day',data:[{x:targetDay,y:0},{x:targetDay,y:targetRt}],borderColor:'#e74c3c',borderDash:[5,5],borderWidth:3,pointRadius:0,fill:false,tension:0,showLine:true},
                {label:'Target Intersection',data:[{x:targetDay,y:targetRt}],pointStyle:'crossRot',radius:10,borderColor:'#e74c3c',borderWidth:4,showLine:false}
            ];
            if(actual)relDS.push(actual);
            chartRel=new Chart(document.getElementById('chart-reliability').getContext('2d'),{type:'line',data:{datasets:relDS},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{type:'logarithmic',title:{display:true,text:'Days (Log Scale)'},min:1,max:xMax},y:{title:{display:true,text:'Reliability %'},min:yMin,max:100}}}});
            chartFR=new Chart(document.getElementById('chart-failurerate').getContext('2d'),{type:'line',data:{datasets:[
                {label:'Failure Rate',data:fm.days.map((d,i)=>({x:d,y:fm.failureRateData[i]})),borderColor:'#3498db',borderWidth:2,tension:0.4,pointRadius:0,fill:false},
                {label:'Current Day',data:[{x:ed,y:0},{x:ed,y:cFR}],borderColor:'#f1c40f',borderDash:[5,5],borderWidth:2,pointRadius:0,fill:false,tension:0,showLine:true},
                {label:'Current Intersection',data:[{x:ed,y:cFR}],backgroundColor:'#f1c40f',pointRadius:6,showLine:false}
            ]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{type:'linear',title:{display:true,text:'Days'},min:0,max:xMax},y:{title:{display:true,text:'Failure Rate'},min:0}}}});
        }
        function updateCurrentDayLines(){
            if(!chartRel||!chartFR||!appData)return;
            const fm=appData.components[currentComponentId].failureModes[currentFailureModeIndex];
            const ed=getEffectiveDay(currentDay,currentComponentId,currentFailureModeIndex);
            const cRel=getValueAtDay(fm.days,fm.reliabilityData,ed);
            const cFR=getValueAtDay(fm.days,fm.failureRateData,ed);
            chartRel.data.datasets[1].data=[{x:ed,y:0},{x:ed,y:cRel}];
            chartRel.data.datasets[2].data=[{x:1,y:cRel},{x:ed,y:cRel}];
            chartRel.data.datasets[3].data=[{x:ed,y:cRel}];
            chartRel.update('none');
            chartFR.data.datasets[1].data=[{x:ed,y:0},{x:ed,y:cFR}];
            chartFR.data.datasets[2].data=[{x:ed,y:cFR}];
            chartFR.update('none');
        }
        function updateUI(){if(document.getElementById('view-diagram').classList.contains('active'))updateDiagramColors();else if(document.getElementById('view-table').classList.contains('active'))renderTable(currentComponentId);}
    </script>
</body>
</html>
__INDEX_HTML__

echo "Done. Files written to: $(pwd)"
