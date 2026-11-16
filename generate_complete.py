import re, os, sys

# 1. Read the diagram
fn = next((f for f in ["diagram.svg", "diagram.dat", "diagram.xml"] if os.path.exists(f)), None)
if not fn:
    print("❌ No diagram file found."); sys.exit(1)

print(f"📄 Processing {fn}...")
with open(fn, "r", encoding="utf-8") as f:
    svg = f.read()

# 2. Process SVG (Surgical: only touches tracked equipment shapes)
mapping = {"esdv":"ESDV-101","vessel":"V-101","psv":"PSV-101","pt":"PT-101",
"pic":"PIC-101","pcv":"PCV-101","pi":"PI-101","pump":"P-101",
"nrv":"NRV-101","gt":"GT-101","compressor":"K-101"}

for cell, comp in mapping.items():
    m = re.search(r'(<g\s+data-cell-id="'+re.escape(cell)+r'">)(.*?)(</g>)', svg, re.DOTALL)
    if not m: continue # Clean skip, no warnings
    o, inner, c = m.groups()
    o = o.replace(f'data-cell-id="{cell}"', f'id="{comp}" class="clickable-area" data-cell-id="{cell}"')
    sm = re.search(r'<(rect|path)([^>]*?)/?>', inner)
    if sm:
        old, tag, attrs = sm.group(0), sm.group(1), sm.group(2)
        attrs = re.sub(r'\s+style="[^"]*"','',attrs)
        attrs = re.sub(r'\s+fill="[^"]*"','',attrs)
        attrs = re.sub(r'\s+stroke="[^"]*"','',attrs)
        attrs = re.sub(r'class="([^"]*)"', r'class="comp-shape \1"', attrs) if 'class=' in attrs else (' class="comp-shape"'+attrs)
        inner = inner.replace(old, f'<{tag}{attrs}>', 1)
    svg = svg.replace(m.group(0), o+inner+c)

svg = re.sub(r'width="[\d.]+px"','width="100%"',svg)
svg = re.sub(r'height="[\d.]+px"','height="100%"',svg)
print("✅ SVG processed.")

# 3. Inject SVG into index.html (The Stitch)
html_file = "index.html"
if not os.path.exists(html_file):
    print("❌ index.html not found. Please ensure it exists."); sys.exit(1)

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

if "<!-- SVG_PLACEHOLDER -->" in html:
    html = html.replace("<!-- SVG_PLACEHOLDER -->", svg)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ SVG successfully injected into index.html.")
else:
    print("⚠️ SVG_PLACEHOLDER not found in index.html. Please add it manually.")
