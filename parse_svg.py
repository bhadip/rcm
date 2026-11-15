import re, json, sys
xml = open("diagram.xml", encoding="utf-8").read()

# viewBox
vb = re.search(r'viewBox="([\d.\s]+)"', xml)
viewbox = vb.group(1) if vb else "0 0 1962 718"

# draw.io cell-id -> our component tag
MAP = {
    "esdv":"ESDV-101","vessel":"V-101","psv":"PSV-101","pt":"PT-101",
    "pic":"PIC-101","pcv":"PCV-101","pi":"PI-101","pump":"P-101",
    "nrv":"NRV-101","gt":"GT-101","compressor":"K-101"
}

out = {"viewBox": viewbox, "components": []}
# split into per-cell groups
for cid, tag in MAP.items():
    # find the <g data-cell-id="cid"> ... up to its matching close (non-greedy to next data-cell-id or end)
    m = re.search(r'<g data-cell-id="'+re.escape(cid)+r'">(.*?)(?=<g data-cell-id=|</g></g>$|$)', xml, re.DOTALL)
    if not m:
        out["components"].append({"id":tag,"cell":cid,"rect":None,"note":"group not found"})
        continue
    block = m.group(1)
    rect = re.search(r'<rect[^>]*\bx="([\d.\-]+)"[^>]*\by="([\d.\-]+)"[^>]*\bwidth="([\d.\-]+)"[^>]*\bheight="([\d.\-]+)"', block)
    if rect:
        x,y,w,h = map(float, rect.groups())
    else:
        # fallback: bbox from a <path d="..."> numeric points
        p = re.search(r'<path[^>]*\bd="([^"]+)"', block)
        if p:
            nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', p.group(1))]
            xs = nums[0::2]; ys = nums[1::2]
            x,y = min(xs),min(ys); w,h = max(xs)-x, max(ys)-y
        else:
            x=y=w=h=None
    out["components"].append({"id":tag,"cell":cid,
        "rect":None if x is None else [round(x,1),round(y,1),round(w,1),round(h,1)]})

print(json.dumps(out, indent=2))
