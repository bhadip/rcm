import re, os

svg_file = "diagram.svg"
if not os.path.exists(svg_file):
    print("❌ diagram.svg not found. Please run merge_diagram.py first.")
    exit(1)

with open(svg_file, "r", encoding="utf-8") as f:
    content = f.read()

tracked = ["ESDV-101", "V-101", "PSV-101", "PT-101", "PIC-101", "PCV-101", 
           "PI-101", "P-101", "NRV-101", "GT-101", "K-101"]

for comp_id in tracked:
    # Find the group block for this equipment
    pattern = r'(<g[^>]*id="'+re.escape(comp_id)+'"[^>]*>)(.*?)(</g>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        g_open, inner, g_close = match.groups()
        
        # Find the first <rect> or <path> inside this group
        shape_match = re.search(r'<(rect|path)([^>]*?)/?>', inner)
        if shape_match:
            old_shape = shape_match.group(0)
            tag = shape_match.group(1)
            attrs = shape_match.group(2)
            
            # 1. Strip ALL inline styles that override our CSS
            attrs = re.sub(r'\s+style="[^"]*"', '', attrs)
            attrs = re.sub(r'\s+fill="[^"]*"', '', attrs)
            attrs = re.sub(r'\s+stroke="[^"]*"', '', attrs)
            attrs = re.sub(r'\s+stroke-width="[^"]*"', '', attrs)
            
            # 2. Add the missing comp-shape class
            if 'class=' in attrs:
                attrs = re.sub(r'class="', 'class="comp-shape ', attrs)
            else:
                attrs += ' class="comp-shape"'
            
            # Reassemble
            new_shape = f'<{tag}{attrs}/>'
            inner = inner.replace(old_shape, new_shape, 1)
            content = content.replace(match.group(0), g_open + inner + g_close)
            print(f"✅ Patched {comp_id} (stripped styles, added comp-shape)")
        else:
            print(f"⚠️ No shape found inside {comp_id}")
    else:
        print(f"⚠️ Group {comp_id} not found")

# Save the fixed SVG
with open(svg_file, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ diagram.svg fixed. Colors will now work.")
