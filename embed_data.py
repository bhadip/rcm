# Version: v0.1.7
import os
import base64
import re

HTML_FILE = "index.html"
DATA_FILE = "data.enc"
OUTPUT_FILE = "dashboard.html"
PASSWORD = "Brawijaya2026!"

# FIX: Using HTML entities guarantees no "Â" garbage characters, as they are pure ASCII.
BRANDING_COPYRIGHT = "&copy; 2026 BCore &middot; Brawijaya Center Of Reliability & Integrity Excellences"
BRANDING_POWERED = "Powered by Prasanti Advisory, Singapore"

def embed_data():
    print(f"embed_data.py Version: v0.1.7")
    
    if not os.path.exists(HTML_FILE):
        print(f"❌ Error: {HTML_FILE} not found.")
        return
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    html_version_match = re.search(r'v\d+\.\d+\.\d+', html_content)
    html_version = html_version_match.group(0) if html_version_match else "Unknown"
    print(f"📄 Processing index.html ({html_version})...")

    caden_version_match = re.search(r'const\s+CADEN_VERSION\s*=\s*["\']([^"\']+)["\']', html_content)
    if caden_version_match:
        caden_version = caden_version_match.group(1)
        print(f"🔒 CADEN Licensing: v{caden_version} detected.")
    else:
        print(f"⚠️ Warning: CADEN licensing script is missing from index.html. Continuing build without it...")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data_content = f.read().strip()

    pwd_b64 = base64.b64encode(PASSWORD.encode('utf-8')).decode('utf-8')
    brand_c_b64 = base64.b64encode(BRANDING_COPYRIGHT.encode('utf-8')).decode('utf-8')
    brand_p_b64 = base64.b64encode(BRANDING_POWERED.encode('utf-8')).decode('utf-8')

    html_content = html_content.replace('const EMBEDDED_DATA = null;', f'const EMBEDDED_DATA = "{data_content}";')
    html_content = html_content.replace('const EMBEDDED_PWD_B64 = "";', f'const EMBEDDED_PWD_B64 = "{pwd_b64}";')
    html_content = html_content.replace('const EMBEDDED_BRAND_C_B64 = "";', f'const EMBEDDED_BRAND_C_B64 = "{brand_c_b64}";')
    html_content = html_content.replace('const EMBEDDED_BRAND_P_B64 = "";', f'const EMBEDDED_BRAND_P_B64 = "{brand_p_b64}";')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Success! Created {OUTPUT_FILE}")

if __name__ == "__main__":
    embed_data()