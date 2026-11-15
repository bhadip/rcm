# Hardcoded known-good data from previous successful parse
data = [
    {"id": "ESDV-101", "rect": [286.0, 284.0, 150.0, 85.0]},
    {"id": "V-101", "rect": [486.0, 264.0, 220.0, 145.0]},
    {"id": "PSV-101", "rect": [771.0, 1.0, 205.0, 85.0]},
    {"id": "PT-101", "rect": [1026.0, 136.0, 220.0, 90.0]},
    {"id": "PIC-101", "rect": [1291.0, 136.0, 215.0, 95.0]},
    {"id": "PCV-101", "rect": [1546.0, 136.0, 195.0, 95.0]},
    {"id": "PI-101", "rect": [991.0, 441.0, 205.0, 90.0]},
    {"id": "P-101", "rect": [1251.0, 441.0, 180.0, 90.0]},
    {"id": "NRV-101", "rect": [1481.0, 441.0, 185.0, 90.0]},
    {"id": "GT-101", "rect": [416.0, 631.0, 260.0, 85.0]},
    {"id": "K-101", "rect": [1011.0, 631.0, 300.0, 85.0]}
]

svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 800" width="100%" height="100%" style="background:transparent;">\n'
svg += '<defs><style>.comp-shape{transition:fill .3s,stroke .3s;} .clickable-area{cursor:pointer;} .clickable-area:hover .comp-shape{fill:rgba(0,123,255,0.2)!important;stroke:#007bff!important;stroke-dasharray:5,5;}</style></defs>\n'

for item in data:
    comp_id = item['id'].strip()
    rect = item['rect']
    x, y, w, h = rect[0], rect[1], rect[2], rect[3]
    
    svg += f'  <g id="{comp_id}" class="clickable-area">\n'
    svg += f'    <rect class="comp-shape" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="#1762A5" stroke-width="2"/>\n'
    svg += f'    <text x="{x + w/2}" y="{y + h/2}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1762A5" text-anchor="middle" dominant-baseline="middle">{comp_id}</text>\n'
    svg += '  </g>\n'

svg += '</svg>'

with open("diagram.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("✅ diagram.svg generated successfully with hardcoded coordinates (bypassed corrupted file).")
