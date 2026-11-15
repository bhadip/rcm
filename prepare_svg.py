import re, os, sys

# 1. Locate the raw draw.io file
filename = None
for f in ["diagram.dat", "diagram.xml", "diagram.svg"]:
    if os.path.exists(f):
        filename = f
        break

if not filename:
    print("❌ No diagram file found.")
    sys.exit(1)

print(f"📄 Processing {filename}...")
with open(filename, "r", encoding="utf-8") as f:
    svg_content = f.read()

# 2. Map draw.io cell IDs
mapping = {
    "esdv": "ESDV-101", "vessel": "V-101", "psv": "PSV-101", "pt": "PT-101",
    "pic": "PIC-101", "pcv": "PCV-101", "pi": "PI-101", "pump": "P-101",
    "nrv": "NRV-101", "gt": "GT-101", "compressor": "K-101"
}

# 3. ONLY add IDs and classes. DO NOT touch styles, fills, or strokes.
for cell_id, comp_id in mapping.items():
    pattern = r'(<g\s+data-cell-id="'+re.escape(cell_id)+r'">)'
    replacement = f'<g id="{comp_id}" class="clickable-area" data-cell-id="{cell_id}"'
    svg_content = re.sub(pattern, replacement, svg_content)

# 4. Responsive
svg_content = re.sub(r'width="[\d.]+px"', 'width="100%"', svg_content)
svg_content = re.sub(r'height="[\d.]+px"', 'height="100%"', svg_content)

# 5. INJECT INTO INDEX.HTML
html_file = "index.html"
if os.path.exists(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find the diagram wrapper and replace its content
    pattern = r'<div id="diagram-wrapper">[\s\S]*?</div>'
    # We need to be careful not to match too much. Let's use a placeholder approach if possible, 
    # but since we are regenerating, let's just find the <svg> block inside diagram-wrapper.
    svg_pattern = r'(<div id="diagram-wrapper">\s*)<svg[\s\S]*?</svg>(\s*</div>)'
    
    if re.search(svg_pattern, html, re.DOTALL):
        html = re.sub(svg_pattern, r'\1' + svg_content + r'\2', html, flags=re.DOTALL)
        open(html_file, "w", encoding="utf-8").write(html)
        print("✅ SVG regenerated with ORIGINAL colors (no stripping).")
    else:
        print("⚠️ Could not find SVG in diagram-wrapper. You may need to manually insert it.")
