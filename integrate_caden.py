# Version: v0.4.0 (Switched to caden_loader.txt for remote auto-updates)
import re, os, sys

SRC = "caden_loader.txt"
HTML = "index.html"

if not os.path.exists(SRC):
    print(f"❌ {SRC} not found"); sys.exit(1)
if not os.path.exists(HTML):
    print("❌ index.html not found"); sys.exit(1)

# Read the clean loader block
loader = open(SRC, encoding="utf-8").read().strip()
block = f"<!-- START CADEN LOADER -->\n{loader}\n<!-- END CADEN LOADER -->"

html = open(HTML, encoding="utf-8").read()

# Remove any prior CADEN block (old embedded script or old loader)
html = re.sub(r'<!--\s*START CADEN (?:LICENSING|LOADER)[\s\S]*?<!--\s*END CADEN (?:LICENSING|LOADER)\s*-->', '', html)

# Inject before </head>
html = html.replace('</head>', block + '\n</head>', 1)

# Ensure header padding for the badge
if 'padding-right:170px' not in html:
    html = html.replace('header{', 'header{padding-right:170px;', 1)

open(HTML, "w", encoding="utf-8").write(html)
ver = re.search(r'Loader\s*(v[\d\.]+)', loader)
v = ver.group(1) if ver else "Unknown"
print(f"✅ CADEN Loader {v} injected. Remote auto-updates enabled.")
