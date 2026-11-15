# Version: v0.3.3 (takes FULL CADEN block; neutralizes embedded </script> to <\/script>)
import re, os, sys
SRC="caden_script.txt"; HTML="index.html"
if not os.path.exists(SRC): print("❌ caden_script.txt not found"); sys.exit(1)
if not os.path.exists(HTML): print("❌ index.html not found"); sys.exit(1)
raw=open(SRC,encoding="utf-8").read()

# Locate the FIRST <script> and the LAST </script> (case-insensitive) to capture the WHOLE block
lo=re.search(r'<script[^>]*>',raw,re.IGNORECASE)
hi=re.search(r'</script>',raw,re.IGNORECASE)
if not lo or not hi:
    print("❌ No <script> block found in caden_script.txt"); sys.exit(1)
last_close=None
for m in re.finditer(r'</script>',raw,re.IGNORECASE): last_close=m
inner=raw[lo.end():last_close.start()]

# Neutralize ANY embedded </script> inside the JS body so it can't prematurely close our wrapper.
# '<\/script>' === '</script>' at JS runtime, but the HTML parser no longer sees a closer.
inner=inner.replace('</script>','<\\/script>').replace('</SCRIPT>','<\\/SCRIPT>')

ver=re.search(r'CADEN_VERSION\s*=\s*["\']([^"\']+)["\']',inner)
v=ver.group(1) if ver else "unknown"
print(f"📦 CADEN version (from CADEN_VERSION): {v}")

block='<!-- START CADEN LICENSING -->\n<script>\n'+inner.strip()+'\n</script>\n<!-- END CADEN LICENSING -->'

html=open(HTML,encoding="utf-8").read()
# Remove any prior CADEN block (incl. malformed) + leaked governance text
html=re.sub(r'<!--\s*START CADEN LICENSING[\s\S]*?<!--\s*END CADEN LICENSING\s*-->','',html)
html=re.sub(r'<!--\s*START CADEN LICENSING[\s\S]*?</script>','',html)
html=re.sub(r'<!--\s*GOVERNANCE COMPONENT[^>]*-->','',html,flags=re.IGNORECASE)
html=re.sub(r'\n\s*GOVERNANCE COMPONENT[^\n]*-->','',html,flags=re.IGNORECASE)

html=html.replace('</head>',block+'\n</head>',1)
if 'padding-right:170px' not in html:
    html=html.replace('header{','header{padding-right:170px;',1)

open(HTML,"w",encoding="utf-8").write(html)
print(f"✅ CADEN v{v} injected (embedded </script> neutralized). Badge/Device ID will render.")
