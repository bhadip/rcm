# patch_v065.py  (v1.0)  — index.html v0.6.x -> v0.6.5
# a) Hide "Calibrate SVG" behind Ctrl+Shift+C   b) Remove Data/Offline indicators
# c) Show Owner + License expiry                 d) Clear-maintenance buttons (system + component)
# Idempotent: re-running does nothing. Works on the setup_v060.sh template (v0.6.0) or v0.6.3/v0.6.4.
import sys, os

f = "index.html"
if not os.path.exists(f):
    print("❌ index.html not found in", os.getcwd()); sys.exit(1)

s = open(f, encoding="utf-8").read()
orig = s

# ---- version bump (handle any starting point) ----
for v in ("v0.6.0", "v0.6.3", "v0.6.4"):
    s = s.replace(v, "v0.6.5")

# ---- (b)+(c) header: drop indicators, add license-info + hidden calibrate button ----
old_header = '''        <div>
            <span id="data-status" class="status-indicator status-unloaded">Data: Not Loaded</span>
            <span id="user-info" style="font-size:.9rem;margin-right:15px;">Offline Mode</span>
            <button class="btn btn-secondary" onclick="toggleCalibration()" style="font-size:.8rem;padding:5px 10px;">Calibrate SVG</button>
        </div>'''
new_header = '''        <div style="display:flex;align-items:center;gap:12px;">
            <span id="license-info" class="license-info"></span>
            <button id="calibrate-btn" class="btn btn-secondary" onclick="toggleCalibration()" style="font-size:.8rem;padding:5px 10px;">Calibrate SVG</button>
        </div>'''
s = s.replace(old_header, new_header)

# ---- (d) level-1: add Clear All Maintenance button ----
old_l1 = '''                        <input type="file" id="import-system-log-input" accept=".json" style="display:none;" onchange="importSystemLog(event)">
                    </div></div>'''
new_l1 = '''                        <input type="file" id="import-system-log-input" accept=".json" style="display:none;" onchange="importSystemLog(event)">
                        <button class="btn" style="background:#c0392b;font-size:.9rem;" onclick="clearAllMaintenance()">Clear All Maintenance</button>
                    </div></div>'''
s = s.replace(old_l1, new_l1)

# ---- (d) level-2: add Clear Component Maintenance button ----
old_l2 = '''                        <input type="file" id="import-comp-log-input" accept=".json" style="display:none;" onchange="importComponentLog(event)">
                    </div></div>'''
new_l2 = '''                        <input type="file" id="import-comp-log-input" accept=".json" style="display:none;" onchange="importComponentLog(event)">
                        <button class="btn" style="background:#c0392b;font-size:.9rem;" onclick="clearComponentMaintenance()">Clear Component Maintenance</button>
                    </div></div>'''
s = s.replace(old_l2, new_l2)

# ---- extra CSS: hidden calibrate btn + license style ----
old_css_end = '''    </style>
</head>'''
new_css_end = '''    </style>
    <style>
        #calibrate-btn{display:none;}
        .calibration-mode #calibrate-btn{display:inline-block;}
        .license-info{font-size:.85rem;color:#ecf0f1;}
    </style>
</head>'''
s = s.replace(old_css_end, new_css_end)

# ---- guard setDataStatus (element may no longer exist) ----
old_sds = 'function setDataStatus(l){const e=document.getElementById(\'data-status\');e.innerText=l?"Data: Loaded":"Data: Not Loaded";e.className="status-indicator "+(l?"status-loaded":"status-unloaded");}'
new_sds = 'function setDataStatus(l){const e=document.getElementById(\'data-status\');if(!e)return;e.innerText=l?"Data: Loaded":"Data: Not Loaded";e.className="status-indicator "+(l?"status-loaded":"status-unloaded");}'
s = s.replace(old_sds, new_sds)

# ---- (a) keyboard shortcut + (c) license populate, injected at DOMContentLoaded ----
old_anchor = "            const cs=document.getElementById('calib-select');"
new_anchor = ("            document.addEventListener('keydown',function(ev){if(ev.ctrlKey&&ev.shiftKey&&(ev.key==='C'||ev.key==='c')){ev.preventDefault();toggleCalibration();}});\n"
              "            (function(){let o='—',e='—';try{if(window.RCM_LICENSE_META){o=window.RCM_LICENSE_META.owner||o;e=window.RCM_LICENSE_META.expiry||e;}if(window.CADEN_LICENSE){o=window.CADEN_LICENSE.owner||o;e=window.CADEN_LICENSE.expiry||e;}}catch(_){}const li=document.getElementById('license-info');if(li)li.innerText='Owner: '+o+'  •  License expires: '+e;})();\n"
              "            const cs=document.getElementById('calib-select');")
s = s.replace(old_anchor, new_anchor)

# ---- (d) clear functions, after toggleCalibration ----
old_tog = "function toggleCalibration(){document.body.classList.toggle('calibration-mode');}"
new_tog = (old_tog + "\n"
    "        function clearAllMaintenance(){if(!appData){alert('No data loaded.');return;}if(confirm('This erases ALL Last Maintenance dates for ALL components. Continue?')){maintenanceLog={};saveMaintenanceLog();updateDiagramColors();if(document.getElementById('view-table').classList.contains('active')&&currentComponentId)renderTable(currentComponentId);alert('All maintenance data cleared.');}}\n"
    "        function clearComponentMaintenance(){if(!currentComponentId){alert('No component selected.');return;}if(confirm('This erases ALL Last Maintenance dates for '+currentComponentId+'. Continue?')){if(maintenanceLog)delete maintenanceLog[currentComponentId];saveMaintenanceLog();updateDiagramColors();renderTable(currentComponentId);alert('Maintenance data for '+currentComponentId+' cleared.');}}")
s = s.replace(old_tog, new_tog)

open(f, "w", encoding="utf-8").write(s)
print("✅ Patched index.html -> v0.6.5" if s != orig else "ℹ️  No change (already v0.6.5)")
