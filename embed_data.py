# Version: v0.2.1
import os, re, sys, json, glob, base64

EMBED_DATA_VERSION = "v0.2.1"
HTML_FILE = "index.html"; DATA_FILE = "data.enc"; OUTPUT_FILE = "dashboard.html"
PASSWORD = "Brawijaya2026!"
BRANDING_COPYRIGHT = "&copy; 2026 BCore &middot; Brawijaya Center Of Reliability & Integrity Excellences"
BRANDING_POWERED = "Powered by Prasanti Advisory, Singapore"

def get_excel_name():
    if len(sys.argv) > 1: return os.path.basename(sys.argv[1])
    try: return json.load(open("build_info.json", encoding="utf-8")).get("source_excel")
    except: pass
    xls = [p for p in glob.glob("*.xlsx") if not os.path.basename(p).startswith("~$")]
    return os.path.basename(max(xls, key=os.path.getmtime)) if xls else "Unknown"

def get_build_data_version():
    try: return json.load(open("build_info.json", encoding="utf-8")).get("build_data_version")
    except: pass
    try:
        m = re.search(r'#\s*Version:\s*(v\d+\.\d+\.\d+)', open("build_data.py", encoding="utf-8").read())
        if m: return m.group(1)
    except: pass
    return "Unknown"

def embed_data():
    print(f"embed_data.py Version: {EMBED_DATA_VERSION}")
    for fn in (HTML_FILE, DATA_FILE):
        if not os.path.exists(fn): print(f"❌ Error: {fn} not found."); return

    html = open(HTML_FILE, encoding="utf-8").read()
    m = re.search(r'v(\d+\.\d+\.\d+)', html)
    app_version = m.group(1) if m else "Unknown"
    excel_name = get_excel_name()
    bdv = get_build_data_version()

    print(f"📄 App version: v{app_version} | Excel: {excel_name} | build_data: {bdv}")
    cv = re.search(r'const\s+CADEN_VERSION\s*=\s*["\']([^"\']+)["\']', html)
    print(f"🔒 CADEN Licensing: v{cv.group(1)} detected." if cv else "⚠️ Warning: CADEN script missing.")

    data = open(DATA_FILE, encoding="utf-8").read().strip()
    b64 = lambda x: base64.b64encode(x.encode('utf-8')).decode('utf-8')
    html = html.replace('const EMBEDDED_DATA = null;', f'const EMBEDDED_DATA = "{data}";')
    html = html.replace('const EMBEDDED_PWD_B64 = "";', f'const EMBEDDED_PWD_B64 = "{b64(PASSWORD)}";')
    html = html.replace('const EMBEDDED_BRAND_C_B64 = "";', f'const EMBEDDED_BRAND_C_B64 = "{b64(BRANDING_COPYRIGHT)}";')
    html = html.replace('const EMBEDDED_BRAND_P_B64 = "";', f'const EMBEDDED_BRAND_P_B64 = "{b64(BRANDING_POWERED)}";')

    # Remove legacy meta blocks
    html = re.sub(r'<script>\s*(window\.)?APP_BUILD_META.*?</script>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*const RCM_BUILD_META.*?</script>\s*', '', html, flags=re.DOTALL)

    meta_injection = (f'<script>\n    window.APP_BUILD_META = {{\n'
                      f'        appVersion: "{app_version}",\n'
                      f'        buildDataVersion: "{bdv}",\n'
                      f'        embedDataVersion: "{EMBED_DATA_VERSION}",\n'
                      f'        sourceExcelFile: "{excel_name}"\n'
                      f'    }};\n</script>\n')

    if '<!-- START CADEN LICENSING' in html:
        html = html.replace('<!-- START CADEN LICENSING', meta_injection + '<!-- START CADEN LICENSING', 1)
    else:
        html = html.replace('</head>', meta_injection + '</head>', 1)

    open(OUTPUT_FILE, "w", encoding="utf-8").write(html)
    print(f"✅ Success! {OUTPUT_FILE} created. APP_BUILD_META injected before CADEN script.")

if __name__ == "__main__":
    embed_data()
