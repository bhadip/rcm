# Version: v0.2.3
import os, re, sys, json, glob, base64
EMBED_DATA_VERSION="v0.2.3"
HTML_FILE="index.html";DATA_FILE="data.enc";OUTPUT_FILE="dashboard.html";PASSWORD="Brawijaya2026!"
BRANDING_COPYRIGHT="&copy; 2026 BCore &middot; Brawijaya Center Of Reliability & Integrity Excellences"
BRANDING_POWERED="Powered by Prasanti Advisory, Singapore"
def get_excel_name():
    if len(sys.argv)>1:return os.path.basename(sys.argv[1])
    try:return json.load(open("build_info.json",encoding="utf-8")).get("source_excel")
    except:pass
    xls=[p for p in glob.glob("*.xlsx") if not os.path.basename(p).startswith("~$")]
    return os.path.basename(max(xls,key=os.path.getmtime)) if xls else "Unknown"
def get_build_data_version():
    try:return json.load(open("build_info.json",encoding="utf-8")).get("build_data_version")
    except:pass
    try:
        m=re.search(r'#\s*Version:\s*(v\d+\.\d+\.\d+)',open("build_data.py",encoding="utf-8").read())
        if m:return m.group(1)
    except:pass
    return "Unknown"
def embed_data():
    print(f"embed_data.py Version: {EMBED_DATA_VERSION}")
    for fn in (HTML_FILE,DATA_FILE):
        if not os.path.exists(fn):print(f"❌ Error: {fn} not found.");return
    html=open(HTML_FILE,encoding="utf-8").read()
    m=re.search(r'v(\d+\.\d+\.\d+)',html);app=m.group(1) if m else "Unknown"
    src=get_excel_name();bdv=get_build_data_version()
    print(f"📄 App version: v{app} | Excel: {src} | build_data: {bdv}")
    cv=re.search(r'<!-- START CADEN LOADER -->',html)
    print("🔒 CADEN Loader detected." if cv else "⚠️ Warning: CADEN Loader missing.")
    data=open(DATA_FILE,encoding="utf-8").read().strip()
    b64=lambda x:base64.b64encode(x.encode('utf-8')).decode('utf-8')
    # whitespace-tolerant injection (handles both minified and spaced constants)
    html=re.sub(r'const\s+EMBEDDED_DATA\s*=\s*null\s*;',lambda mm:f'const EMBEDDED_DATA = "{data}";',html)
    html=re.sub(r'const\s+EMBEDDED_PWD_B64\s*=\s*""\s*;',lambda mm:f'const EMBEDDED_PWD_B64 = "{b64(PASSWORD)}";',html)
    html=re.sub(r'const\s+EMBEDDED_BRAND_C_B64\s*=\s*""\s*;',lambda mm:f'const EMBEDDED_BRAND_C_B64 = "{b64(BRANDING_COPYRIGHT)}";',html)
    html=re.sub(r'const\s+EMBEDDED_BRAND_P_B64\s*=\s*""\s*;',lambda mm:f'const EMBEDDED_BRAND_P_B64 = "{b64(BRANDING_POWERED)}";',html)
    # remove any leaked governance comment/text outside scripts
    html=re.sub(r'<!--\s*GOVERNANCE COMPONENT[^>]*-->','',html,flags=re.IGNORECASE)
    html=re.sub(r'\n\s*GOVERNANCE COMPONENT[^\n]*-->','',html,flags=re.IGNORECASE)
    html=re.sub(r'<script>\s*(window\.)?APP_BUILD_META.*?</script>\s*','',html,flags=re.DOTALL)
    meta=(f'<script>\n    window.APP_BUILD_META = {{\n        appVersion: "{app}",\n        buildDataVersion: "{bdv}",\n        embedDataVersion: "{EMBED_DATA_VERSION}",\n        sourceExcelFile: "{src}"\n    }};\n</script>\n')
    if '<!-- START CADEN LOADER' in html:
        html=html.replace('<!-- START CADEN LOADER',meta+'<!-- START CADEN LOADER',1)
    else:
        html=html.replace('</head>',meta+'</head>',1)
    open(OUTPUT_FILE,"w",encoding="utf-8").write(html)
    print(f"✅ Success! {OUTPUT_FILE} created.")
if __name__=="__main__":embed_data()


# ==========================================
# FINAL VERSION SUMMARY
# ==========================================
def get_ver(path, pattern):
    if not os.path.exists(path): return "NOT FOUND"
    content = open(path, encoding="utf-8").read()
    m = re.search(pattern, content)
    return m.group(1) if m else "Unknown"

app_ver = get_ver("index.html", r'v0\.9\.(\d+)')
build_ver = get_ver("build_data.py", r'Version:\s*(v[\d\.]+)')
embed_ver = get_ver("embed_data.py", r'Version:\s*(v[\d\.]+)')
integ_ver = get_ver("integrate_caden.py", r'Version:\s*(v[\d\.]+)')
loader_ver = get_ver("caden_loader.txt", r'Loader\s*(v[\d\.]+)')
excel_file = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

print("\n" + "="*60)
print(" 📦 COMPONENT VERSIONS")
print("="*60)
print(f" App (index.html)      : v0.9.{app_ver}")
print(f" build_data.py         : {build_ver}")
print(f" embed_data.py         : {embed_ver}")
print(f" integrate_caden.py    : {integ_ver}")
print(f" caden_loader.txt      : {loader_ver}")
print(f" Excel Data            : {excel_file}")
print("="*60)
