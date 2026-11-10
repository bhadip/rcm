# integrate_caden.py (Updated for v0.3.0 & Layout Fix)
import os
import re

HTML_FILE = "index.html"
CADEN_SCRIPT_FILE = "caden_script.txt"

def get_html_version(content):
    match = re.search(r'v(\d+\.\d+\.\d+)', content)
    return match.group(1) if match else "Unknown"

def get_caden_version(content):
    match = re.search(r'const\s+CADEN_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else "Unknown"

def integrate_caden():
    print(f"🔍 Checking files...")
    
    if not os.path.exists(HTML_FILE):
        print(f"❌ Error: {HTML_FILE} not found in this directory.")
        return
    if not os.path.exists(CADEN_SCRIPT_FILE):
        print(f"❌ Error: {CADEN_SCRIPT_FILE} not found in this directory.")
        return

    # 1. Read the new CADEN script
    with open(CADEN_SCRIPT_FILE, 'r', encoding='utf-8') as f:
        caden_content = f.read().strip()

    caden_version = get_caden_version(caden_content)
    print(f"   -> Detected CADEN Script Version: {caden_version}")

    # 2. Read the main index.html
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_version = get_html_version(html_content)
    print(f"   -> Detected index.html Version: {html_version}")

    # 3. Remove any existing CADEN block
    old_caden_pattern = re.compile(r'<!-- START CADEN LICENSING.*?-->.*?<!-- END CADEN LICENSING.*?-->', re.DOTALL | re.IGNORECASE)
    html_content = old_caden_pattern.sub('', html_content).strip()
    print("🧹 Removed old CADEN script (if any).")

    # 4. FIX LAYOUT CONFLICT: Add padding to header to prevent badge from blocking buttons
    # Look for the header CSS block and add padding-right if it's not already there
    header_css_pattern = re.compile(r'(header\s*\{[^}]*?)(\})', re.DOTALL)
    match = header_css_pattern.search(html_content)
    if match:
        current_header_css = match.group(1)
        if 'padding-right' not in current_header_css:
            # Insert padding-right before the closing brace
            new_header_css = current_header_css + ' padding-right: 170px; '
            html_content = html_content.replace(current_header_css, new_header_css)
            print("🎨 Applied CSS fix: Added padding-right to header to protect 'Calibrate SVG' button.")
        else:
            print("🎨 Header CSS already has padding-right. Skipping CSS fix.")

    # 5. Inject the new CADEN script before </head>
    head_pattern = re.compile(r'(</head>)', re.IGNORECASE)
    
    if head_pattern.search(html_content):
        new_html_content = head_pattern.sub(f'{caden_content}\n\\1', html_content, count=1)
        
        # 6. Save the file
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_html_content)
            
        print(f"\n✅ Integration Complete!")
        print(f"   📄 File: {HTML_FILE} (v{html_version})")
        print(f"   🔒 CADEN: v{caden_version}")
    else:
        print(f"❌ Error: Could not find the closing </head> tag in {HTML_FILE}.")

if __name__ == "__main__":
    integrate_caden()