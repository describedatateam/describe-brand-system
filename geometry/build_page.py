"""Build the specimen page by inlining the generated plates."""
import html
import json

m = json.load(open("manifest.json", encoding="utf-8"))
tpl = open("page_template.html", encoding="utf-8").read()

order = ["A", "B", "C", "D", "E", "F", "G", "H", "Z"]
out = []
for fam in order:
    plates = [p for p in m["plates"] if p["family"] == fam]
    if not plates:
        continue
    name, note = m["families"][fam]["name"], m["families"][fam]["note"]
    out.append(f'<div class="family"><div class="fhead"><span class="k">{fam}</span>'
               f'<h3>{html.escape(name)}</h3><p>{html.escape(note)}</p></div>'
               f'<div class="grid">')
    for p in plates:
        out.append(
            '<figure>'
            f'<svg class="dsc" viewBox="-20 -20 240 240" role="img" '
            f'aria-label="{html.escape(p["title"])}">{p["body"]}</svg>'
            f'<figcaption><span class="id">{p["id"]}</span>'
            f'<b>{html.escape(p["title"])}</b>'
            f'<span>{html.escape(p["note"])}</span></figcaption></figure>')
    out.append("</div></div>")

page = tpl.replace("<!--PLATES-->", "".join(out))
open("specimen.html", "w", encoding="utf-8").write(page)
print(f"specimen.html — {len(page)/1024:.0f} KB, {len(m['plates'])} plates")
