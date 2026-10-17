"""Build every token output from tokens/tokens.json.

  python3 tokens/build.py           write tokens/dist/* and tokens/TOKENS.md
  python3 tokens/build.py --check   fail if any of them is out of date (CI)

Outputs:
  dist/tokens.css    CSS custom properties: light on :root, dark under
                     prefers-color-scheme and [data-theme="dark"], and the
                     type scale re-based per medium under [data-medium].
  dist/tokens.json   Flat, resolved: one entry per token with its light and
                     dark value and its CSS name. For Python, JS, Figma
                     plugins, Plotly and matplotlib.
  TOKENS.md          The human reference: every value, with its job and its
                     measured contrast. Generated, so it cannot drift.

Standard library only.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from colour import contrast  # noqa: E402

SRC = HERE / "tokens.json"
DIST = HERE / "dist"

# Short names the kit already uses (ui/ui.css, type/typography.css, the
# website). Everything else gets its path, joined with hyphens.
ALIAS = {
    "color.surface.ground": "ground", "color.surface.panel": "panel",
    "color.surface.field": "field",
    "color.text.ink": "ink", "color.text.body": "body", "color.text.dim": "dim",
    "color.text.active-ink": "active-ink",
    "color.line.faint": "faint", "color.line.rule": "rule",
    "color.role.active": "active", "color.role.mark": "mark",
    "color.role.neg": "neg", "color.role.pos": "pos",
    "radius.control": "r", "stroke.hair": "hair",
    "size.control": "ctl", "size.control-sm": "ctl-sm",
    "motion.ease": "ease", "motion.t1": "t1", "motion.t2": "t2", "motion.t3": "t3",
    "shadow.elev": "elev",
}
PREFIX = [  # path prefix -> CSS prefix, first match wins
    ("color.brand.", "brand-"), ("color.viz.", "viz-"), ("font.", "font-"),
    ("type.line-height.", "lh-"), ("type.tracking.", "tr-"), ("type.weight.", "w-"),
    ("type.arabic.", "ar-"), ("space.", "s"), ("radius.", "radius-"),
    ("stroke.", "stroke-"), ("size.", "size-"),
]
MEDIA = ("web", "slides", "social", "report")
SEQ_STEPS = ("100", "200", "300", "400", "500", "600", "700")


def walk(node, path=(), inherited=None):
    """Yield (path, token) for every leaf, carrying $type down the tree."""
    t = node.get("$type", inherited)
    if "$value" in node:
        yield path, dict(node, **({"$type": t} if t else {}))
        return
    for k, v in node.items():
        if not k.startswith("$") and isinstance(v, dict):
            yield from walk(v, path + (k,), t)


def css_name(path):
    p = ".".join(path)
    if p in ALIAS:
        return "--" + ALIAS[p]
    for pre, out in PREFIX:
        if p.startswith(pre):
            return "--" + out + p[len(pre):].replace(".", "-")
    return "--" + p.replace(".", "-")


def css_value(tok, v):
    t = tok.get("$type", tok.get("type"))
    if t == "fontFamily":
        return ", ".join(f"'{f}'" if " " in f else f for f in v)
    if t == "cubicBezier":
        return "cubic-bezier(" + ",".join(f"{x:g}" for x in v) + ")"
    return str(v)


def type_scale(tokens, medium):
    base = tokens["type"]["base"][medium]["$value"]
    unit = "pt" if base.endswith("pt") else "px"
    b = float(base[:-2])
    step = 0.5 if unit == "pt" else 1
    out = {}
    for name, r in tokens["type"]["ratio"].items():
        if name.startswith("$"):
            continue
        v = round(b * r["$value"] / step) * step
        out[name] = f"{v:g}{unit}"
    return out


def resolve(tokens):
    flat = {}
    for path, tok in walk(tokens):
        dark = tok.get("$extensions", {}).get("mode", {}).get("dark")
        flat[".".join(path)] = {
            "css": css_name(path),
            "type": tok.get("$type"),
            "light": tok["$value"],
            "dark": dark if dark is not None else tok["$value"],
            **({"description": tok["$description"]} if "$description" in tok else {}),
            **({"name": tok["$extensions"]["name"]} if "name" in tok.get("$extensions", {}) else {}),
        }
    # The sequential scales read as magnitude steps 1..7 (near zero -> most),
    # light to dark on a light surface and reversed on a dark one, so small
    # values always recede into the surface.
    for ramp in ("seq", "seq-alt"):
        for i, s in enumerate(SEQ_STEPS, 1):
            light = flat[f"color.viz.{ramp}.{s}"]["light"]
            dark = flat[f"color.viz.{ramp}.{SEQ_STEPS[-i]}"]["light"]
            flat[f"color.viz.{ramp}-step.{i}"] = {
                "css": f"--viz-{ramp}-step-{i}", "type": "color", "light": light, "dark": dark,
                "description": f"Magnitude step {i} of 7; flips in dark mode"}
    return flat


def build_css(tokens, flat):
    def block(mode, only_moded=False):
        lines = []
        for key, t in flat.items():
            if key.startswith("type.base.") or key.startswith("type.ratio."):
                continue
            if only_moded and t["light"] == t["dark"]:
                continue
            lines.append(f"  {t['css']}: {css_value(t, t[mode])};")
        return "\n".join(lines)

    web = type_scale(tokens, "web")
    scale = "\n".join(f"  --t-{k}: {v};" for k, v in web.items())
    dark = block("dark", only_moded=True)
    media = []
    for m in MEDIA[1:]:
        s = type_scale(tokens, m)
        media.append(f'[data-medium="{m}"]{{\n' +
                     "\n".join(f"  --t-{k}: {v};" for k, v in s.items()) + "\n}")
    return f"""/* .describe( design tokens. GENERATED by tokens/build.py from
   tokens/tokens.json. Do not edit; edit the JSON and rebuild.

   Light is the default. Dark is a separate environment, not an inversion:
   it follows the OS unless the page pins [data-theme]. The type scale is
   the web scale; set data-medium="slides|social|report" on a root element
   to re-base it for that medium. */

