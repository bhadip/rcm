import re, os

# 1. Process diagram.xml (Add clickable classes, keep original colors)
filename = "diagram.xml"
if not os.path.exists(filename):
    print(f"❌ {filename} not found.")
    exit(1)

print(f"📄 Processing {filename}...")
with open(filename, "r", encoding="utf-8") as f:
    svg_content = f.read()

# Add IDs and clickable-area classes to the equipment groups
mapping = {
    "esdv": "ESDV-101", "vessel": "V-101", "psv": "PSV-101", "pt": "PT-101",
    "pic": "PIC-101", "pcv": "PCV-101", "pi": "PI-101", "pump": "P-101",
    "nrv": "NRV-101", "gt": "GT-101", "compressor": "K-101"
}

for cell_id, comp_id in mapping.items():
    pattern = f'<g data-cell-id="{cell_id}"'
    replacement = f'<g id="{comp_id}" class="clickable-area" data-cell-id="{cell_id}"'
    svg_content = svg_content.replace(pattern, replacement)

# Make responsive
svg_content = re.sub(r'width="[\d.]+px"', 'width="100%"', svg_content)
svg_content = re.sub(r'height="[\d.]+px"', 'height="100%"', svg_content)

# 2. Forcefully inject into index.html
html_file = "index.html"
if not os.path.exists(html_file):
    print("❌ index.html not found.")
    exit(1)

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

# Find the start of the diagram wrapper
start_marker = '<div id="diagram-wrapper">'
# Find the start of the next view (view-table)
end_marker = '<div id="view-table"'

if start_marker in html and end_marker in html:
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        # Construct the replacement block
        # We keep the opening wrapper, inject SVG, close the wrapper, close the card, close the view-diagram
        replacement_block = f'''<div id="diagram-wrapper">
    {svg_content}
</div>
</div>
</div>

<div id="view-table"'''
        
        # Replace the section
        html = html[:start_idx] + replacement_block + html[end_idx + len('<div id="view-table"'):]
        
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Successfully injected SVG into diagram-wrapper (Original colors preserved).")
    else:
        print("⚠️ Could not find the correct anchors in index.html.")
else:
    print("❌ Could not find diagram-wrapper or view-table in index.html.")
