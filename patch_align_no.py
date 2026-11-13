# patch_align_no.py  (v1.0)
# Right-aligns the "No" header and the sequence-number cell in renderTable().
# Idempotent: running it again does nothing. Works on v0.6.0 and v0.6.3 layouts.
import sys, os

f = "index.html"
if not os.path.exists(f):
    print("❌ index.html not found in", os.getcwd()); sys.exit(1)

s = open(f, encoding="utf-8").read()
orig = s

# 1) Right-align the "No" column header
s = s.replace("<th>No</th>", '<th style="text-align:right">No</th>')

# 2) Right-align the first <td> built inside renderTable() (the sequence number cell)
s = s.replace("tr.innerHTML='<td>'", "tr.innerHTML='<td style=\"text-align:right\">'")

# 3) Bump version marker v0.6.3 -> v0.6.4 (no-op if your file isn't v0.6.3)
s = s.replace("v0.6.3", "v0.6.4")

open(f, "w", encoding="utf-8").write(s)
print("✅ Patched" if s != orig else "ℹ️  No change (already right-aligned)")