:root{{
  color-scheme: light;
{block("light")}

  /* type scale, web (base {tokens["type"]["base"]["web"]["$value"]}) */
{scale}
}}

@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    color-scheme: dark;
{chr(10).join("  " + l for l in dark.splitlines())}
  }}
}}
:root[data-theme="dark"], [data-theme="dark"]{{
  color-scheme: dark;
{dark}
}}
[data-theme="light"]{{
  color-scheme: light;
{block("light", only_moded=True)}
}}

{chr(10).join(media)}
"""


def build_json(tokens, flat):
    return json.dumps({
        "$description": "GENERATED by tokens/build.py from tokens/tokens.json. Flat and resolved: "
                        "every token's light and dark value and its CSS custom property.",
        "tokens": flat,
        "type-scale": {m: type_scale(tokens, m) for m in MEDIA},
    }, indent=2, ensure_ascii=False) + "\n"


def build_md(tokens, flat):
    mode_surface = {"light": ("#F6F8FC", "#FFFFFF"), "dark": ("#050F2E", "#081A40")}

    def cr(hexv, mode, key=""):
        if key == "color.text.active-ink":  # measured on the fill it sits on
            on = flat["color.role.active"][mode]
            return f"{contrast(hexv, on):.2f} on active"
        g, p = mode_surface[mode]
        return f"{contrast(hexv, g):.2f} / {contrast(hexv, p):.2f}"

    out = ["# Token reference",
           "",
           "GENERATED by `tokens/build.py` from `tokens/tokens.json`; do not edit. How to use the",
           "tokens in each medium is in the README, under *Design tokens*.",
           "",
           "Contrast is WCAG, against ground / panel in that mode. Text needs 4.5, marks need 3.",
           ""]
    groups = [
        ("Brand primitives", "color.brand."),
        ("Surfaces", "color.surface."), ("Text", "color.text."), ("Lines", "color.line."),
        ("Roles", "color.role."), ("Data viz: story and context", ("color.viz.story", "color.viz.context")),
        ("Data viz: categorical (in this order)", "color.viz.cat."),
        ("Data viz: sequential, blue", "color.viz.seq."),
        ("Data viz: sequential, brass", "color.viz.seq-alt."),
        ("Data viz: diverging", "color.viz.div."),
    ]
    for title, pre in groups:
        out += [f"## {title}", "", "| Token | CSS | Light | Contrast | Dark | Contrast | Job |",
                "|---|---|---|---|---|---|---|"]
        for key, t in flat.items():
            ok = key in pre if isinstance(pre, tuple) else key.startswith(pre)
            if not ok or t["type"] != "color":
                continue
            job = t.get("name", "") + (" · " if t.get("name") and t.get("description") else "") + t.get("description", "")
            if key.startswith("color.brand."):  # primitives have no dark step
                dark = "same | " + cr(t["dark"], "dark", key)
            else:
                dark = f"`{t['dark']}` | " + cr(t["dark"], "dark", key)
            out.append(f"| `{key[6:]}` | `{t['css']}` | `{t['light']}` | {cr(t['light'], 'light', key)} "
                       f"| {dark} | {job} |")
        out.append("")
    out += ["## Type scale", "", "| Step | Ratio | " + " | ".join(MEDIA) + " |",
            "|---|---|" + "---|" * len(MEDIA)]
    scales = {m: type_scale(tokens, m) for m in MEDIA}
    for name, r in tokens["type"]["ratio"].items():
        if name.startswith("$"):
            continue
        out.append(f"| `--t-{name}` | {r['$value']:g} | " + " | ".join(scales[m][name] for m in MEDIA) + " |")
    out += ["", "## Everything else", "", "| Token | CSS | Value | Dark | Note |", "|---|---|---|---|---|"]
    for key, t in flat.items():
        if t["type"] == "color" or key.startswith(("type.ratio.", "type.base.")):
            continue
        lv = css_value(t, t["light"])
        dv = css_value(t, t["dark"]) if t["dark"] != t["light"] else ""
        out.append(f"| `{key}` | `{t['css']}` | `{lv}` | {f'`{dv}`' if dv else ''} | {t.get('description', '')} |")
    return "\n".join(out) + "\n"


def outputs():
    tokens = json.loads(SRC.read_text())
    flat = resolve(tokens)
    return {
        DIST / "tokens.css": build_css(tokens, flat),
        DIST / "tokens.json": build_json(tokens, flat),
        HERE / "TOKENS.md": build_md(tokens, flat),
    }


def main():
    check = "--check" in sys.argv
    stale = []
    for path, text in outputs().items():
        if check:
            if not path.exists() or path.read_text() != text:
                stale.append(path.relative_to(HERE.parent))
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(text)
            print("wrote", path.relative_to(HERE.parent))
    if stale:
        print("Out of date; run `python3 tokens/build.py` and commit:", *stale, sep="\n  ")
        sys.exit(1)
    if check:
        print("tokens/dist and TOKENS.md are up to date")


if __name__ == "__main__":
    main()
