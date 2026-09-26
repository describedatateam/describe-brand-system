"""Gate 01-04 checks from DESIGN_SYSTEM.md sec.29, run against brandkit/logo/."""
import glob, os, re, sys, xml.etree.ElementTree as ET

DIR = sys.argv[1] if len(sys.argv)>1 else "out"
PALETTE = {"#092052","#0F58E5","#E5484D","#64748B","#CBD5E1","#F6F8FC","#8C1D1D","#0F7B3D","#5B93FF","#14357F"}
GROUNDED = ("favicon",)
fails=[]; rows=[]
for path in sorted(glob.glob(f"{DIR}/*.svg")):
    n=os.path.basename(path); src=open(path,encoding="utf-8").read(); bad=[]
    root=ET.fromstring(src)
    NS="{http://www.w3.org/2000/svg}"

    # --- Gate 01 geometry ---------------------------------------------------
    if root.get("viewBox")!="-20 -20 240 240": bad.append("viewBox")
    if re.search(r"<image|xlink:href|data:image",src):  bad.append("raster embedded")
    if re.search(r"<(filter|feGaussian|linearGradient|radialGradient)",src): bad.append("filter/gradient")
    if re.search(r'(display\s*:\s*none|visibility\s*:\s*hidden|opacity="0")',src): bad.append("hidden object")
    if re.search(r"<clipPath|<mask",src): bad.append("clip/mask")
    if re.search(r"(inkscape|sodipodi|c2pa|<metadata)",src,re.I): bad.append("editor metadata")
    for el in root.iter():
        if el.get("stroke") and el.get("stroke")!="none":
            if not el.get("stroke-width"): bad.append(f"{el.tag.replace(NS,'')} missing stroke-width")
    # numeric precision <= 2dp
    for num in re.findall(r'-?\d+\.(\d+)', src):
        if len(num)>2: bad.append("precision >2dp"); break

    # --- Gate 02 brand ------------------------------------------------------
    cols={c.upper() for c in re.findall(r'#[0-9A-Fa-f]{6}',src)}
    off=cols-{c.upper() for c in PALETTE}
    if off: bad.append("off-palette "+",".join(sorted(off)))

    # --- Gate 04 production -------------------------------------------------
    if not re.match(r'^logo-5a-[a-z-]+-v\d+\.\d+\.svg$',n): bad.append("filename")
    if "-v1.0." not in n: bad.append("version")
    if root.get("role")!="img": bad.append("role=img")
    if root.find(f"{NS}title") is None or root.find(f"{NS}desc") is None: bad.append("title/desc")
    ids=re.findall(r'aria-labelledby="([^"]+)"',src)
    if not ids: bad.append("aria-labelledby")
    has_bg = bool(re.search(r'<rect[^>]*fill="#',src))
    should = any(k in n for k in GROUNDED)
    if has_bg!=should: bad.append("background "+("present"if has_bg else"absent"))
    if root.get("width") or root.get("height"): bad.append("fixed width/height")

    rows.append((n,len(src),sorted(cols),bad))
    if bad: fails.append((n,bad))

w=max(len(r[0]) for r in rows)
print(f"{'file':<{w}}  {'bytes':>6}  colours")
print("-"*(w+50))
for n,size,cols,bad in rows:
    mark="  OK  " if not bad else " FAIL "
    print(f"{n:<{w}}  {size:>6,}  {' '.join(cols)}")
    if bad: print(f"{'':<{w}}          -> "+"; ".join(bad))
print("-"*(w+50))
print(f"{len(rows)} files checked, {len(fails)} failing")
# cross-file checks
prim=open(f"{DIR}/logo-5a-primary-light-v1.0.svg",encoding="utf-8").read()
mark=open(f"{DIR}/logo-5a-mark-only-v1.0.svg",encoding="utf-8").read()
import difflib
print("mark-only == primary-light geometry:",
      re.sub(r'<(title|desc)[^>]*>.*?</\1>','',prim)==re.sub(r'<(title|desc)[^>]*>.*?</\1>','',mark) or "geometry same, ids differ")
sys.exit(1 if fails else 0)

