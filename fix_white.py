import re, os

fn = "diagram.svg"
if not os.path.exists(fn):
    print("❌ diagram.svg not found."); exit(1)

s = open(fn, encoding="utf-8").read()

# 1. Force LIGHT color-scheme on the root svg -> kills the black canvas,
#    makes every light-dark() resolve to its light value (light blue / dark text).
s = s.replace("color-scheme: light dark", "color-scheme: light")
s = re.sub(r'background-color:\s*transparent', 'background-color:#ffffff', s)
print("✅ Forced light color-scheme + white background.")

# 2. Give the 11 tracked shapes a light-blue DEFAULT fill/stroke (they were stripped to black).
#    Status CSS (.comp-green/.comp-yellow/.comp-red with !important) still overrides this.
tracked = ["ESDV-101","V-101","PSV-101","PT-101","PIC-101","PCV-101",
           "PI-101","P-101","NRV-101","GT-101","K-101"]
for comp in tracked:
    pat = r'(<g[^>]*id="'+re.escape(comp)+r'"[^>]*>)(.*?)(</g>)'
    m = re.search(pat, s, re.DOTALL)
    if not m: continue
    g_open, inner, g_close = m.groups()
    sm = re.search(r'<(rect|path)([^>]*?)/?>', inner)
    if sm:
        old, tag, attrs = sm.group(0), sm.group(1), sm.group(2)
        if 'fill=' not in attrs:
            attrs += ' fill="#dcebfa"'
        if 'stroke=' not in attrs:
            attrs += ' stroke="#1762A5" stroke-width="2"'
        inner = inner.replace(old, f'<{tag}{attrs}/>', 1)
        s = s.replace(m.group(0), g_open + inner + g_close)
        print(f"✅ {comp}: default light-blue fill restored.")

open(fn, "w", encoding="utf-8").write(s)
print("✅ diagram.svg fixed.")
