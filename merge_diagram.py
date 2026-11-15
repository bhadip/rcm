import re, os

# Look for the freshly exported file
filename = "diagram_original.svg"
if not os.path.exists(filename):
    print(f"❌ {filename} not found. Please export it from Draw.io first.")
    exit(1)

print(f"📄 Reading {filename}...")
with open(filename, "r", encoding="utf-8") as f:
    svg_content = f.read()

# Map draw.io cell IDs to our component IDs
mapping = {
    "esdv": "ESDV-101", "vessel": "V-101", "psv": "PSV-101", "pt": "PT-101",
    "pic": "PIC-101", "pcv": "PCV-101", "pi": "PI-101", "pump": "P-101",
    "nrv": "NRV-101", "gt": "GT-101", "compressor": "K-101"
}

# SURGICAL: Only touch the 11 tracked groups. Leave everything else alone.
for cell_id, comp_id in mapping.items():
    # Find the group
    pattern = r'(<g\s+[^>]*data-cell-id="'+re.escape(cell_id)+r'"[^>]*>)'
    match = re.search(pattern, svg_content)
    if match:
        old_tag = match.group(1)
        # Inject our id and clickable-area class
        new_tag = old_tag.replace('>', f' id="{comp_id}" class="clickable-area">')
        svg_content = svg_content.replace(old_tag, new_tag, 1)
        print(f"   ✅ Made {comp_id} clickable.")
    else:
        print(f"   ⚠️ Could not find group for {cell_id} (it might be named differently in Draw.io).")

# Make responsive
svg_content = re.sub(r'width="[\d.]+px"', 'width="100%"', svg_content)
svg_content = re.sub(r'height="[\d.]+px"', 'height="100%"', svg_content)

# Save as the active diagram file
with open("diagram.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
print("✅ diagram.svg created successfully with ALL original elements intact!")
